"""Typosquat and lookalike-domain discovery — stdlib only.

Why a native tool instead of an MCP server
------------------------------------------
The catalog entry this replaces (`domain-permutation`, wrapping
BurtTheCoder/mcp-dnstwist) is on hold for five separate reasons, and every one
of them is about the *packaging* rather than the technique:

  * `@modelcontextprotocol/sdk ^0.4.0` — pre-1.0, five protocol revisions old
  * that SDK carries GHSA-w48q-cv73-mx4w (HIGH, DNS rebinding) whose only fix
    crosses the 1.0 boundary, so `npm audit fix` cannot touch it
  * unmaintained since 2025-03
  * requires a running Docker daemon; it shells out to `elceef/dnstwist`
  * the least critical capability in the security set

None of that is inherent to domain permutation. The algorithms are published
and well documented — dnstwist's own fuzzer list is `addition, bitsquatting,
cyrillic, homoglyph, hyphenation, insertion, omission, plural, repetition,
replacement, subdomain, transposition, vowel-swap, dictionary` — and the work
is string manipulation plus DNS lookups. Both are stdlib.

So this module implements those techniques independently, from their published
descriptions, with **zero dependencies**: no MCP SDK, no Docker, no npm tree.
There is no advisory surface to audit because there is nothing to audit.

Credit where due: dnstwist (Marcin Ulikowski) is the reference implementation
of this idea and defined the fuzzer taxonomy used here. This is an independent
implementation of published techniques, not a port of its code.

What this does NOT do
---------------------
- **No IDN/Cyrillic homoglyphs.** dnstwist ships a researched Unicode
  homoglyph set constrained to what TLD authorities actually accept. Getting
  that wrong generates unregisterable domains and wastes lookups, so this
  sticks to ASCII confusables (rn/m, 0/o, 1/l) and says so rather than
  guessing at punycode.
- **No MX records.** `socket.getaddrinfo` resolves A/AAAA only; MX needs a real
  DNS library. A registered domain with MX is higher-risk than a parked one,
  so that distinction is unavailable here — noted in the output rather than
  silently absent.
- **No content similarity.** dnstwist compares pages with ssdeep and pHash.
  Out of scope; use the `web` toolset on any hit worth investigating.
"""

from __future__ import annotations

import concurrent.futures
import logging
import socket
import string
from typing import Iterable, Iterator

from tools.registry import registry

logger = logging.getLogger(__name__)

# DNS label rules. Filtering on these first is what keeps the lookup count
# sane: per haveibeensquatted's analysis, invalid candidates are a measurable
# fraction of raw fuzzer output, especially from insertion and homoglyph.
_LABEL_MAX = 63
_LABEL_CHARS = set(string.ascii_lowercase + string.digits + "-")

# QWERTY adjacency, used by `replacement` and `insertion`. These two model the
# most common real typing errors, which is why their hits matter more than
# vowel-swap or full-alphabet insertion: they attract accidental traffic.
_KEYBOARD = {
    "q": "12wa",     "w": "3qase",    "e": "4wsdr",   "r": "5edft",
    "t": "6rfgy",    "y": "7tghu",    "u": "8yhji",   "i": "9ujko",
    "o": "0iklp",    "p": "-ol",      "a": "qwsz",    "s": "weadzx",
    "d": "erfscx",   "f": "rtgdvc",   "g": "tyhfbv",  "h": "yujgnb",
    "j": "uikhmn",   "k": "iojlm",    "l": "opk",     "z": "asx",
    "x": "sdzc",     "c": "dfxv",     "v": "fgcb",    "b": "ghvn",
    "n": "hjbm",     "m": "jkn",
    "1": "2q",       "2": "13qw",     "3": "24we",    "4": "35er",
    "5": "46rt",     "6": "57ty",     "7": "68yu",    "8": "79ui",
    "9": "80io",     "0": "9op",
}

