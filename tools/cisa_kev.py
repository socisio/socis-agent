"""Exploitation intelligence: CISA KEV + FIRST EPSS — stdlib, no third-party server.

Why a native tool rather than an MCP server
-------------------------------------------
KEV is a single JSON document that CISA publishes at a stable URL with no
authentication, no API key and no rate limit. Roughly 1-2 MB, updated when
CISA adds entries. Wrapping that in an MCP server adds a dependency tree, a
process, and — in the case of the server suggested for this
(github.com/yeger00/kev-mcp) — three specific problems:

  * **No LICENSE file.** Absent an explicit grant the work is all rights
    reserved, so it cannot be packaged or redistributed. That is the fourth
    repository in this catalog's research to look adoptable and turn out not
    to be.
  * **1 star, 0 forks.** A personal side project, which is fine for its author
    and thin ground for something a customer's vulnerability triage depends on.
  * **Its documented deployment is a third-party host.** The README's
    "Production Deployment" points MCP clients at `https://amcipi.com/cisa-kev/`
    — an unknown personal domain. Every CVE you check would be visible to
    whoever runs it. In an MSSP that is client vulnerability posture leaving
    your control, which is not a trade worth making to avoid parsing a JSON
    file.

So this fetches the catalogue directly from CISA and caches it locally.

What KEV actually tells you
---------------------------
Presence in KEV is the strongest routine signal available that a vulnerability
is being exploited: CISA adds an entry only on evidence of active exploitation.
That makes it a better prioritisation input than CVSS alone — a 7.5 in KEV
outranks a 9.8 that nobody has ever exploited, because CVSS scores potential
and KEV records reality.

Two fields carry most of the weight:

  * ``knownRansomwareCampaignUse`` — "Known" means the CVE has appeared in
    ransomware activity. For most organisations that is the single most
    actionable field in the record.
  * ``dueDate`` — the remediation deadline binding on US federal civilian
    agencies under BOD 22-01. Not binding elsewhere, but it is CISA's own
    statement of urgency and a defensible benchmark to cite.

EPSS: the third leg
-------------------
FIRST.org's Exploit Prediction Scoring System gives a probability (0-1) that a
CVE will be exploited in the next 30 days, updated daily. Together the three
sources answer different questions, and confusing them is a common triage
error:

    CVSS  how bad COULD it be          severity of impact, if exploited
    KEV   is it being exploited NOW    confirmed observation, binary
    EPSS  how LIKELY is exploitation   prediction, probabilistic

A CVSS 9.8 with EPSS 0.02% and no KEV entry is theoretically severe and
practically ignorable this week. A CVSS 6.5 in KEV with EPSS 90% is not. Most
vulnerability programmes still rank by CVSS alone, which is why they drown.

EPSS is likewise a free unauthenticated API (api.first.org), so this needs no
key and no server either.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

from tools.registry import registry

logger = logging.getLogger(__name__)

KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)

# CISA updates the catalogue on business days. Six hours keeps it current
# without re-downloading ~2 MB for every lookup in a triage session.
_CACHE_TTL = 6 * 3600

# FIRST.org EPSS. Free, unauthenticated, recomputed daily for every scored CVE.
# Queried per-CVE rather than cached wholesale: the full dataset is ~250k rows
# and changes every day, so a local copy would be both large and stale.
_EPSS_URL = "https://api.first.org/data/v1/epss"
_FETCH_TIMEOUT = 30
_MAX_RESULTS = 100

_CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$", re.I)


def _cache_path() -> Path:
    home = os.environ.get("SOCIS_AGENT_HOME")
    base = Path(home) if home else Path.home() / ".socis-agent"
    d = base / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d / "cisa-kev.json"


def _load(force: bool = False) -> tuple[Optional[dict], Optional[str]]:
    """Return (catalogue, error). Serves from cache when fresh."""
    cache = _cache_path()

    if not force and cache.is_file():
        age = time.time() - cache.stat().st_mtime
        if age < _CACHE_TTL:
            try:
                return json.loads(cache.read_text(encoding="utf-8")), None
            except (json.JSONDecodeError, OSError):
                pass  # fall through and re-fetch

    try:
        req = urllib.request.Request(
            KEV_URL, headers={"User-Agent": "socis-agent-kev/1.0"}
        )
        with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        cache.write_text(raw, encoding="utf-8")
        return data, None
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        # A stale cache beats no answer: KEV changes slowly, so yesterday's
        # copy is still overwhelmingly correct. Say how old it is rather than
        # presenting it as current.
        if cache.is_file():
            try:
                data = json.loads(cache.read_text(encoding="utf-8"))
                age_h = (time.time() - cache.stat().st_mtime) / 3600
                return data, f"stale cache ({age_h:.0f}h old) — fetch failed: {exc}"
            except (json.JSONDecodeError, OSError):
                pass
        return None, f"Could not fetch the KEV catalogue: {exc}"


def _fmt(v: dict[str, Any]) -> str:
    ransom = v.get("knownRansomwareCampaignUse", "Unknown")
    lines = [
        f"**{v.get('cveID')}** — {v.get('vulnerabilityName', 'n/a')}",
        f"  Vendor/Product : {v.get('vendorProject', '?')} / {v.get('product', '?')}",
        f"  Added to KEV   : {v.get('dateAdded', '?')}",
        f"  Federal due    : {v.get('dueDate', '?')}  (BOD 22-01; binding on US federal civilian agencies)",
        f"  Ransomware use : {ransom}",
    ]
    if v.get("cwes"):
        lines.append(f"  CWE            : {', '.join(v['cwes'])}")
    if v.get("requiredAction"):
        lines.append(f"  Required action: {v['requiredAction']}")
    if v.get("shortDescription"):
        lines.append(f"  Description    : {v['shortDescription']}")
    return "\n".join(lines)


def _handle_check(args: dict, **_kw) -> str:
    raw = (args.get("cve_id") or "").strip().upper()
    if not raw:
        return "❌ `cve_id` is required, e.g. CVE-2021-44228"
    if not _CVE_RE.match(raw):
        return f"❌ Not a CVE identifier: {raw!r}. Expected CVE-YYYY-NNNNN."

    data, warn = _load()
    if data is None:
        return f"❌ {warn}"

    for v in data.get("vulnerabilities", []):
        if (v.get("cveID") or "").upper() == raw:
            out = [f"✅ {raw} IS in the CISA KEV catalogue.", "", _fmt(v)]
            if (v.get("knownRansomwareCampaignUse") or "").lower() == "known":
                out += ["", "⚠ Used in known ransomware campaigns — treat as "
                            "urgent regardless of CVSS."]
            out += ["",
                    "KEV membership means CISA has evidence of ACTIVE EXPLOITATION. "
                    "That outranks a CVSS score: a 7.5 in KEV is more urgent than a "
                    "9.8 nobody has ever exploited, because CVSS scores potential "
                    "and KEV records what is actually happening."]
            if warn:
                out += ["", f"⚠ {warn}"]
            return "\n".join(out)

    n = len(data.get("vulnerabilities", []))
    out = [f"❌ {raw} is NOT in the CISA KEV catalogue "
           f"({n:,} entries, version {data.get('catalogVersion', '?')}).",
           "",
           "Absence is NOT evidence the vulnerability is unexploited. KEV records "
           "what CISA has confirmed and chosen to publish; exploitation can precede "
           "a KEV entry by weeks, and non-US-relevant activity may never appear. "
           "Use it to escalate, never to dismiss."]
    if warn:
        out += ["", f"⚠ {warn}"]
    return "\n".join(out)


def _handle_search(args: dict, **_kw) -> str:
    vendor = (args.get("vendor") or "").strip().lower()
    product = (args.get("product") or "").strip().lower()
    days = args.get("recent_days")
    ransomware_only = bool(args.get("ransomware_only"))

    if not any([vendor, product, days, ransomware_only]):
        return ("❌ Give at least one filter: vendor, product, recent_days, "
                "or ransomware_only.")

    data, warn = _load()
    if data is None:
        return f"❌ {warn}"

    vulns = data.get("vulnerabilities", [])
    hits = []
    for v in vulns:
        if vendor and vendor not in (v.get("vendorProject") or "").lower():
            continue
        if product and product not in (v.get("product") or "").lower():
            continue
        if ransomware_only and (v.get("knownRansomwareCampaignUse") or "").lower() != "known":
            continue
        if days:
            added = v.get("dateAdded") or ""
            try:
                t = time.mktime(time.strptime(added, "%Y-%m-%d"))
                if (time.time() - t) > int(days) * 86400:
                    continue
            except (ValueError, TypeError):
                continue
        hits.append(v)

    # Newest first — a reader scanning a KEV list wants the latest additions.
    hits.sort(key=lambda v: v.get("dateAdded") or "", reverse=True)

    if not hits:
        return (f"No KEV entries matched (catalogue has {len(vulns):,} entries, "
                f"version {data.get('catalogVersion', '?')}).\n\n"
                "Remember KEV only lists CONFIRMED exploited vulnerabilities — a "
                "vendor absent here may still have serious unexploited CVEs.")

    head = [f"# CISA KEV matches: {len(hits)} of {len(vulns):,} entries",
            f"Catalogue version {data.get('catalogVersion', '?')}, "
            f"released {data.get('dateReleased', '?')}", ""]
    body = [_fmt(v) for v in hits[:_MAX_RESULTS]]
    tail = []
    if len(hits) > _MAX_RESULTS:
        tail.append(f"\n… {len(hits) - _MAX_RESULTS} more not shown.")
    if warn:
        tail.append(f"\n⚠ {warn}")
    return "\n".join(head) + "\n\n".join(body) + "\n".join(tail)



def _epss(cve_ids: list[str]) -> tuple[dict[str, dict], Optional[str]]:
    """Fetch EPSS scores. Returns ({cve: {score, percentile, date}}, error)."""
    if not cve_ids:
        return {}, None
    # The API accepts a comma-separated list, so one request covers a batch.
    # Keep batches modest: the URL is a GET and very long query strings get
    # rejected by intermediaries before FIRST ever sees them.
    out: dict[str, dict] = {}
    for i in range(0, len(cve_ids), 50):
        chunk = cve_ids[i:i + 50]
        url = f"{_EPSS_URL}?cve={','.join(chunk)}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "socis-agent-epss/1.0"})
            with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            return out, f"EPSS lookup failed: {exc}"
        for row in payload.get("data", []):
            cid = (row.get("cve") or "").upper()
            if cid:
                out[cid] = {
                    "score": row.get("epss"),
                    "percentile": row.get("percentile"),
                    "date": row.get("date"),
                }
    return out, None


def _fmt_epss(e: dict) -> list[str]:
    """Render one EPSS record, with the interpretation an analyst needs.

    A bare probability invites misreading. 0.94 does NOT mean "94% of hosts
    will be attacked" — it means FIRST's model puts a 94% chance on ANY
    exploitation being observed in the wild in the next 30 days. And the
    percentile matters more than the raw figure for ranking: most CVEs score
    below 0.01, so 0.15 is unremarkable in isolation and alarming at the 97th
    percentile.
    """
    try:
        score = float(e.get("score") or 0)
        pct = float(e.get("percentile") or 0)
    except (TypeError, ValueError):
        return ["  EPSS           : unparseable"]

    if score >= 0.5:
        band = "VERY HIGH — exploitation expected"
    elif score >= 0.1:
        band = "HIGH — exploitation plausible within 30 days"
    elif score >= 0.01:
        band = "MODERATE — above the bulk of CVEs"
    else:
        band = "LOW — in the long tail where most CVEs sit"

    return [
        f"  EPSS           : {score:.5f} ({score * 100:.2f}% chance of exploitation "
        f"in 30 days) — {band}",
        f"  EPSS percentile: {pct * 100:.1f}% — scores higher than {pct * 100:.1f}% "
        f"of all scored CVEs",
        f"  EPSS as of     : {e.get('date', '?')}",
    ]


def _handle_epss(args: dict, **_kw) -> str:
    raw = args.get("cve_ids") or args.get("cve_id") or ""
    # Unlike exploitation_triage, this one validates strictly: the caller named
    # specific CVEs, so a typo should be reported rather than quietly dropped.
    if isinstance(raw, str):
        ids = [x.strip().upper() for x in re.split(r"[,\s]+", raw) if x.strip()]
    else:
        ids = [str(x).strip().upper() for x in raw if str(x).strip()]
    if not ids:
        return "❌ `cve_ids` is required — one CVE or a list, e.g. CVE-2021-44228"

    bad = [c for c in ids if not _CVE_RE.match(c)]
    if bad:
        return f"❌ Not CVE identifiers: {', '.join(bad[:5])}. Expected CVE-YYYY-NNNNN."
    if len(ids) > 200:
        return f"❌ {len(ids)} CVEs is too many for one call; 200 is the limit."

    scores, err = _epss(ids)
    if err and not scores:
        return f"❌ {err}"

    # Rank by score. The whole point of EPSS is ordering a backlog.
    ranked = sorted(ids, key=lambda c: float(scores.get(c, {}).get("score") or 0),
                    reverse=True)

    out = [f"# EPSS exploitation probability — {len(ids)} CVE(s)", ""]
    for c in ranked:
        e = scores.get(c)
        if not e:
            out += [f"**{c}**", "  EPSS           : not scored (CVE may be too new, "
                                "rejected, or reserved)", ""]
            continue
        out += [f"**{c}**"] + _fmt_epss(e) + [""]

    out += [
        "EPSS predicts, it does not observe. A high score means exploitation is "
        "LIKELY; it is not evidence that anything has happened. Pair it with "
        "kev_check, which records confirmed exploitation — the combination is what "
        "ranks a backlog:",
        "",
        "    in KEV + high EPSS   patch now; exploited and expected to continue",
        "    in KEV + low EPSS    patch now anyway; KEV is observation, EPSS is a guess",
        "    not KEV + high EPSS  patch soon; likely to be exploited before you hear",
        "    not KEV + low EPSS   schedule normally",
    ]
    if err:
        out += ["", f"⚠ {err} (partial results shown)"]
    return "\n".join(out)


def _handle_triage(args: dict, **_kw) -> str:
    """Rank a list of CVEs by KEV membership and EPSS.

    This exists because the two signals are only useful together, and asking an
    analyst to run two tools and merge the output by hand is where prioritisation
    actually breaks down. The ordering below is deliberate: KEV outranks EPSS
    because it is observation rather than prediction.
    """
    raw = args.get("cve_ids") or ""
    # Extract CVE IDs by pattern rather than by splitting on whitespace.
    #
    # Splitting first and pattern-matching only as a fallback looks equivalent
    # and is not: pasted scanner output splits into words, every word becomes a
    # candidate, and the table fills with rows called TRIVY, NOISE and LINE.
    # Matching the pattern directly means arbitrary surrounding text is simply
    # ignored, which is the behaviour the tool advertises.
    text = raw if isinstance(raw, str) else " ".join(str(x) for x in raw)
    ids = [m.upper() for m in re.findall(r"CVE-\d{4}-\d{4,}", text, re.I)]
    if not ids:
        return ("❌ `cve_ids` is required. Accepts a list, a comma/space-separated "
                "string, or raw scanner output containing CVE IDs.")
    ids = list(dict.fromkeys(ids))          # de-dupe, keep order
    if len(ids) > 200:
        return f"❌ {len(ids)} CVEs is too many for one call; 200 is the limit."

    kev, kev_warn = _load()
    kev_map = {}
    if kev:
        for v in kev.get("vulnerabilities", []):
            cid = (v.get("cveID") or "").upper()
            if cid in set(ids):
                kev_map[cid] = v

    scores, epss_warn = _epss(ids)

    rows = []
    for c in ids:
        k = kev_map.get(c)
        e = scores.get(c) or {}
        try:
            sc = float(e.get("score") or 0)
        except (TypeError, ValueError):
            sc = 0.0
        ransom = (k or {}).get("knownRansomwareCampaignUse", "").lower() == "known"
        # Rank: ransomware-in-KEV, then KEV, then EPSS descending.
        rank = (0 if ransom else 1 if k else 2, -sc)
        rows.append((rank, c, k, e, sc, ransom))
    rows.sort(key=lambda r: r[0])

    out = [f"# Exploitation triage — {len(ids)} CVE(s)",
           "",
           "Ranked by confirmed exploitation first, predicted exploitation second.",
           "",
           f"| CVE | KEV | Ransomware | EPSS | Percentile | Action |",
           f"|---|---|---|---|---|---|"]
    for _, c, k, e, sc, ransom in rows:
        pct = ""
        try:
            pct = f"{float(e.get('percentile') or 0) * 100:.0f}%"
        except (TypeError, ValueError):
            pct = "—"
        epss_s = f"{sc:.4f}" if e else "—"
        if k and ransom:
            action = "**PATCH NOW** — exploited, ransomware"
        elif k:
            action = "**PATCH NOW** — confirmed exploited"
        elif sc >= 0.5:
            action = "Patch soon — exploitation expected"
        elif sc >= 0.1:
            action = "Prioritise — exploitation plausible"
        else:
            action = "Schedule normally"
        out.append(f"| {c} | {'YES' if k else 'no'} | {'YES' if ransom else 'no'} "
                   f"| {epss_s} | {pct} | {action} |")

    kev_n = sum(1 for r in rows if r[2])
    ransom_n = sum(1 for r in rows if r[5])
    out += ["",
            f"{kev_n} of {len(ids)} are in CISA KEV; {ransom_n} "
            f"{'is' if ransom_n == 1 else 'are'} associated with ransomware campaigns.",
            "",
            "Note what this does NOT tell you: whether the affected product is in "
            "your estate, whether it is reachable, and whether a compensating "
            "control already blocks the path. Exploitation likelihood ranks the "
            "backlog; it does not decide it."]
    for w in (kev_warn, epss_warn):
        if w:
            out += ["", f"⚠ {w}"]
    return "\n".join(out)

def _handle_status(args: dict, **_kw) -> str:
    data, warn = _load(force=bool(args.get("refresh")))
    if data is None:
        return f"❌ {warn}"
    vulns = data.get("vulnerabilities", [])
    ransom = sum(1 for v in vulns
                 if (v.get("knownRansomwareCampaignUse") or "").lower() == "known")
    cache = _cache_path()
    age_h = (time.time() - cache.stat().st_mtime) / 3600 if cache.is_file() else 0
    out = [f"CISA KEV catalogue version {data.get('catalogVersion', '?')}",
           f"  Released    : {data.get('dateReleased', '?')}",
           f"  Entries     : {len(vulns):,}",
           f"  Ransomware  : {ransom:,} flagged as used in known campaigns",
           f"  Local cache : {cache} ({age_h:.1f}h old, refreshed every "
           f"{_CACHE_TTL // 3600}h)"]
    if warn:
        out += ["", f"⚠ {warn}"]
    return "\n".join(out)


def _always() -> bool:
    """Stdlib only — nothing to gate on."""
    return True


registry.register(
    name="kev_check",
    toolset="cve-intel",
    schema={
        "name": "kev_check",
        "description": (
            "Check whether a CVE is in CISA's Known Exploited Vulnerabilities catalogue. "
            "KEV membership means CISA has evidence of ACTIVE exploitation, which is a "
            "stronger prioritisation signal than CVSS alone. Also reports ransomware "
            "association and the BOD 22-01 federal remediation deadline."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cve_id": {"type": "string", "description": "e.g. CVE-2021-44228"},
            },
            "required": ["cve_id"],
        },
    },
    handler=_handle_check,
    check_fn=_always,
    description="Check a CVE against CISA's Known Exploited Vulnerabilities.",
    emoji="🚨",
)

registry.register(
    name="kev_search",
    toolset="cve-intel",
    schema={
        "name": "kev_search",
        "description": (
            "Search the CISA KEV catalogue by vendor, product, recency, or ransomware "
            "association. Use to answer 'what actively-exploited vulnerabilities affect "
            "the products we run?' — the question that actually drives patch priority."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor": {"type": "string", "description": "Substring match, e.g. Fortinet, Microsoft, Cisco."},
                "product": {"type": "string", "description": "Substring match, e.g. FortiOS, Exchange."},
                "recent_days": {"type": "integer", "description": "Only entries added to KEV in this many days."},
                "ransomware_only": {"type": "boolean", "description": "Only CVEs flagged as used in known ransomware campaigns."},
            },
        },
    },
    handler=_handle_search,
    check_fn=_always,
    description="Search CISA KEV by vendor, product, recency or ransomware use.",
    emoji="🔍",
)

registry.register(
    name="epss_score",
    toolset="cve-intel",
    schema={
        "name": "epss_score",
        "description": (
            "Get FIRST.org EPSS exploitation-probability scores for one or more CVEs. "
            "EPSS predicts the likelihood of exploitation in the next 30 days (0-1, "
            "updated daily). This is a PREDICTION, distinct from CISA KEV which records "
            "CONFIRMED exploitation — use kev_check for that, or exploitation_triage to "
            "combine both."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cve_ids": {
                    "type": "string",
                    "description": "One CVE or several, comma- or space-separated. Max 200.",
                },
            },
            "required": ["cve_ids"],
        },
    },
    handler=_handle_epss,
    check_fn=_always,
    description="EPSS exploitation probability for one or more CVEs.",
    emoji="📈",
)

registry.register(
    name="exploitation_triage",
    toolset="cve-intel",
    schema={
        "name": "exploitation_triage",
        "description": (
            "Rank a list of CVEs by exploitation risk, combining CISA KEV (confirmed "
            "exploitation) with EPSS (predicted probability). Accepts a list, a "
            "comma-separated string, or raw scanner output containing CVE IDs. This is "
            "the tool to use when prioritising a patch backlog — KEV and EPSS answer "
            "different questions and are only useful together."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cve_ids": {
                    "type": "string",
                    "description": (
                        "CVE IDs — a list, comma/space-separated string, or pasted "
                        "scanner output. IDs are extracted from surrounding text. Max 200."
                    ),
                },
            },
            "required": ["cve_ids"],
        },
    },
    handler=_handle_triage,
    check_fn=_always,
    description="Rank CVEs by KEV membership and EPSS probability.",
    emoji="🎯",
)

registry.register(
    name="kev_status",
    toolset="cve-intel",
    schema={
        "name": "kev_status",
        "description": "Report the local KEV catalogue version, entry count and cache age.",
        "input_schema": {
            "type": "object",
            "properties": {
                "refresh": {"type": "boolean", "description": "Force a re-fetch from CISA."},
            },
        },
    },
    handler=_handle_status,
    check_fn=_always,
    description="KEV catalogue version and cache status.",
    emoji="📊",
)

__all__ = ["_handle_check", "_handle_search", "_handle_status",
           "_handle_epss", "_handle_triage", "KEV_URL", "_EPSS_URL"]
