"""YARA candidate-string extraction with a local goodware index.

Why this exists instead of wrapping yarGen
------------------------------------------
yarGen is the reference implementation of this idea and this module owes its
whole approach to it. It is also, per its own README, **not maintained** — the
author has moved to yarGen-Go — and wrapping it costs:

  * a 913 MB database download before the first useful run,
  * 3 GB of resident memory per invocation, 6 GB with ``--opcodes``,
  * no Python packaging at all (no setup.py, no pyproject.toml), so it can
    only be cloned, given a venv, and wrapped by hand.

Its README explains the memory figure:

    "yarGen pulls the whole goodstring database to memory ... I've already
     tried to migrate the database to sqlite but the numerous string
     comparisons and lookups made the analysis painfully slow."

That tradeoff is correct **for yarGen's workload**. It processes large sample
sets, so loading the corpus once and holding it amortises well. An analyst
triaging one sample has the opposite shape: a few thousand strings to check
once. There, querying an indexed database beats loading it — which is why the
conclusion flips rather than the reasoning being wrong.

The second difference matters more. yarGen ships a *generic* goodware corpus
built from software the author had in 2020. A SOC has a better one: the
software actually running in the environment being defended. A string present
on every one of a customer's endpoints is goodware **for that customer**,
whether or not it appears in a public database. So the index here is built
from paths the operator chooses — starting with the local system, and
extendable to a gold image or a mounted application share.

Design consequences
-------------------
- **Query, don't load.** Strings are looked up in batches against an indexed
  SQLite table. Resident memory stays proportional to one sample, not to the
  corpus.
- **Store hashes, not strings.** A truncated BLAKE2b digest is indexed rather
  than the string itself. The index is a fraction of the size, lookups are
  fixed-width, and a goodware index built from a customer's estate does not
  become a readable inventory of their software if it leaks.
- **Incremental.** Indexing a path adds to the corpus; it is never rebuilt
  from scratch.
- **No WAL.** This database is written by one process at a time, so it uses
  the default journal and avoids the WAL-reset corruption guard entirely
  (see socis_agent_state.py, sqlite.org/wal.html#walresetbug).
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Iterable, Iterator

from tools.registry import registry

logger = logging.getLogger(__name__)

# Below 8 characters almost everything is noise; yarGen defaults to the same.
_MIN_LEN = 8
# Above this, strings are usually embedded blobs, base64 or resource data.
_MAX_LEN = 128
# Cap what one call will return so a large sample cannot flood the context.
_MAX_RESULTS = 200
# Refuse files bigger than this — string extraction is linear, but a 4 GB disk
# image is not what this tool is for.
_MAX_FILE_MB = 64

_ASCII_RE = re.compile(rb"[\x20-\x7e]{%d,%d}" % (_MIN_LEN, _MAX_LEN))
# UTF-16LE as it appears in PE files: ASCII bytes interleaved with NULs.
_WIDE_RE = re.compile(rb"(?:[\x20-\x7e]\x00){%d,%d}" % (_MIN_LEN, _MAX_LEN))

# Substrings that mark a string as compiler, runtime or loader noise. These are
# present in a large share of benign binaries, so a rule built on them matches
# everything. yarGen learns this from its corpus; enumerating the worst
# offenders directly means a useful score even with an empty index.
_NOISE_MARKERS = (
    "kernel32", "ntdll", "msvcrt", "advapi32", "user32", "gdi32", "ole32",
    "oleaut32", "shell32", "shlwapi", "ws2_32", "wininet", "urlmon",
    "GetProcAddress", "LoadLibrary", "VirtualAlloc", "GetModuleHandle",
    "HeapAlloc", "RtlUnwind", "__cdecl", "__stdcall", "operator",
    "std::", "basic_string", "_CRT_", "_MSC_", "GetLastError",
    "Microsoft Visual C++", "mscoree", "System.Runtime", "libstdc++",
    "GLIBC_", "GCC: (", "__gmon_start__", ".text", ".rdata", ".rsrc",
    "This program cannot be run in DOS mode",
)

# Shapes that are distinctive enough to be worth surfacing even when short.
_INTERESTING = (
    (re.compile(r"^https?://", re.I), 25, "URL"),
    (re.compile(r"^[a-z0-9.-]+\.(com|net|org|ru|cn|xyz|top|info|biz)$", re.I), 25, "domain"),
    (re.compile(r"^/[a-z0-9_./-]{4,}\.(php|asp|aspx|jsp|cgi)$", re.I), 30, "C2 URI path"),
    (re.compile(r"^[A-Za-z0-9+/]{24,}={0,2}$"), 10, "base64-like"),
    # Backslash counts here are load-bearing and easy to get wrong.
    # A named pipe really does start with TWO backslashes (\\.\pipe\name),
    # so that pattern needs four in a raw string. A mutex or registry path has
    # ONE (Global\Name, SOFTWARE\Vendor), so those need two. Over-escaping
    # them makes the pattern require literal doubled backslashes, which real
    # samples do not contain — the rule silently stops matching.
    (re.compile(r"^\\\\\.\\pipe\\", re.I), 30, "named pipe"),
    (re.compile(r"^(Global|Local|Session)\\", re.I), 30, "mutex/event name"),
    (re.compile(r"(SOFTWARE|SYSTEM|HKEY_)\\", re.I), 15, "registry path"),
    (re.compile(r"^[A-Za-z0-9._-]+\.(exe|dll|bat|ps1|vbs|scr)$", re.I), 12, "filename"),
    (re.compile(r"Mozilla/[45]\.0"), 20, "user-agent"),
)


def _db_path() -> Path:
    home = os.environ.get("SOCIS_AGENT_HOME")
    base = Path(home) if home else Path.home() / ".socis-agent"
    d = base / "tools"
    d.mkdir(parents=True, exist_ok=True)
    return d / "goodware-strings.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()), timeout=30)
    # Default journal, deliberately: single-writer use, and this sidesteps the
    # WAL-reset corruption issue on unpatched SQLite builds altogether.
    conn.execute("PRAGMA synchronous=NORMAL")
    # Strings are attributed to the SOURCE PATH that contributed them, not
    # accumulated into one global counter.
    #
    # The obvious schema -- a single (hash, count) row incremented per sighting
    # -- is not idempotent: re-indexing a path adds its strings again, so a
    # string present in one file claims two after a second run. Because the
    # score treats "in more than 5 goodware files" as strong evidence, that
    # inflation silently suppresses real rule candidates, and nothing in the
    # output reveals it.
    #
    # Per-source rows make re-indexing a replace rather than an add, let a
    # source be forgotten outright (an MSSP that indexed a customer's estate
    # needs to be able to purge it when the engagement ends), and let staleness
    # be reported per path instead of guessed.
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sources (
               id       INTEGER PRIMARY KEY,
               path     TEXT UNIQUE NOT NULL,
               files    INTEGER NOT NULL,
               strings  INTEGER NOT NULL,
               indexed  TEXT NOT NULL
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS goodware (
               h         BLOB NOT NULL,   -- truncated blake2b of the string
               source_id INTEGER NOT NULL,
               n         INTEGER NOT NULL,-- files under THIS source containing it
               PRIMARY KEY (h, source_id)
           )"""
    )
    # Lookups are always "how many files across all sources", so index the hash.
    conn.execute("CREATE INDEX IF NOT EXISTS idx_goodware_h ON goodware(h)")
    return conn