# ASCII confusables only — see the module docstring on why IDN is excluded.
_HOMOGLYPHS = {
    "a": ["4"],        "b": ["6", "lb"],   "c": ["("],
    "d": ["cl", "dl"], "e": ["3"],         "g": ["9", "q"],
    "i": ["1", "l", "!"], "l": ["1", "i"], "m": ["rn", "nn"],
    "n": ["m", "r"],   "o": ["0"],         "q": ["g", "9"],
    "s": ["5", "$"],   "t": ["7", "+"],    "u": ["v", "vv"],
    "v": ["u", "vv"],  "w": ["vv"],        "z": ["2"],
    "0": ["o"],        "1": ["l", "i"],    "5": ["s"],
}

_VOWELS = "aeiou"

# Words attackers append most often. Kept short deliberately: a long list
# multiplies lookups for little return, and the high-yield ones are the ones
# that make a domain look like official infrastructure.
_DICTIONARY = [
    "login", "secure", "account", "verify", "support", "mail", "portal",
    "auth", "sso", "vpn", "admin", "update", "billing", "pay", "online",
]

_COMMON_TLDS = [
    "com", "net", "org", "co", "io", "info", "biz", "online", "site",
    "xyz", "top", "app", "cloud", "shop", "live", "icu", "cn", "ru",
]

# Hard caps. A 12-character domain across every fuzzer runs to thousands of
# candidates; each unresolved one costs a DNS timeout. Bounding both keeps a
# single call from turning into a several-minute stall or a burst that looks
# like abuse to a resolver.
_MAX_CANDIDATES = 4000
_MAX_LOOKUPS = 1500
_DNS_WORKERS = 32
_DNS_TIMEOUT = 3.0


def _split(domain: str) -> tuple[str, str]:
    """Split into (name, tld). Handles multi-part TLDs like co.uk."""
    d = domain.strip().lower().rstrip(".")
    if d.startswith(("http://", "https://")):
        d = d.split("//", 1)[1]
    d = d.split("/", 1)[0].split(":", 1)[0]
    parts = d.split(".")
    if len(parts) < 2:
        return d, ""
    # Two-label public suffixes worth recognising; not exhaustive, and a
    # wrong guess only affects which part gets fuzzed, not correctness.
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net", "gov", "ac", "edu"} and len(parts[-1]) == 2:
        return ".".join(parts[:-2]), ".".join(parts[-2:])
    return ".".join(parts[:-1]), parts[-1]


def _valid(label: str) -> bool:
    if not label or len(label) > _LABEL_MAX:
        return False
    if label.startswith("-") or label.endswith("-"):
        return False
    if ".." in label:
        return False
    return all(c in _LABEL_CHARS or c == "." for c in label)


# ── Fuzzers ──────────────────────────────────────────────────────────────────
# Each yields (candidate_name, fuzzer_label). The label matters downstream:
# omission / transposition / replacement model genuine typing errors, so a
# registered hit from those is more likely to catch real user traffic than one
# from vowel-swap or full-alphabet addition.

def _omission(n: str) -> Iterator[tuple[str, str]]:
    for i in range(len(n)):
        yield n[:i] + n[i + 1:], "omission"


def _transposition(n: str) -> Iterator[tuple[str, str]]:
    for i in range(len(n) - 1):
        if n[i] != n[i + 1]:
            yield n[:i] + n[i + 1] + n[i] + n[i + 2:], "transposition"


def _repetition(n: str) -> Iterator[tuple[str, str]]:
    for i, c in enumerate(n):
        if c.isalnum():
            yield n[:i] + c + n[i:], "repetition"


def _replacement(n: str) -> Iterator[tuple[str, str]]:
    for i, c in enumerate(n):
        for k in _KEYBOARD.get(c, ""):
            yield n[:i] + k + n[i + 1:], "replacement"


def _insertion(n: str) -> Iterator[tuple[str, str]]:
    # Insert a key ADJACENT to the one at this position — models hitting two
    # keys at once. Restricting to neighbours rather than the full alphabet is
    # what keeps the output manageable: full-alphabet insertion is
    # (n+1) x 26 raw candidates for little extra yield.
    for i, c in enumerate(n):
        for k in _KEYBOARD.get(c, ""):
            yield n[:i] + k + n[i:], "insertion"


def _addition(n: str) -> Iterator[tuple[str, str]]:
    for c in string.ascii_lowercase + string.digits:
        yield n + c, "addition"


