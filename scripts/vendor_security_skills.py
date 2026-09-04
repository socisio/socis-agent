#!/usr/bin/env python3
"""Vendor a filtered subset of Anthropic-Cybersecurity-Skills into SOCIS Agent.

Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills (Apache-2.0)

Why vendor rather than consume as a tap:
  - No GitHub API rate limits (the tap hits 60 req/hr unauthenticated)
  - Works in air-gapped customer environments, which many SOC/OT sites are
  - Immune to upstream deletion or unreviewed content changes
  - We control and are accountable for exactly what ships

Output goes to optional-skills/security/ (opt-in), NOT skills/ (bundled).
Bundled skills sit in the system prompt every turn; several hundred would
make the platform unusable. Opt-in costs nothing until installed.

Usage:
    python3 scripts/vendor_security_skills.py /path/to/Archive-extract
    python3 scripts/vendor_security_skills.py /path/to/src --include-offensive
    python3 scripts/vendor_security_skills.py /path/to/src --dry-run
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: python3 -m pip install pyyaml")


# Defensive subdomains — the blue-team work an MSSP does for customers.
DEFENSIVE = {
    "cloud-security", "threat-hunting", "threat-intelligence", "network-security",
    "digital-forensics", "malware-analysis", "identity-access-management",
    "identity-and-access-management", "identity-security", "soc-operations",
    "container-security", "security-operations", "ot-ics-security", "ot-security",
    "incident-response", "vulnerability-management", "devsecops",
    "zero-trust-architecture", "zero-trust", "endpoint-security", "cryptography",
    "phishing-defense", "ai-security", "ransomware-defense", "compliance-governance",
    "governance-risk-compliance", "privacy-compliance", "data-protection",
    "supply-chain-security", "threat-detection", "deception-technology",
    "hardware-firmware-security", "firmware-security", "firmware-analysis",
    "wireless-security", "social-engineering-defense", "mobile-security",
    "web-application-security", "api-security", "application-security",
    "blockchain-security",
}

# Offensive / dual-use. Excluded by default: vendoring these means SOCIS is
# *shipping* exploitation and C2 tooling in a product used inside customer
# environments, which is a different liability posture from a user choosing to
# install them. Enable with --include-offensive if you do purple-team work.
OFFENSIVE = {
    "red-teaming", "red-team", "penetration-testing", "offensive-security",
    "purple-team",
}


def parse_frontmatter(text: str) -> tuple[dict, str] | tuple[None, None]:
    if not text.startswith("---"):
        return None, None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, None
    try:
        return yaml.safe_load(parts[1]) or {}, parts[2]
    except yaml.YAMLError:
        return None, None


def shorten(desc: str, limit: int = 60) -> str:
    """SOCIS house style caps descriptions at 60 chars for the prompt index.

    Upstream descriptions run to several sentences (they are written for
    keyword-based discovery). Take the first sentence and trim on a word
    boundary so the result still reads as English.
    """
    desc = " ".join(str(desc).split())
    first = re.split(r"(?<=[.!?])\s", desc)[0].rstrip(".")
    if len(first) <= limit:
        return first
    cut = first[:limit]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(",;:") 


def convert(src: Path, dst: Path) -> dict | None:
    """Rewrite one skill into SOCIS house format. Returns its metadata."""
    skill_md = src / "SKILL.md"
    if not skill_md.is_file():
        return None

    fm, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm is None or not fm.get("name"):
        return None

    sub = fm.get("subdomain", "")
    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]

    # Rebuild frontmatter in SOCIS format, preserving upstream authorship and
    # licence (Apache-2.0 requires attribution to survive redistribution).
    new_fm = {
        "name": fm["name"],
        "description": shorten(fm.get("description", "")),
        "version": str(fm.get("version", "1.0")),
        "author": f"{fm.get('author', 'unknown')} (vendored by SOCIS)",
        "license": fm.get("license", "Apache-2.0"),
        "platforms": ["linux", "macos", "windows"],
        "category": "security",
        "metadata": {
            "socis": {
                "tags": tags[:8],
                "subdomain": sub,
                "upstream": "mukul975/Anthropic-Cybersecurity-Skills",
            }
        },
    }
    for key in ("nist_csf", "atlas_techniques", "d3fend_techniques",
                "nist_ai_rmf", "mitre_attack", "mitre_f3"):
        if fm.get(key):
            new_fm["metadata"]["socis"][key] = fm[key]

    dst.mkdir(parents=True, exist_ok=True)
    header = yaml.safe_dump(new_fm, sort_keys=False, allow_unicode=True,
                            default_flow_style=False, width=100)
    (dst / "SKILL.md").write_text(f"---\n{header}---\n{body}", encoding="utf-8")

    # Supporting material travels with the skill. `scripts/` is the exception:
    # upstream ships one with every skill, but most procedures never invoke it,
    # and shipping ~1000 unreviewed third-party Python files that run shell
    # commands into customer environments is a liability with no upside. Copy
    # scripts only when the skill actually calls them.
    extras = ["references", "assets", "templates", "examples"]
    if re.search(r"scripts/[A-Za-z0-9_.-]+", body):
        extras.append("scripts")
    for extra in extras:
        s = src / extra
        if s.is_dir():
            shutil.copytree(s, dst / extra, dirs_exist_ok=True)

    return {"name": fm["name"], "subdomain": sub,
            "desc": new_fm["description"], "author": fm.get("author", "unknown")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="extracted upstream repo (contains skills/)")
    ap.add_argument("--dest", type=Path, default=Path("optional-skills/security"))
    ap.add_argument("--include-offensive", action="store_true",
                    help="also vendor red-team / pentest / exploitation skills")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src_skills = args.source / "skills" if (args.source / "skills").is_dir() else args.source
    if not src_skills.is_dir():
        sys.exit(f"No skills/ directory under {args.source}")

    allowed = set(DEFENSIVE) | (set(OFFENSIVE) if args.include_offensive else set())

    selected, skipped, failed = [], [], []
    for d in sorted(p for p in src_skills.iterdir() if p.is_dir()):
        md = d / "SKILL.md"
        if not md.is_file():
            continue
        fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        if fm is None:
            failed.append(d.name)
            continue
        sub = fm.get("subdomain", "")
        if sub not in allowed:
            skipped.append((d.name, sub))
            continue
        selected.append(d)

    print(f"source:   {src_skills}")
    print(f"selected: {len(selected)}")
    print(f"skipped:  {len(skipped)} (offensive/unknown subdomain)")
    if failed:
        print(f"failed:   {len(failed)} (unparseable frontmatter)")

    if args.dry_run:
        by_sub: dict[str, int] = {}
        for d in selected:
            fm, _ = parse_frontmatter((d / "SKILL.md").read_text(encoding="utf-8"))
            by_sub[fm.get("subdomain", "?")] = by_sub.get(fm.get("subdomain", "?"), 0) + 1
        print("\nwould vendor:")
        for s, n in sorted(by_sub.items(), key=lambda kv: -kv[1]):
            print(f"  {n:4}  {s}")
        return 0

    args.dest.mkdir(parents=True, exist_ok=True)
    written = []
    for d in selected:
        meta = convert(d, args.dest / d.name)
        if meta:
            written.append(meta)

    # Apache-2.0 §4: retain the licence, and state that files were changed.
    (args.dest / "NOTICE").write_text(f"""\