def _h(s: str) -> bytes:
    """8-byte digest. Collisions are ~1 in 10^19 at these corpus sizes, and a
    collision costs one dropped candidate string, not a wrong verdict."""
    return hashlib.blake2b(s.encode("utf-8", "replace"), digest_size=8).digest()


def _extract(path: Path) -> set[str]:
    """ASCII and UTF-16LE strings from one file."""
    data = path.read_bytes()
    out: set[str] = set()
    for m in _ASCII_RE.finditer(data):
        out.add(m.group().decode("ascii", "ignore"))
    for m in _WIDE_RE.finditer(data):
        out.add(m.group().decode("utf-16-le", "ignore"))
    return out


# Magic bytes for the executable formats worth indexing. Checking content
# rather than extension is what makes this behave the same on every OS:
#
#   * On Linux and macOS, /usr/bin is full of EXTENSIONLESS binaries, so an
#     extension allowlist has to include "" to find anything.
#   * On Windows, "" then matches README, LICENSE, CHANGELOG and every other
#     extensionless text file, filling the goodware index with English prose.
#     Prose strings are exactly the sort of thing that looks like a good
#     candidate, so the index would start suppressing useful rule strings.
#
# Reading four bytes avoids having to guess per platform.
_MAGIC = (
    b"MZ",           # PE / DOS  (.exe .dll .sys .ocx .scr)
    b"\x7fELF",      # ELF       (Linux)
    b"\xcf\xfa\xed\xfe",  # Mach-O 64 LE
    b"\xce\xfa\xed\xfe",  # Mach-O 32 LE
    b"\xca\xfe\xba\xbe",  # Mach-O universal (fat)
)