def _bitsquatting(n: str) -> Iterator[tuple[str, str]]:
    # A single bit flip in a cached DNS name — models hardware/memory error,
    # and attackers register the results deliberately.
    for i, c in enumerate(n):
        for mask in (1, 2, 4, 8, 16, 32, 64, 128):
            flipped = chr(ord(c) ^ mask)
            if flipped in _LABEL_CHARS and flipped != c:
                yield n[:i] + flipped + n[i + 1:], "bitsquatting"


def _homoglyph(n: str) -> Iterator[tuple[str, str]]:
    for i, c in enumerate(n):
        for g in _HOMOGLYPHS.get(c, []):
            yield n[:i] + g + n[i + 1:], "homoglyph"


def _hyphenation(n: str) -> Iterator[tuple[str, str]]:
    for i in range(1, len(n)):
        yield n[:i] + "-" + n[i:], "hyphenation"


def _subdomain(n: str) -> Iterator[tuple[str, str]]:
    for i in range(1, len(n)):
        if n[i - 1] not in "-." and n[i] not in "-.":
            yield n[:i] + "." + n[i:], "subdomain"


def _vowel_swap(n: str) -> Iterator[tuple[str, str]]:
    for i, c in enumerate(n):
        if c in _VOWELS:
            for v in _VOWELS:
                if v != c:
                    yield n[:i] + v + n[i + 1:], "vowel-swap"


def _plural(n: str) -> Iterator[tuple[str, str]]:
    if not n.endswith("s"):
        yield n + "s", "plural"


def _dictionary(n: str) -> Iterator[tuple[str, str]]:
    for w in _DICTIONARY:
        yield f"{n}-{w}", "dictionary"
        yield f"{w}-{n}", "dictionary"


_FUZZERS = {
    "omission": _omission,
    "transposition": _transposition,
    "repetition": _repetition,
    "replacement": _replacement,
    "insertion": _insertion,
    "addition": _addition,
    "bitsquatting": _bitsquatting,
    "homoglyph": _homoglyph,
    "hyphenation": _hyphenation,
    "subdomain": _subdomain,
    "vowel-swap": _vowel_swap,
    "plural": _plural,
    "dictionary": _dictionary,
}

# Ordered by how much accidental traffic a registered hit is likely to catch.
# Used to prioritise output, and to decide what to drop when capped.
_PRIORITY = {
    "omission": 0, "transposition": 1, "replacement": 2, "insertion": 3,
    "repetition": 4, "homoglyph": 5, "hyphenation": 6, "dictionary": 7,
    "bitsquatting": 8, "subdomain": 9, "plural": 10, "vowel-swap": 11,
    "addition": 12, "tld-swap": 13,
}


def _generate(name: str, tld: str, fuzzers: Iterable[str], tld_swap: bool) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    for f in fuzzers:
        fn = _FUZZERS.get(f)
        if not fn:
            continue
        for cand, label in fn(name):
            if not _valid(cand) or cand == name:
                continue
            full = f"{cand}.{tld}" if tld else cand
            # Keep the highest-priority attribution when two fuzzers collide.
            if full not in seen or _PRIORITY[label] < _PRIORITY[seen[full]]:
                seen[full] = label
    if tld_swap and tld:
        for t in _COMMON_TLDS:
            if t != tld:
                seen.setdefault(f"{name}.{t}", "tld-swap")
    out = [(d, f) for d, f in seen.items()]
    out.sort(key=lambda x: (_PRIORITY[x[1]], x[0]))
    return out[:_MAX_CANDIDATES]


def _resolve(domain: str) -> str | None:
    """Return an A/AAAA address, or None. socket only — no DNS library."""
    try:
        infos = socket.getaddrinfo(domain, None, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError, OSError):
        return None
    for fam, _, _, _, sockaddr in infos:
        if fam in (socket.AF_INET, socket.AF_INET6):
            return sockaddr[0]
    return None


# ── Handler ──────────────────────────────────────────────────────────────────