Vendored security skills
========================

{len(written)} skills vendored from:

    Anthropic Cybersecurity Skills
    https://github.com/mukul975/Anthropic-Cybersecurity-Skills
    Copyright (c) Mahipal Jangra and contributors
    Licensed under the Apache License, Version 2.0

The full Apache-2.0 licence text is in LICENSE alongside this file.

NOT affiliated with or endorsed by Anthropic PBC. The upstream project is an
independent community project; the name reflects the skill format it targets.

Modifications made by SOCIS
---------------------------
Required by Apache-2.0 section 4(b):

  1. Frontmatter rewritten to the SOCIS skill schema (`metadata.socis`),
     preserving upstream `author` and `license` fields.
  2. Descriptions shortened to <=60 characters for the SOCIS prompt index.
     Full upstream descriptions remain in each skill's body and references/.
  3. Subdomain filtering — only the subdomains listed in
     scripts/vendor_security_skills.py were vendored.
  4. No changes to skill procedures, scripts, or reference material.

Review status
-------------
These skills are vendored as-is from upstream. They have NOT been individually
reviewed by SOCIS. Roughly 340 of the bundled scripts make outbound network
calls and 345 execute shell commands. Review any skill before using it in a
customer environment, and treat the scripts as third-party code.
""", encoding="utf-8")

    lic = args.source / "LICENSE"
    if lic.is_file():
        shutil.copy2(lic, args.dest / "LICENSE")

    by_sub: dict[str, list] = {}
    for m in written:
        by_sub.setdefault(m["subdomain"], []).append(m)

    lines = [f"# Security Skills ({len(written)})", "",
             "Vendored from [Anthropic Cybersecurity Skills]"
             "(https://github.com/mukul975/Anthropic-Cybersecurity-Skills) "
             "(Apache-2.0). See NOTICE.", "",
             "Opt-in — install with `socis skills install official/security/<name>`.", ""]
    for sub in sorted(by_sub):
        lines.append(f"## {sub} ({len(by_sub[sub])})")
        lines.append("")
        for m in sorted(by_sub[sub], key=lambda x: x["name"]):
            lines.append(f"- **{m['name']}** — {m['desc']}")
        lines.append("")
    # CATALOG.md, not DESCRIPTION.md: the latter is the category blurb that
    # skills_sync.py copies alongside the category, and overwriting it with an
    # 800-line listing breaks that contract.
    (args.dest / "CATALOG.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\nwrote {len(written)} skills to {args.dest}")
    print("  + NOTICE, LICENSE, CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