def _is_binary(p: Path) -> bool:
    """True when *p* starts with a known executable magic number."""
    try:
        with p.open("rb") as fh:
            head = fh.read(4)
    except OSError:
        return False
    return any(head.startswith(m) for m in _MAGIC)


def _walk(root: Path, limit: int) -> Iterator[Path]:
    """Executable files under *root*, breadth-limited, identified by content."""
    seen = 0
    for p in root.rglob("*"):
        if seen >= limit:
            return
        try:
            if not p.is_file() or p.is_symlink():
                continue
            if p.stat().st_size > _MAX_FILE_MB * 1024 * 1024:
                continue
            if not _is_binary(p):
                continue
        except OSError:
            # Permission denied is routine when walking system directories;
            # skip and carry on rather than aborting the whole index.
            continue
        seen += 1
        yield p


def _score(s: str, goodware_count: int) -> tuple[int, str]:
    """Score a candidate. Higher is more likely to be worth keeping.

    The scoring answers one question: would the malware author have to change
    their code, or would a recompile defeat this string? Compiler and API
    noise loses to a recompile. Infrastructure and hardcoded names do not.
    """
    low = s.lower()

    # Present in goodware — the strongest signal available, and the whole
    # reason for the index. Scale by prevalence rather than excluding outright:
    # a string in 2 files may still be worth keeping if nothing better exists,
    # which is the behaviour yarGen adopted in 0.12.0.
    if goodware_count:
        return (-50 if goodware_count > 5 else -15,
                f"in goodware ({goodware_count} file(s))")

    for marker in _NOISE_MARKERS:
        if marker.lower() in low:
            return -30, f"compiler/API noise ({marker})"

    for rx, pts, why in _INTERESTING:
        if rx.search(s):
            return pts, why

    score, why = 0, "unclassified"
    # Long strings with mixed case and punctuation tend to be messages or
    # paths the author wrote; long uniform-case strings tend to be data.
    if len(s) >= 20:
        score += 5
        why = "long"
    if any(c.isupper() for c in s) and any(c.islower() for c in s):
        score += 3
    if re.search(r"[ .,:;!?'\"()\[\]{}=<>/\\-]", s):
        score += 3
        why = "punctuated — often author-written text"
    # Near-uniform character distribution suggests encoded data, not text.
    if len(set(s)) / max(len(s), 1) > 0.85 and len(s) > 16:
        score -= 8
        why = "high-entropy — likely encoded data"
    return score, why


def _lookup(conn: sqlite3.Connection, strings: Iterable[str]) -> dict[str, int]:
    """Batched goodware counts. This is the query-not-load decision in code."""
    by_hash = {_h(s): s for s in strings}
    found: dict[str, int] = {}
    hashes = list(by_hash)
    # 900 keeps us under SQLITE_MAX_VARIABLE_NUMBER on old builds (999).
    for i in range(0, len(hashes), 900):
        chunk = hashes[i:i + 900]
        q = ("SELECT h, SUM(n) FROM goodware WHERE h IN (%s) GROUP BY h"
             % ",".join("?" * len(chunk)))
        for h, n in conn.execute(q, chunk):
            found[by_hash[bytes(h)]] = n
    return found