def _handle(args: dict, **_kw) -> str:
    raw = (args.get("domain") or "").strip()
    if not raw:
        return "❌ `domain` is required, e.g. example.com"

    name, tld = _split(raw)
    if not name:
        return f"❌ Could not parse a domain from {raw!r}"

    requested = args.get("fuzzers")
    if isinstance(requested, str):
        requested = [x.strip() for x in requested.split(",") if x.strip()]
    fuzzers = requested or list(_FUZZERS)
    unknown = [f for f in fuzzers if f not in _FUZZERS]
    if unknown:
        return (f"❌ Unknown fuzzer(s): {', '.join(unknown)}\n"
                f"   Available: {', '.join(sorted(_FUZZERS))}")

    tld_swap = bool(args.get("tld_swap", True))
    registered_only = bool(args.get("registered_only", True))

    candidates = _generate(name, tld, fuzzers, tld_swap)
    if not candidates:
        return f"⚠ No valid permutations generated for {raw}."

    if not args.get("resolve", True):
        lines = [f"# {len(candidates)} permutations of {name}.{tld} (no DNS lookups)"]
        lines += [f"  {d:<44} {f}" for d, f in candidates[:400]]
        if len(candidates) > 400:
            lines.append(f"  … {len(candidates) - 400} more")
        return "\n".join(lines)

    to_check = candidates[:_MAX_LOOKUPS]
    results: list[tuple[str, str, str | None]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=_DNS_WORKERS) as pool:
        futs = {pool.submit(_resolve, d): (d, f) for d, f in to_check}
        for fut in concurrent.futures.as_completed(futs):
            d, f = futs[fut]
            try:
                ip = fut.result()
            except Exception:
                ip = None
            results.append((d, f, ip))

    live = [r for r in results if r[2]]

    # Subdomain hits are a false-positive class and need separating.
    #
    # The `subdomain` fuzzer inserts a dot, so socis.io -> soc.is.io. That
    # resolving does NOT mean someone registered a lookalike — it means the
    # PARENT (is.io) exists, and if it has wildcard DNS then every possible
    # subdomain resolves. Reporting those alongside genuine registrations
    # invites exactly the wrong conclusion, and in testing the model ranked
    # them as the strongest candidates when they are the weakest.
    #
    # So resolve the parent for each subdomain hit and label accordingly.
    parents = {d.split(".", 1)[1] for d, f, _ in live if f == "subdomain"}
    parent_ips: dict[str, str | None] = {}
    if parents:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(_DNS_WORKERS, len(parents))) as pool:
            for parent, ip in zip(parents, pool.map(_resolve, parents)):
                parent_ips[parent] = ip
        # A random label under the parent: if THAT resolves, the parent has
        # wildcard DNS and every subdomain permutation is meaningless.
        wildcards = set()
        probes = {p: f"socis-wildcard-probe-zzq7.{p}" for p in parents}
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(_DNS_WORKERS, len(probes))) as pool:
            for parent, ip in zip(probes, pool.map(_resolve, probes.values())):
                if ip:
                    wildcards.add(parent)
    else:
        wildcards = set()

    live.sort(key=lambda r: (_PRIORITY[r[1]], r[0]))

    out = [
        f"# Lookalike domains for {name}.{tld}",
        f"# {len(candidates)} permutations generated, {len(to_check)} resolved, "
        f"{len(live)} registered",
        "",
    ]
    if not live:
        out.append("No permutations resolve. Nothing registered among those checked.")
    else:
        out.append(f"  {'domain':<40} {'resolves to':<18} technique")
        for d, f, ip in live:
            note = ""
            if f == "subdomain":
                parent = d.split(".", 1)[1]
                if parent in wildcards:
                    note = f"  ← WILDCARD on {parent}; not a registration"
                elif parent_ips.get(parent):
                    note = f"  ← subdomain of {parent}, which resolves"
            out.append(f"  {d:<40} {ip:<18} {f}{note}")

    if not registered_only:
        dead = [r for r in results if not r[2]][:200]
        if dead:
            out += ["", f"# {len(dead)} shown of "
                        f"{len([r for r in results if not r[2]])} unregistered"]
            out += [f"  {d:<44} {'—':<20} {f}" for d, f, _ in dead]

    # Cluster by resolved IP. This is the highest-value triage signal in the
    # output and it is invisible in a flat list: four lookalikes on one address
    # are not four actors. They are a parking service, a registrar holding
    # page, or — more interestingly — one holder who registered the set.
    #
    # In testing against socis.io, four domains sat on 76.223.54.146 and four
    # on 13.248.169.48 (both AWS/Route53 parking). Knowing that collapses
    # sixteen "candidates" into three things worth looking at.
    from collections import defaultdict
    by_ip: dict[str, list[str]] = defaultdict(list)
    for d, f, ip in live:
        if ip and f != "subdomain":
            by_ip[ip].append(d)
    clusters = {ip: ds for ip, ds in by_ip.items() if len(ds) > 1}
    if clusters:
        out += ["", "# Clustered by IP — shared hosting means shared ownership:"]
        for ip, ds in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
            out.append(f"    {ip:<18} {len(ds)} domains: {', '.join(sorted(ds))}")
        out += ["",
                "  A cluster is usually a parking service or registrar holding page "
                "rather than separate actors. Check one, and you have effectively "
                "checked all of them. A cluster NOT on a known parking range is the "
                "more interesting case: one party holding several of your lookalikes."]

    if len(candidates) > _MAX_LOOKUPS:
        out += ["", f"⚠ Capped at {_MAX_LOOKUPS} lookups of {len(candidates)} "
                    "candidates. Narrow with `fuzzers` — omission, transposition "
                    "and replacement model real typing errors and yield the "
                    "hits most likely to catch accidental traffic."]

    out += [
        "",
        "# These are CANDIDATES, not findings. Most registered lookalikes are",
        "# defensive registrations by the brand itself, parked domains, or",
        "# unrelated businesses with similar names. Before treating any hit as",
        "# hostile, check registration date, WHOIS, and what the site actually",
        "# serves — reporting a legitimate company as a phishing domain is its",
        "# own kind of incident.",
        "#",
        "# Ordered by technique: omission and transposition first, because a",
        "# registered domain there catches genuine typos. A vowel-swap or",
        "# full-alphabet addition hit is more often coincidence.",
        "#",
        "# IGNORE subdomain hits unless the parent is unexpected. socis.io ->",
        "# soc.is.io is a SUBDOMAIN of is.io, so it resolving says the parent",
        "# exists — not that anyone registered a lookalike. Any marked WILDCARD",
        "# are meaningless: that parent resolves every possible subdomain.",
        "#",
        "# LIMITATION: A/AAAA records only (stdlib socket resolution). A",
        "# registered variant with MX records or a live HTTP server is higher",
        "# risk than a parked one, and that distinction is not available here.",
        "# Check MX separately on anything worth pursuing.",
    ]
    return "\n".join(out)


