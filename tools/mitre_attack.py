"""MITRE ATT&CK lookups and Navigator layer generation.

Why a data-backed toolset rather than model knowledge: technique IDs go into
CUSTOMER DELIVERABLES. `T1059.001` is PowerShell and `T1059.003` is Windows
Command Shell; a plausible-looking wrong ID lands in a report and a Navigator
layer, and neither the analyst nor the customer has an easy way to notice. The
`attack-mapping` skill already asks for "sub-techniques used only where
evidence supports them" — this is what makes that checkable instead of
aspirational.

Offline by design. The STIX bundle is fetched once and cached; every later
lookup is local. A cache that cannot be refreshed still answers, and says how
old it is rather than presenting itself as current — the same trade CISA KEV
makes in tools/cisa_kev.py, for the same reason.

Every output states the ATT&CK version it used, and generated layers stamp it
into the layer's own metadata. A deliverable that does not record which matrix
version produced it cannot be reproduced or defended a year later.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tools.registry import registry

# The official STIX distribution. attack-stix-data is MITRE's own repo and its
# `master` branch tracks the current release, which is what every customer
# here works against — no pinned older versions are needed.
ATTACK_URL = (
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/"
    "enterprise-attack/enterprise-attack.json"
)

# ~35 MB. Refresh weekly: ATT&CK ships roughly twice a year, so a 7-day TTL is
# generous and still catches a release within a week of it landing.
_CACHE_TTL = 7 * 24 * 3600
_FETCH_TIMEOUT = 120

# Navigator layer format. NOT the ATT&CK version — Navigator validates this
# separately and REFUSES TO LOAD a layer whose format it does not recognise, so
# a wrong value here produces a file that silently will not open in the
# customer's browser. Override with SOCIS_NAVIGATOR_LAYER_VERSION if the
# deployed Navigator expects a different one; verify by loading one generated
# layer before relying on it for a deliverable.
_LAYER_VERSION = os.environ.get("SOCIS_NAVIGATOR_LAYER_VERSION", "4.5")

_TECHNIQUE_RE = re.compile(r"^T\d{4}(?:\.\d{3})?$", re.I)

_TACTIC_ORDER = [
    "reconnaissance", "resource-development", "initial-access", "execution",
    "persistence", "privilege-escalation", "defense-evasion",
    "credential-access", "discovery", "lateral-movement", "collection",
    "command-and-control", "exfiltration", "impact",
]

_index_cache: Optional[Dict[str, Any]] = None


def _cache_path() -> Path:
    home = os.environ.get("SOCIS_AGENT_HOME")
    base = Path(home) if home else Path.home() / ".socis-agent"
    d = base / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d / "mitre-attack-enterprise.json"


def _fetch(force: bool = False) -> Tuple[Optional[dict], Optional[str]]:
    """Return (bundle, warning). Serves from cache when fresh."""
    cache = _cache_path()

    if not force and cache.is_file():
        age = time.time() - cache.stat().st_mtime
        if age < _CACHE_TTL:
            try:
                return json.loads(cache.read_text(encoding="utf-8")), None
            except (json.JSONDecodeError, OSError):
                pass  # corrupt cache — fall through and re-fetch

    try:
        req = urllib.request.Request(
            ATTACK_URL, headers={"User-Agent": "socis-agent-attack/1.0"}
        )
        with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        cache.write_text(raw, encoding="utf-8")
        return data, None
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        # An air-gapped install lives here permanently, and that is fine: the
        # matrix changes twice a year. Report the age so a deliverable can
        # record it, rather than implying the data is current.
        if cache.is_file():
            try:
                data = json.loads(cache.read_text(encoding="utf-8"))
                age_d = (time.time() - cache.stat().st_mtime) / 86400
                return data, (
                    f"offline — using cached ATT&CK data {age_d:.0f} day(s) old "
                    f"({exc})"
                )
            except (json.JSONDecodeError, OSError):
                pass
        return None, (
            f"No ATT&CK data available and the download failed: {exc}\n"
            "Install it with `bash scripts/install.sh --ensure mitre`, or place "
            f"the enterprise-attack STIX bundle at {cache}."
        )


def _build_index(force: bool = False) -> Tuple[Optional[dict], Optional[str]]:
    """Parse the STIX bundle into lookup tables, memoised per process."""
    global _index_cache
    if _index_cache is not None and not force:
        return _index_cache, _index_cache.get("_warning")

    bundle, warning = _fetch(force=force)
    if bundle is None:
        return None, warning

    by_id: Dict[str, dict] = {}
    by_tactic: Dict[str, List[dict]] = {}
    version = "unknown"

    for obj in bundle.get("objects", []):
        otype = obj.get("type")

        # The collection object carries the ATT&CK release version. Without it
        # a layer cannot honestly state what it was built against.
        if otype == "x-mitre-collection":
            version = obj.get("x_mitre_version") or version
            continue

        if otype != "attack-pattern":
            continue
        # Revoked and deprecated techniques must not reach a report: they are
        # real IDs that Navigator will render, and an analyst has no way to
        # tell from the ID alone that MITRE withdrew it.
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        ext = next(
            (r for r in obj.get("external_references", [])
             if r.get("source_name") == "mitre-attack"),
            None,
        )
        if not ext or not ext.get("external_id"):
            continue

        tid = ext["external_id"]
        entry = {
            "id": tid,
            "name": obj.get("name", ""),
            "description": (obj.get("description") or "").strip(),
            "url": ext.get("url", ""),
            "tactics": [p.get("phase_name") for p in obj.get("kill_chain_phases", [])
                        if p.get("kill_chain_name") == "mitre-attack"],
            "platforms": obj.get("x_mitre_platforms") or [],
            "is_subtechnique": bool(obj.get("x_mitre_is_subtechnique")),
            "detection": (obj.get("x_mitre_detection") or "").strip(),
            "data_sources": obj.get("x_mitre_data_sources") or [],
        }
        by_id[tid.upper()] = entry
        for tac in entry["tactics"]:
            by_tactic.setdefault(tac, []).append(entry)

    _index_cache = {
        "by_id": by_id,
        "by_tactic": by_tactic,
        "version": version,
        "count": len(by_id),
        "_warning": warning,
    }
    return _index_cache, warning


def _version_line(idx: dict, warning: Optional[str]) -> str:
    line = f"ATT&CK Enterprise v{idx['version']} · {idx['count']} techniques"
    if warning:
        line += f"\n⚠ {warning}"
    return line


def _fmt_technique(t: dict, *, full: bool = False) -> str:
    tactics = ", ".join(t["tactics"]) or "—"
    out = [f"**{t['id']} — {t['name']}**",
           f"  tactics: {tactics}"]
    if t["platforms"]:
        out.append(f"  platforms: {', '.join(t['platforms'])}")
    if t["url"]:
        out.append(f"  {t['url']}")
    if full:
        if t["description"]:
            out += ["", t["description"][:1200]]
        if t["data_sources"]:
            out += ["", f"data sources: {', '.join(t['data_sources'])}"]
        if t["detection"]:
            out += ["", "**Detection guidance (MITRE):**", t["detection"][:900]]
    return "\n".join(out)


# ── handlers ────────────────────────────────────────────────────────────────


def _handle_technique(args: dict, **_kw) -> str:
    tid = (args.get("technique_id") or "").strip().upper()
    if not tid:
        return "❌ `technique_id` is required (e.g. T1059.001)."
    if not _TECHNIQUE_RE.match(tid):
        return (f"❌ `{tid}` is not a technique ID. Expected Tnnnn or Tnnnn.nnn "
                "(e.g. T1059 or T1059.001). Use attack_search to find one by name.")

    idx, warning = _build_index()
    if idx is None:
        return f"❌ {warning}"

    entry = idx["by_id"].get(tid)
    if not entry:
        parent = tid.split(".")[0]
        hint = ""
        if "." in tid and parent in idx["by_id"]:
            subs = [k for k in idx["by_id"] if k.startswith(parent + ".")]
            hint = (f"\n\nParent {parent} exists ({idx['by_id'][parent]['name']}) "
                    f"with sub-techniques: {', '.join(sorted(subs))}")
        return (f"❌ {tid} is not a current Enterprise technique.\n"
                f"{_version_line(idx, warning)}\n"
                "It may be revoked, deprecated, or from another matrix "
                "(Mobile/ICS are separate). Revoked IDs are excluded here "
                "deliberately — Navigator will still render them, so an "
                f"analyst cannot tell from the ID alone.{hint}")

    return (_fmt_technique(entry, full=True) + "\n\n" + _version_line(idx, warning))


def _handle_search(args: dict, **_kw) -> str:
    query = (args.get("query") or "").strip()
    if not query:
        return "❌ `query` is required (technique name or keyword)."

    idx, warning = _build_index()
    if idx is None:
        return f"❌ {warning}"

    tactic = (args.get("tactic") or "").strip().lower()
    platform = (args.get("platform") or "").strip().lower()
    needle = query.lower()

    hits = []
    for t in idx["by_id"].values():
        if tactic and tactic not in [x.lower() for x in t["tactics"]]:
            continue
        if platform and platform not in [p.lower() for p in t["platforms"]]:
            continue
        name = t["name"].lower()
        if needle in name:
            hits.append((0, t))                      # name match ranks first
        elif needle in t["description"].lower():
            hits.append((1, t))
    hits.sort(key=lambda kv: (kv[0], kv[1]["id"]))

    if not hits:
        scope = "".join(
            [f", tactic={tactic}" if tactic else "",
             f", platform={platform}" if platform else ""]
        )
        return (f"No technique matches “{query}”{scope}.\n"
                f"{_version_line(idx, warning)}")

    limit = 15
    out = [f"{len(hits)} match(es) for “{query}”:", ""]
    for _, t in hits[:limit]:
        out.append(_fmt_technique(t))
        out.append("")
    if len(hits) > limit:
        out.append(f"…and {len(hits) - limit} more. Narrow with `tactic` or `platform`.")
    out.append(_version_line(idx, warning))
    return "\n".join(out)


def _handle_tactic(args: dict, **_kw) -> str:
    idx, warning = _build_index()
    if idx is None:
        return f"❌ {warning}"

    tactic = (args.get("tactic") or "").strip().lower().replace(" ", "-")
    if not tactic:
        return ("❌ `tactic` is required. Enterprise tactics, in kill-chain order:\n  "
                + "\n  ".join(_TACTIC_ORDER))
    if tactic not in idx["by_tactic"]:
        return (f"❌ `{tactic}` is not an Enterprise tactic. Valid values:\n  "
                + "\n  ".join(_TACTIC_ORDER))

    techniques = sorted(idx["by_tactic"][tactic], key=lambda t: t["id"])
    parents = [t for t in techniques if not t["is_subtechnique"]]
    out = [f"**{tactic}** — {len(parents)} techniques "
           f"({len(techniques) - len(parents)} sub-techniques)", ""]
    for t in parents:
        subs = [s for s in techniques
                if s["is_subtechnique"] and s["id"].startswith(t["id"] + ".")]
        out.append(f"  {t['id']}  {t['name']}"
                   + (f"  ({len(subs)} sub)" if subs else ""))
    out += ["", _version_line(idx, warning)]
    return "\n".join(out)


def _handle_layer(args: dict, **_kw) -> str:
    techniques = args.get("techniques")
    if isinstance(techniques, str):
        techniques = [t.strip() for t in techniques.replace(",", " ").split() if t.strip()]
    if not techniques:
        return ("❌ `techniques` is required — a list of technique IDs, or "
                "objects with {id, score, comment}.")

    idx, warning = _build_index()
    if idx is None:
        return f"❌ {warning}"

    name = (args.get("name") or "SOCIS coverage").strip()
    entries, unknown, unusable = [], [], []

    for item in techniques:
        if isinstance(item, str):
            tid, score, comment, colour = item.strip().upper(), None, "", ""
        elif isinstance(item, dict):
            # `techniqueID` is what Navigator itself calls this field in layer
            # JSON, so it is the first thing a caller reaches for — accept it
            # alongside the shorter forms rather than dropping the entry.
            tid = str(
                item.get("id")
                or item.get("technique_id")
                or item.get("techniqueID")
                or item.get("techniqueId")
                or ""
            ).strip().upper()
            score = item.get("score")
            comment = str(item.get("comment") or "")
            colour = str(item.get("color") or item.get("colour") or "")
        elif isinstance(item, (list, tuple)) and item:
            # [id, score] pairs — the shape that falls out of "T1059.001 and
            # T1053.005 with scores 100 and 40". Refusing it cost a round trip
            # for no reason; the intent is unambiguous.
            tid = str(item[0]).strip().upper()
            score = item[1] if len(item) > 1 else None
            comment = str(item[2]) if len(item) > 2 else ""
            colour = ""
        else:
            unusable.append(repr(item)[:60])
            continue
        if not tid:
            # An entry whose ID key we do not recognise USED TO be skipped
            # silently, and the layer was emitted anyway — a ✅ over
            # `"techniques": []`, which is the precise failure this tool
            # exists to prevent. Name the keys we got so the caller can fix
            # the call instead of guessing at the shape.
            unusable.append(
                "object with no recognised ID key (got: "
                + ", ".join(sorted(item.keys())) + ")"
                if isinstance(item, dict) else repr(item)[:60]
            )
            continue

        # Validate against the real matrix. A layer built from an unverified
        # ID renders in Navigator as a cell the customer believes is covered.
        if tid not in idx["by_id"]:
            unknown.append(tid)
            continue

        e: Dict[str, Any] = {"techniqueID": tid, "enabled": True}
        if score is not None:
            try:
                e["score"] = int(score)
            except (TypeError, ValueError):
                pass
        if comment:
            e["comment"] = comment
        if colour:
            e["color"] = colour
        entries.append(e)

    if unusable:
        return ("❌ Could not read a technique ID from "
                f"{len(unusable)} entr(y/ies), so the layer was NOT generated:\n"
                + "\n".join(f"    • {u}" for u in unusable)
                + "\n\nAccepted shapes:\n"
                + '    "T1059.001"                                  (plain ID)\n'
                + '    {"id": "T1059.001", "score": 100}            (with a score)\n'
                + '    {"techniqueID": "T1059.001", "score": 100}   (Navigator own key)\n'
                + '    ["T1059.001", 100]                           (id, score pair)\n')

    if unknown:
        return ("❌ These are not current Enterprise techniques, so the layer was "
                f"NOT generated: {', '.join(sorted(unknown))}\n\n"
                "A layer built from an unverified ID renders in Navigator as a "
                "cell the customer reads as covered. Check each with "
                "attack_technique or attack_search first.\n"
                f"{_version_line(idx, warning)}")

    if not entries:
        # Non-empty input that yields nothing is always an error. An empty
        # layer loads in Navigator and shows a blank matrix, which reads as
        # "no coverage" rather than "the call was wrong".
        return ("❌ No techniques resolved from the input, so the layer was NOT "
                "generated — an empty layer loads in Navigator and shows a "
                "blank matrix, which reads as 'no coverage' rather than 'the "
                "call was wrong'.\n"
                f"{_version_line(idx, warning)}")

    # versions.attack takes the MAJOR version only. The layer spec's own
    # example shows "attack": "18", and Navigator matches this against the
    # ATT&CK releases it can load — a full "19.2" matches nothing, so the
    # layer opens with no data behind it. The exact version still needs
    # recording for the deliverable, so it goes in layer metadata below.
    attack_major = str(idx["version"]).split(".")[0]

    # Sub-technique annotations are HIDDEN unless asked for: `showSubtechniques`
    # defaults to false per the spec, so a layer scoring only sub-techniques
    # (T1059.001, T1053.005 — the common case for detection coverage) loads
    # correctly and renders an apparently empty matrix. `expandedSubtechniques:
    # "annotated"` expands exactly the ones this layer annotates.
    layer = {
        "name": name,
        "versions": {
            "attack": attack_major,
            "navigator": "5.1.0",
            "layer": _LAYER_VERSION,
        },
        "domain": "enterprise-attack",
        "description": (args.get("description")
                        or f"Generated by SOCIS Agent against ATT&CK v{idx['version']}"),
        "layout": {"layout": "side", "expandedSubtechniques": "annotated"},
        "metadata": [
            {"name": "ATT&CK version", "value": str(idx["version"])},
            {"name": "Generated by", "value": "SOCIS Agent"},
        ],
        # list(entries): the parent-expansion below appends to
        # layer["techniques"], and sharing the object would inflate the
        # annotated count reported to the caller.
        "techniques": list(entries),
        "gradient": {
            "colors": ["#ff6666", "#ffe766", "#8ec843"],
            "minValue": 0,
            "maxValue": 100,
        },
        "legendItems": [],
        "showTacticRowBackground": False,
        "sorting": 0,
        "hideDisabled": False,
    }

    # Belt and braces for Navigators that predate layout.expandedSubtechniques:
    # mark each annotated sub-technique's PARENT with showSubtechniques so the
    # child cell is visible on load. Only add parents not already annotated.
    annotated = {e["techniqueID"] for e in entries}
    added_parents = 0
    parents_needed = {
        t.split(".")[0] for t in annotated if "." in t
    } - annotated
    for parent in sorted(parents_needed):
        if parent in idx["by_id"]:
            layer["techniques"].append(
                {"techniqueID": parent, "enabled": True, "showSubtechniques": True}
            )
            added_parents += 1

    body = json.dumps(layer, indent=2)
    parent_note = (f" (+{added_parents} parent row(s) marked to reveal the "
                   "annotated sub-techniques)" if added_parents else "")
    return (f"✅ Navigator layer “{name}” — {len(entries)} annotated "
            f"technique(s){parent_note}, ATT&CK v{idx['version']}, "
            f"layer format {_LAYER_VERSION}.\n\n"
            f"```json\n{body}\n```\n\n"
            "Save as .json and import via Navigator → Open Existing Layer. "
            "The ATT&CK version is stamped in `versions.attack` so the "
            "deliverable records what it was built against.\n"
            + (f"⚠ {warning}\n" if warning else ""))


def _handle_status(args: dict, **_kw) -> str:
    idx, warning = _build_index(force=bool(args.get("refresh")))
    cache = _cache_path()
    if idx is None:
        return f"❌ {warning}"
    age = ("never" if not cache.is_file()
           else f"{(time.time() - cache.stat().st_mtime) / 86400:.1f} days old")
    return "\n".join([
        f"ATT&CK Enterprise v{idx['version']}",
        f"  techniques (current, excluding revoked/deprecated): {idx['count']}",
        f"  cache: {cache}",
        f"  age: {age}",
        f"  Navigator layer format: {_LAYER_VERSION}",
        (f"\n⚠ {warning}" if warning else ""),
    ])


def _always() -> bool:
    """Stdlib only. Works offline once the bundle is cached."""
    return True


# ── registration ────────────────────────────────────────────────────────────

registry.register(
    name="attack_technique",
    toolset="mitre",
    schema={
        "name": "attack_technique",
        "description": (
            "Look up a MITRE ATT&CK Enterprise technique by ID, with its tactics, "
            "platforms, data sources and MITRE's own detection guidance. Verify every "
            "ID here before it reaches a report or a Navigator layer — T1059.001 "
            "(PowerShell) and T1059.003 (cmd) are one character apart. Revoked and "
            "deprecated techniques are reported as not current."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "technique_id": {"type": "string", "description": "e.g. T1059.001"},
            },
            "required": ["technique_id"],
        },
    },
    handler=_handle_technique,
    check_fn=_always,
    description="Look up an ATT&CK technique by ID.",
    emoji="🎯",
)

registry.register(
    name="attack_search",
    toolset="mitre",
    schema={
        "name": "attack_search",
        "description": (
            "Search ATT&CK Enterprise techniques by name or description. Use this to "
            "find the right technique for an observed behaviour instead of recalling "
            "an ID. Optionally scope by tactic or platform."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name or keyword, e.g. 'scheduled task'."},
                "tactic": {"type": "string", "description": "Optional tactic filter, e.g. persistence."},
                "platform": {"type": "string", "description": "Optional platform filter, e.g. Windows."},
            },
            "required": ["query"],
        },
    },
    handler=_handle_search,
    check_fn=_always,
    description="Search ATT&CK techniques by name or keyword.",
    emoji="🔎",
)

registry.register(
    name="attack_tactic",
    toolset="mitre",
    schema={
        "name": "attack_tactic",
        "description": (
            "List the techniques under one ATT&CK Enterprise tactic, parents with "
            "sub-technique counts. Use for coverage work — which techniques exist "
            "under a tactic is the denominator any honest coverage claim needs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tactic": {"type": "string", "description": "e.g. persistence, lateral-movement"},
            },
            "required": ["tactic"],
        },
    },
    handler=_handle_tactic,
    check_fn=_always,
    description="List techniques for an ATT&CK tactic.",
    emoji="📊",
)

registry.register(
    name="attack_navigator_layer",
    toolset="mitre",
    schema={
        "name": "attack_navigator_layer",
        "description": (
            "Generate a schema-valid ATT&CK Navigator layer JSON. EVERY technique ID "
            "is validated against the current matrix first and the layer is refused "
            "if any is unknown — an unverified ID renders as a cell the customer "
            "reads as covered. The ATT&CK version is stamped into versions.attack so "
            "the deliverable records what it was built against."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "techniques": {
                    "type": ["array", "string"],
                    "description": (
                        "Technique IDs as plain strings, objects "
                        "{id|techniqueID, score, comment, color}, or [id, score] "
                        "pairs. score drives the heatmap gradient (0-100)."
                    ),
                },
                "name": {"type": "string", "description": "Layer name shown in Navigator."},
                "description": {"type": "string", "description": "Layer description."},
            },
            "required": ["techniques"],
        },
    },
    handler=_handle_layer,
    check_fn=_always,
    description="Generate an ATT&CK Navigator layer.",
    emoji="🗺️",
)

registry.register(
    name="attack_status",
    toolset="mitre",
    schema={
        "name": "attack_status",
        "description": (
            "ATT&CK data version, technique count, cache location and age. Check this "
            "before citing coverage: an offline install serves cached data "
            "indefinitely, and a deliverable should record which version it used."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "refresh": {"type": "boolean", "description": "Force a re-download."},
            },
        },
    },
    handler=_handle_status,
    check_fn=_always,
    description="ATT&CK dataset version and cache status.",
    emoji="ℹ️",
)