# ── Handlers ─────────────────────────────────────────────────────────────────

def _handle_index(args: dict, **_kw) -> str:
    path = (args.get("path") or "").strip()
    limit = min(int(args.get("max_files") or 2000), 20000)
    if not path:
        return "❌ `path` is required — a directory of known-good binaries."
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        return f"❌ Not a directory: {root}"

    conn = _connect()
    try:
        prior = conn.execute(
            "SELECT id, files, indexed FROM sources WHERE path = ?",
            (str(root),)).fetchone()

        # Re-indexing REPLACES this source's contribution. Deleting first is
        # what makes the operation idempotent: run it ten times and the counts
        # are identical, so an operator refreshing after a patch cycle does not
        # inflate the corpus and start suppressing real candidates.
        if prior:
            conn.execute("DELETE FROM goodware WHERE source_id = ?", (prior[0],))
            conn.execute("DELETE FROM sources WHERE id = ?", (prior[0],))

        cur = conn.execute(
            "INSERT INTO sources(path, files, strings, indexed) "
            "VALUES(?,0,0,datetime('now'))", (str(root),))
        source_id = cur.lastrowid

        files = 0
        occurrences = 0
        for f in _walk(root, limit):
            try:
                strings = _extract(f)
            except OSError:
                continue
            files += 1
            occurrences += len(strings)
            conn.executemany(
                "INSERT INTO goodware(h, source_id, n) VALUES(?, ?, 1) "
                "ON CONFLICT(h, source_id) DO UPDATE SET n = n + 1",
                [(_h(x), source_id) for x in strings])

        distinct_here = conn.execute(
            "SELECT COUNT(*) FROM goodware WHERE source_id = ?",
            (source_id,)).fetchone()[0]
        conn.execute("UPDATE sources SET files = ?, strings = ? WHERE id = ?",
                     (files, distinct_here, source_id))
        conn.commit()
        total = conn.execute("SELECT COUNT(DISTINCT h) FROM goodware").fetchone()[0]
    finally:
        conn.close()

    if not files:
        return (f"⚠ No executables found under {root}.\n\n"
                "Files are identified by magic bytes (PE, ELF, Mach-O), not by "
                "extension, so extensionless Unix binaries are included and "
                "Windows text files like README are not. Point this at a system "
                "directory or an application install root.")

    verb = "Re-indexed" if prior else "Indexed"
    out = [f"✅ {verb} {files} file(s) from {root}",
           f"   {occurrences:,} string occurrences, {distinct_here:,} distinct here",
           f"   {total:,} distinct strings across the whole index"]
    if prior:
        out.append(f"   (replaced the previous run of {prior[1]} file(s) from {prior[2]})")
    out += ["",
            "Re-running this on the same path is safe — it replaces that path's "
            "contribution rather than adding to it. Refresh after a patch cycle: "
            "updated software ships new strings, and strings absent from the index "
            "look like malware candidates.",
            "",
            "The most valuable corpus is the software actually running in the "
            "environment you defend. A gold image or application share beats any "
            "generic database, because a string common on your estate is goodware "
            "for you whether or not it appears in a public corpus."]
    return "\n".join(out)