def _always() -> bool:
    """Stdlib only — nothing to gate on."""
    return True


registry.register(
    name="domain_permutations",
    toolset="domain-intel",
    schema={
        "name": "domain_permutations",
        "description": (
            "Find typosquat and lookalike domains for a brand: generates permutations "
            "using the standard fuzzing techniques (omission, transposition, homoglyph, "
            "bitsquatting, keyboard adjacency, hyphenation, dictionary, TLD swap) and "
            "reports which ones actually resolve. No dependencies, no Docker, no API key. "
            "Resolves A/AAAA only — MX and page content are not checked."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Domain to protect, e.g. example.com"},
                "fuzzers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Techniques to use. Default: all. Narrow to omission, transposition "
                        "and replacement for the hits most likely to catch real typos. "
                        "Available: omission, transposition, repetition, replacement, "
                        "insertion, addition, bitsquatting, homoglyph, hyphenation, "
                        "subdomain, vowel-swap, plural, dictionary."
                    ),
                },
                "resolve": {"type": "boolean", "description": "Resolve DNS (default true). False returns bare permutations."},
                "registered_only": {"type": "boolean", "description": "Only show domains that resolve (default true)."},
                "tld_swap": {"type": "boolean", "description": "Also try the same name under common TLDs (default true)."},
            },
            "required": ["domain"],
        },
    },
    handler=_handle,
    check_fn=_always,
    description="Find registered typosquat and lookalike domains.",
    emoji="🎣",
)

__all__ = ["_handle", "_generate", "_split", "_valid"]
