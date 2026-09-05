#!/usr/bin/env python3
"""Set the SOCIS Agent version everywhere at once.

WHY THIS EXISTS
---------------
Tagging a release does NOT change the version baked into the artifacts.
electron-builder resolves `artifactName: "SOCIS-${version}-..."` from
apps/desktop/package.json, and Tauri reads src-tauri/Cargo.toml — neither
looks at the git tag. Tagging v0.1.1 while those files still said 0.0.1
produced installers named "SOCIS-0.0.1-..." for a v0.1.1 release.

Ten files carry a version string. Editing them by hand means one gets missed,
and the mismatch only shows up after a release is already published.

USAGE
-----
    python3 scripts/set-version.py 0.1.1     # write
    python3 scripts/set-version.py --check   # report drift, exit 1 if any

Run --check in CI to fail the build rather than ship a mislabelled installer.
"""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JSON_FILES = [
    "package.json",
    "apps/desktop/package.json",
    "apps/shared/package.json",
    "apps/bootstrap-installer/package.json",
    "apps/bootstrap-installer/src-tauri/tauri.conf.json",
    "ui-tui/package.json",
    "ui-tui/packages/socis-ink/package.json",
    "web/package.json",
    "website/package.json",
]

# (path, regex with one capture group for the version)
REGEX_FILES = [
    ("pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.M)),
    ("socis_cli/__init__.py", re.compile(r'^(__version__\s*=\s*")([^"]+)(")', re.M)),
    # Cargo.toml: anchor to the [package] block's first `version =` so a
    # dependency's version is never rewritten by mistake.
    ("apps/bootstrap-installer/src-tauri/Cargo.toml",
     re.compile(r'(\[package\](?:[^\[]*?)\nversion\s*=\s*")([^"]+)(")', re.S)),
]


def read_versions() -> "OrderedDict[str, str | None]":
    found: "OrderedDict[str, str | None]" = OrderedDict()
    for rel in JSON_FILES:
        p = ROOT / rel
        found[rel] = json.loads(p.read_text(encoding="utf-8")).get("version") if p.is_file() else None
    for rel, pat in REGEX_FILES:
        p = ROOT / rel
        if not p.is_file():
            found[rel] = None
            continue
        m = pat.search(p.read_text(encoding="utf-8"))
        found[rel] = m.group(2) if m else None
    return found


def write_version(version: str) -> int:
    changed = 0
    for rel in JSON_FILES:
        p = ROOT / rel
        if not p.is_file():
            print(f"  skip (missing) {rel}")
            continue
        d = json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
        if d.get("version") == version:
            continue
        old = d.get("version")
        d["version"] = version
        p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
        print(f"  {rel}: {old} -> {version}")
        changed += 1

    for rel, pat in REGEX_FILES:
        p = ROOT / rel
        if not p.is_file():
            print(f"  skip (missing) {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        m = pat.search(text)
        if not m:
            print(f"  WARN: no version match in {rel}")
            continue
        if m.group(2) == version:
            continue
        p.write_text(pat.sub(lambda mm: mm.group(1) + version + mm.group(3), text, count=1),
                     encoding="utf-8")
        print(f"  {rel}: {m.group(2)} -> {version}")
        changed += 1
    return changed


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if args[0] == "--check":
        found = read_versions()
        present = {v for v in found.values() if v is not None}
        for rel, v in found.items():
            print(f"  {rel:52} {v}")
        if len(present) == 1:
            print(f"\nOK — all files agree on {present.pop()}")
            return 0
        print(f"\nVERSION DRIFT: {sorted(present)}")
        print("Fix with: python3 scripts/set-version.py <version>")
        return 1

    version = args[0].lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+].+)?", version):
        print(f"Not a semver version: {version}")
        return 1
    print(f"Setting version to {version}")
    n = write_version(version)
    print(f"\n{n} file(s) updated" if n else "\nAlready up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
