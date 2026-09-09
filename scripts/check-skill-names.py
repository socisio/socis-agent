#!/usr/bin/env python3
"""Reject skills whose frontmatter `name` collides or mismatches its directory.

Skill names are a FLAT namespace. `skills/<category>/<dir>/SKILL.md` is indexed
by the frontmatter ``name:``, not by path, so two skills declaring the same name
collide and one becomes permanently unreachable — it never enters the sync
manifest, `skill_view <dir>` reports "not a tracked bundled skill", and the
index shows one entry where there should be two.

Nothing raises. That is the whole problem.

`skills/security-operations/evidence-handling/` was created by copying
`detection-engineering/` and renaming the directory. Its frontmatter still said
``name: detection-engineering``, so:

  * it never appeared in .bundled_manifest
  * sync skipped it on every run
  * it was never loadable, for its entire existence
  * the index advertised its description against the other skill's content

The body turned out to be a verbatim copy too — 343 identical lines — so the
skill had never been written at all. But the *name* collision is what hid it,
and that is mechanically detectable. This check is the four lines that would
have caught it on the day it was committed.

Checks, over every `skills/*/*/SKILL.md`:

  1. frontmatter has a ``name:``
  2. ``name`` is unique across ALL categories
  3. ``name`` equals the directory name
  4. body is not byte-identical to another skill's (catches template copies
     that were renamed correctly but never filled in)

Exit 1 on any failure, naming the file and the fix.
"""

from __future__ import annotations

import hashlib
import sys
from collections import defaultdict
from pathlib import Path

SKILLS_GLOB = "skills/*/*/SKILL.md"


def frontmatter_field(text: str, field: str) -> str | None:
    """Value of *field* from the leading ``---`` block, or None.

    Scoped to the frontmatter deliberately: several skills embed example rules
    whose YAML contains ``name:`` or ``description:`` at column 0, and a naive
    whole-file grep picks those up. That is how a first pass at this check read
    a Sigma example's description as a skill's own.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return None


def body_digest(text: str) -> str:
    """Hash of everything after the frontmatter."""
    parts = text.split("---", 2)
    return hashlib.sha256(parts[-1].strip().encode("utf-8")).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    files = sorted(root.glob(SKILLS_GLOB))
    if not files:
        print(f"❌ No skills found under {SKILLS_GLOB} — wrong working directory?")
        return 1

    by_name: dict[str, list[Path]] = defaultdict(list)
    by_body: dict[str, list[Path]] = defaultdict(list)
    problems: list[str] = []

    for path in files:
        rel = path.relative_to(root)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            problems.append(f"{rel}: cannot read ({exc})")
            continue

        name = frontmatter_field(text, "name")
        directory = path.parent.name

        if not name:
            problems.append(
                f"{rel}: no `name:` in frontmatter — the skill cannot be indexed"
            )
            continue

        if name != directory:
            problems.append(
                f"{rel}: frontmatter says `name: {name}` but the directory is "
                f"`{directory}`.\n"
                f"      Indexing uses the NAME, so this skill is reachable only as "
                f"`{name}` — and if another skill owns that name, not at all.\n"
                f"      Fix: set `name: {directory}`."
            )

        by_name[name].append(rel)
        by_body[body_digest(text)].append(rel)

    for name, paths in sorted(by_name.items()):
        if len(paths) > 1:
            listed = "\n".join(f"        - {p}" for p in paths)
            problems.append(
                f"duplicate `name: {name}` declared by {len(paths)} skills:\n"
                f"{listed}\n"
                f"      Names are a flat namespace: one of these is unreachable and "
                f"will silently never load."
            )

    for _, paths in sorted(by_body.items(), key=lambda kv: str(kv[1][0])):
        if len(paths) > 1:
            listed = "\n".join(f"        - {p}" for p in paths)
            problems.append(
                f"{len(paths)} skills share an IDENTICAL body:\n"
                f"{listed}\n"
                f"      A template copy that was renamed but never written. Either "
                f"write it or delete it — a skill that misdescribes its own content "
                f"is worse than a missing one."
            )

    if problems:
        print(f"❌ {len(problems)} skill-naming problem(s) across {len(files)} skills:\n")
        for p in problems:
            print(f"  • {p}")
        print()
        return 1

    print(f"✓ {len(files)} skills: names unique, matching their directories, "
          f"no duplicate bodies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