def _handle_forget(args: dict, **_kw) -> str:
    """Remove a source's contribution from the index."""
    path = (args.get("path") or "").strip()
    if not path:
        return "❌ `path` is required. Use yara_goodware_status to list sources."
    root = str(Path(path).expanduser().resolve())
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id, files FROM sources WHERE path = ?", (root,)).fetchone()
        if not row:
            return (f"❌ {root} is not an indexed source.\n"
                    "Run yara_goodware_status to see what is indexed.")
        conn.execute("DELETE FROM goodware WHERE source_id = ?", (row[0],))
        conn.execute("DELETE FROM sources WHERE id = ?", (row[0],))
        conn.commit()
        total = conn.execute("SELECT COUNT(DISTINCT h) FROM goodware").fetchone()[0]
    finally:
        conn.close()
    return (f"✅ Forgot {root} ({row[1]} file(s))\n"
            f"   {total:,} distinct strings remain in the index\n\n"
            "Strings shared with another indexed source are retained — only this "
            "source's attribution is removed.")


def _handle_extract(args: dict, **_kw) -> str:
    path = (args.get("path") or "").strip()
    if not path:
        return "❌ `path` is required — the sample to analyse."
    p = Path(path).expanduser()
    if not p.is_file():
        return f"❌ Not a file: {p}"
    try:
        size_mb = p.stat().st_size / 1024 / 1024
    except OSError as exc:
        return f"❌ Cannot stat {p}: {exc}"
    if size_mb > _MAX_FILE_MB:
        return f"❌ {p.name} is {size_mb:.0f} MB; limit is {_MAX_FILE_MB} MB."

    min_score = int(args.get("min_score") or 0)
    try:
        strings = _extract(p)
    except OSError as exc:
        return f"❌ Cannot read {p}: {exc}"
    if not strings:
        return (f"⚠ No printable strings ≥{_MIN_LEN} chars in {p.name}.\n\n"
                "That usually means the sample is packed or encrypted. Strings "
                "extracted from a packer belong to the packer, not the malware — "
                "unpack first, or write the rule against the packer deliberately "
                "and say so in the rule metadata.")

    conn = _connect()
    try:
        good = _lookup(conn, strings)
        corpus = conn.execute("SELECT COUNT(*) FROM goodware").fetchone()[0]
        indexed = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    finally:
        conn.close()

    scored = []
    for s in strings:
        sc, why = _score(s, good.get(s, 0))
        if sc >= min_score:
            scored.append((sc, s, why))
    scored.sort(key=lambda t: (-t[0], -len(t[1])))

    lines = [f"# Candidate strings — {p.name}",
             f"# {len(strings):,} extracted, {len(scored):,} above score {min_score}",
             f"# goodware index: {corpus:,} strings from {indexed} source path(s)",
             ""]
    if corpus == 0:
        lines += [
            "⚠ THE GOODWARE INDEX IS EMPTY, so nothing has been filtered.",
            "  Scores below come only from heuristics. Build the index first:",
            "    yara_goodware_index with path=/usr/bin  (or C:\\Windows\\System32)",
            "  Without it, expect compiler and API strings to survive.",
            "",
        ]
    for sc, s, why in scored[:_MAX_RESULTS]:
        lines.append(f"{sc:+4d}  {s!r:<60} # {why}")
    if len(scored) > _MAX_RESULTS:
        lines.append(f"\n# … {len(scored) - _MAX_RESULTS:,} more below the cut")

    lines += [
        "",
        "# These are CANDIDATES, not a rule. For each one ask: would the author",
        "# have to change their code, or would a recompile defeat it? Drop",
        "# anything a recompile defeats, then test the finished rule against a",
        "# goodware corpus with yara_scan — any hit there means it is not done.",
    ]
    return "\n".join(lines)


