#!/usr/bin/env python3
"""Measure how far this fork has diverged from a REBRANDED upstream.

WHY THIS EXISTS

The fork cannot merge ``upstream/main`` — that reverts the rebrand — so
MAINTENANCE.md §B prescribes cherry-picking individual commits. That worked
while the gap was small. On 2026-09-10 the gap was 1322 commits and every
security fix ported that day had to be REWRITTEN rather than cherry-picked,
because upstream had split modules after the fork date (``models_detect.py``,
``client_lifecycle.py``, ``approval_detection.py`` — none exist here).

That cost grows with the gap, so the question "when do we rebase" needs a
number, not a feeling. Getting that number by hand took twenty commands.

WHAT IT MEASURES

Clones upstream, runs the fork's own ``scripts/rebrand`` over it, and compares
the result with this tree. Three buckets:

  yours-only     files this fork has and rebranded-upstream does not, minus
                 generated output and build noise. THIS IS THE REAL DELTA —
                 the set a rebase would have to replay. Measured at ~52 files
                 on 2026-09-10, against 1597 before noise was excluded.
  upstream-only  post-fork additions we do not have.
  differing      present in both with different content: upstream's changes,
                 ours, or both.

It is also a CANARY on the rebrand script. If ``run_rebrand.py`` starts
failing against current upstream — a new module, a naming pattern the map does
not cover — the whole rebase strategy is blocked, and we want to know when
that happens rather than at rebase time.

READ-ONLY. Writes nothing but its own report.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

UPSTREAM = "https://github.com/NousResearch/hermes-agent.git"

# Paths whose contents are BUILD OUTPUT or environment, not authored code.
# website/docs skill pages carry an "auto-generated" marker and are produced by
# website/scripts/generate-skill-docs.py; counting them as divergence inflated
# the real figure roughly thirtyfold.
NOISE_PARTS = (
    ".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache",
    "venv", ".venv", "build", "dist", "release", ".next", "target",
    "rebrand_report.json",
)
NOISE_NAMES = (".DS_Store", "Thumbs.db", ".coverage")

# Generated trees: present in the fork, reproducible by a build step. Excluded
# from the delta but reported separately, because a rebase still has to
# regenerate them.
GENERATED_PREFIXES = (
    "website/docs/user-guide/skills/",
    "website/docs/reference/skills-catalog.md",
    "website/docs/reference/optional-skills-catalog.md",
    "website/static/api/",
)

# Trees this fork OWNS: authored work at paths upstream never populates.
#
# 762 original security skills (optional-skills/security/ — CMMC compliance,
# Cobalt Strike beacon analysis, AD ACL abuse, and hundreds more) plus the MCP
# manifests. Upstream has an optional-skills/ tree with the same category
# names, but nothing under security/, so these cannot conflict on a rebase:
# they replay by copying a directory.
#
# Counted separately from the shared-code delta because the two need different
# handling, and conflating them hid the useful number. The first report said
# "2563 files diverge", which reads as untrackable; the shared-code figure was
# ~66, which is a day of careful work.
FORK_OWNED_PREFIXES = (
    "optional-skills/security/",
    "optional-mcps/",
)


def _is_noise(rel: str) -> bool:
    parts = Path(rel).parts
    if any(p in NOISE_PARTS for p in parts):
        return True
    return Path(rel).name in NOISE_NAMES


def _is_generated(rel: str) -> bool:
    return any(rel.startswith(p) for p in GENERATED_PREFIXES)


def _is_fork_owned(rel: str) -> bool:
    """Authored, but at a path upstream never populates — replays by copy."""
    return any(rel.startswith(p) for p in FORK_OWNED_PREFIXES)


def walk(root: Path) -> set[str]:
    """Relative paths of every non-noise file under *root*."""
    out: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in NOISE_PARTS]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if not _is_noise(rel):
                out.add(rel)
    return out


def classify(fork: Path, rebranded: Path) -> dict:
    ours, theirs = walk(fork), walk(rebranded)

    yours_only_all = sorted(ours - theirs)
    upstream_only = sorted(theirs - ours)

    generated = [p for p in yours_only_all if _is_generated(p)]
    fork_owned = [p for p in yours_only_all
                  if not _is_generated(p) and _is_fork_owned(p)]
    # The delta that matters: authored files at paths upstream ALSO uses, so a
    # rebase has to reconcile them by hand.
    yours_only = [p for p in yours_only_all
                  if not _is_generated(p) and not _is_fork_owned(p)]

    differing = []
    for rel in sorted(ours & theirs):
        if _is_generated(rel):
            continue
        a, b = fork / rel, rebranded / rel
        try:
            if a.stat().st_size != b.stat().st_size or a.read_bytes() != b.read_bytes():
                differing.append(rel)
        except OSError:
            differing.append(rel)

    by_area: dict[str, int] = {}
    for p in yours_only:
        area = Path(p).parts[0] if len(Path(p).parts) > 1 else p
        by_area[area] = by_area.get(area, 0) + 1

    fork_owned_areas: dict[str, int] = {}
    for p in fork_owned:
        for prefix in FORK_OWNED_PREFIXES:
            if p.startswith(prefix):
                fork_owned_areas[prefix.rstrip("/")] = (
                    fork_owned_areas.get(prefix.rstrip("/"), 0) + 1
                )
                break

    return {
        "delta_files": len(yours_only),
        "yours_only": yours_only,
        "fork_owned_count": len(fork_owned),
        "fork_owned_areas": dict(sorted(fork_owned_areas.items(),
                                        key=lambda kv: -kv[1])),
        "upstream_only_count": len(upstream_only),
        "differing_count": len(differing),
        "differing": differing,
        "generated_count": len(generated),
        "by_area": dict(sorted(by_area.items(), key=lambda kv: -kv[1])),
    }


def rebrand_upstream(workdir: Path, rebrand_src: Path, ref: str) -> tuple[Path, str]:
    """Clone upstream at *ref*, apply the fork's rebrand, return (path, sha)."""
    clone = workdir / "upstream"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", "--branch", ref, UPSTREAM, str(clone)],
        check=True,
    )
    sha = subprocess.run(
        ["git", "-C", str(clone), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    shutil.copytree(rebrand_src, clone / "scripts" / "rebrand", dirs_exist_ok=True)
    # The rebrand script defaults to a dry run; both flags are required. Its
    # own post-flight checks (syntax, stale imports) run here — if they fail,
    # check=True surfaces it, which is the canary.
    subprocess.run(
        [sys.executable, "scripts/rebrand/run_rebrand.py",
         "--apply-text", "--apply-renames"],
        cwd=clone, check=True, capture_output=True, text=True,
    )
    return clone, sha


def render(result: dict, sha: str, behind: str) -> str:
    owned = result.get("fork_owned_count", 0)
    lines = [
        f"**{result['delta_files']}** files need merge judgement on a rebase. "
        f"**{owned}** more replay by copy.",
        "",
        f"- upstream at `{sha[:12]}`, this fork is **{behind}** commits behind",
        f"- {result['upstream_only_count']} files exist upstream and not here "
        "(post-fork additions — what a rebase GAINS)",
        f"- {result['differing_count']} files exist in both with different content",
        f"- {result['generated_count']} generated files excluded "
        "(docs pages, static API output — rebuilt, not replayed)",
        "",
        "### Needs merge judgement",
        "",
        "Authored files at paths upstream also uses. This is the only part of a "
        "rebase that needs reading and deciding.",
        "",
        "| area | files |",
        "|---|---|",
    ]
    for area, count in result["by_area"].items():
        lines.append(f"| `{area}` | {count} |")

    if result.get("fork_owned_areas"):
        lines += [
            "",
            "### Replays by copy",
            "",
            "Authored work at paths upstream never populates — it cannot "
            "conflict, so a rebase copies these trees across.",
            "",
            "| tree | files |",
            "|---|---|",
        ]
        for area, count in result["fork_owned_areas"].items():
            lines.append(f"| `{area}` | {count} |")

    lines += [
        "",
        "### Why this is measured",
        "",
        "The fork cannot merge `upstream/main` — that reverts the rebrand — so "
        "MAINTENANCE.md §B prescribes cherry-picking. That degrades as the gap "
        "grows: at 1322 commits behind, every security fix ported on 2026-09-10 "
        "had to be REWRITTEN rather than cherry-picked, because upstream had "
        "split modules that do not exist here (`models_detect.py`, "
        "`client_lifecycle.py`, `approval_detection.py`).",
        "",
        "Rebase-and-rebrand replays this delta onto a current base instead, so "
        "upstream's changes arrive as upstream wrote them. The two figures above "
        "are deliberately separate: conflating them produced a first report "
        "reading \"2563 files diverge\", which looks untrackable, when the "
        "figure needing actual judgement was around sixty.",
        "",
        "The rebrand script ran cleanly against this upstream commit, including "
        "its own syntax and stale-import post-flight checks. If that ever fails "
        "this job fails — the strategy depends on it.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", default=".", help="path to the fork checkout")
    ap.add_argument("--ref", default="main", help="upstream ref to compare against")
    ap.add_argument("--json", dest="json_out", help="write raw results here")
    ap.add_argument("--markdown", dest="md_out", help="write the report here")
    ap.add_argument("--max-delta", type=int, default=0,
                    help="exit 1 if the delta exceeds this (0 = never fail)")
    args = ap.parse_args()

    fork = Path(args.fork).resolve()
    rebrand_src = fork / "scripts" / "rebrand"
    if not (rebrand_src / "run_rebrand.py").is_file():
        print(f"error: no rebrand script at {rebrand_src}", file=sys.stderr)
        return 2

    behind = "?"
    try:
        subprocess.run(["git", "-C", str(fork), "fetch", "--quiet",
                        "--filter=blob:none", "upstream", args.ref], check=False)
        behind = subprocess.run(
            ["git", "-C", str(fork), "rev-list", "--count",
             f"HEAD..upstream/{args.ref}"],
            capture_output=True, text=True, check=False,
        ).stdout.strip() or "?"
    except Exception:
        pass

    with tempfile.TemporaryDirectory(prefix="fork-delta-") as tmp:
        clone, sha = rebrand_upstream(Path(tmp), rebrand_src, args.ref)
        result = classify(fork, clone)

    result["upstream_sha"] = sha
    result["commits_behind"] = behind

    report = render(result, sha, behind)
    print(report)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.md_out:
        Path(args.md_out).write_text(report + "\n", encoding="utf-8")

    if args.max_delta and result["delta_files"] > args.max_delta:
        print(f"\nerror: delta {result['delta_files']} exceeds "
              f"--max-delta {args.max_delta}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
