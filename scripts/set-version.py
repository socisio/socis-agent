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
    python3 scripts/set-version.py --tag     # tag + push the current version

Run --check in CI to fail the build rather than ship a mislabelled installer.

--tag refuses unless the tree is clean, the versions agree, and HEAD is pushed.
Those three conditions are what make a tag point at the code it claims to be:
a tag created on an unpushed or dirty tree builds something other than what
you tested, and re-using an existing tag silently rebuilds the OLD commit.
"""

from __future__ import annotations

import json
import re
import subprocess
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


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip())
    return r.stdout.strip()


def tag_release() -> int:
    """Create and push an annotated tag for the version already in the tree."""
    found = read_versions()
    present = {v for v in found.values() if v is not None}
    if len(present) != 1:
        print(f"Refusing to tag — version drift: {sorted(present)}")
        print("Fix with: python3 scripts/set-version.py <version>")
        return 1
    version = present.pop()
    tag = f"v{version}"

    if git("status", "--porcelain"):
        print("Refusing to tag — working tree is dirty.")
        print("Commit or stash first; a tag must point at committed code.")
        return 1

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    head = git("rev-parse", "HEAD")

    # An unpushed HEAD means the tag would reference a commit GitHub cannot
    # see, so the workflow would fail to check it out.
    try:
        remote_head = git("rev-parse", f"origin/{branch}")
    except RuntimeError:
        print(f"Refusing to tag — no origin/{branch}. Push the branch first.")
        return 1
    if remote_head != head:
        print(f"Refusing to tag — HEAD is not pushed to origin/{branch}.")
        print(f"  local : {head[:12]}\n  remote: {remote_head[:12]}")
        print("Run: git push")
        return 1

    # A LOCAL tag blocks `git tag` even when origin has none — deleting a tag
    # on GitHub leaves the local ref behind, and `git tag -d` is easy to skip.
    # Check it before the remote so the message names the right problem.
    local = git("tag", "--list", tag, check=False)
    if local:
        local_sha = git("rev-parse", f"{tag}^{{commit}}", check=False)
        print(f"Refusing to tag — {tag} already exists locally at {local_sha[:12]}.")
        if local_sha != head:
            print(f"  It does NOT point at HEAD ({head[:12]}).")
        print(f"Delete it first:\n  git tag -d {tag}")
        return 1

    # A tag that already exists points at whatever it pointed at when it was
    # created — re-using it rebuilds the OLD commit while looking current.
    existing = git("ls-remote", "--tags", "origin", f"refs/tags/{tag}", check=False)
    if existing:
        old = existing.split()[0]
        print(f"Refusing to tag — {tag} already exists on origin at {old[:12]}.")
        if old != head:
            print(f"  It does NOT point at HEAD ({head[:12]}); tagging would rebuild the old commit.")
        print(f"Delete it first:\n  git push origin --delete {tag}\n  git tag -d {tag}")
        return 1

    print(f"Tagging {tag} at {head[:12]} on {branch}")
    git("tag", "-a", tag, "-m", f"SOCIS Agent {tag}")
    git("push", "origin", tag)
    print(f"Pushed {tag} — the release workflow should now be running.")
    print("It publishes a DRAFT release; publish it once the artifacts attach.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if args[0] == "--tag":
        try:
            return tag_release()
        except RuntimeError as exc:
            print(f"git error: {exc}")
            return 1

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