def _handle_status(args: dict, **_kw) -> str:
    conn = _connect()
    try:
        total = conn.execute("SELECT COUNT(DISTINCT h) FROM goodware").fetchone()[0]
        rows = conn.execute(
            "SELECT path, files, strings, indexed, "
            "       CAST(julianday('now') - julianday(indexed) AS INTEGER) "
            "FROM sources ORDER BY indexed DESC").fetchall()
    finally:
        conn.close()

    if not total:
        return ("Goodware index is empty — nothing will be filtered.\n\n"
                "Build it by indexing known-good binaries:\n"
                "  yara_goodware_index  path=/usr/bin\n"
                "  yara_goodware_index  path=/Applications           (macOS)\n"
                "  yara_goodware_index  path=C:\\\\Windows\\\\System32  (Windows)\n\n"
                "Better still, index a gold image or application share from the "
                "environment you defend — that corpus is more relevant than any "
                "generic database.")

    out = [f"Goodware index: {total:,} distinct strings",
           f"Database: {_db_path()}",
           "",
           f"{'files':>7}  {'strings':>9}  {'age':>6}  path"]
    stale = []
    for path, files, strings, indexed, age_days in rows:
        age = f"{age_days}d" if age_days is not None else "?"
        out.append(f"{files:>7}  {strings:>9,}  {age:>6}  {path}")
        if age_days is not None and age_days > 90:
            stale.append((path, age_days))

    if stale:
        out += ["", "⚠ STALE SOURCES — re-index these:"]
        for path, age in stale:
            out.append(f"    {path}  ({age} days old)")
        out += ["",
                "Software gets patched, and patched software ships new strings. A "
                "string absent from the index scores as a malware candidate, so a "
                "stale corpus produces noisier rules — the failure is silent and "
                "looks like the tool working.",
                "",
                "Re-indexing is idempotent: it replaces that path's contribution "
                "rather than adding to it, so it is safe to run on a schedule."]
    else:
        out += ["", "All sources indexed within 90 days.",
                "Re-index after a patch cycle — re-running is idempotent."]
    return "\n".join(out)


# ── Registration ─────────────────────────────────────────────────────────────

def _always() -> bool:
    """No external binary needed — this is pure stdlib."""
    return True


registry.register(
    name="yara_extract",
    toolset="yara",
    schema={
        "name": "yara_extract",
        "description": (
            "Extract and score candidate YARA strings from a sample, filtered against "
            "the local goodware index. Replaces yarGen for single-sample triage without "
            "its 913 MB database or 3-6 GB memory footprint. Build the index first with "
            "yara_goodware_index or nothing is filtered."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Sample file to analyse."},
                "min_score": {
                    "type": "integer",
                    "description": "Only return strings at or above this score. 0 shows everything scored; 10 shows likely keepers.",
                },
            },
            "required": ["path"],
        },
    },
    handler=_handle_extract,
    check_fn=_always,
    description="Extract and score candidate YARA strings from a sample.",
    emoji="⚗️",
)

registry.register(
    name="yara_goodware_index",
    toolset="yara",
    schema={
        "name": "yara_goodware_index",
        "description": (
            "Index a directory of known-good binaries into the local goodware string "
            "database, so yara_extract can filter them out. Incremental — index several "
            "paths. The best corpus is software from the environment you defend, not a "
            "generic database."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory of known-good binaries, e.g. /usr/bin or C:\\Windows\\System32."},
                "max_files": {"type": "integer", "description": "Cap files per run (default 2000)."},
            },
            "required": ["path"],
        },
    },
    handler=_handle_index,
    check_fn=_always,
    description="Index known-good binaries for string filtering.",
    emoji="📚",
)

registry.register(
    name="yara_goodware_forget",
    toolset="yara",
    schema={
        "name": "yara_goodware_forget",
        "description": (
            "Remove an indexed source's contribution from the goodware index. Use when "
            "a path is gone, was indexed by mistake, or when an engagement ends and a "
            "customer's software should no longer influence rule scoring."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "An indexed source path — see yara_goodware_status."},
            },
            "required": ["path"],
        },
    },
    handler=_handle_forget,
    check_fn=_always,
    description="Remove a source from the goodware index.",
    emoji="🗑️",
)

registry.register(
    name="yara_goodware_status",
    toolset="yara",
    schema={
        "name": "yara_goodware_status",
        "description": "Report the size of the goodware index and which paths built it.",
        "input_schema": {"type": "object", "properties": {}},
    },
    handler=_handle_status,
    check_fn=_always,
    description="Show goodware index size and sources.",
    emoji="📊",
)

__all__ = ["_handle_extract", "_handle_index", "_handle_status", "_handle_forget"]
