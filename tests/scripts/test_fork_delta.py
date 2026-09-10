"""The fork-delta classifier separates authored work from build output.

The raw number is worthless without this. A plain `diff -rq` between this fork
and a rebranded upstream reported 1597 "only in ours" files on 2026-09-10 —
which reads as an untrackable divergence. Of those, 769 were generated docs
pages (they carry an "auto-generated" marker and are produced by
website/scripts/generate-skill-docs.py) and 762 were a directory that exists
upstream too. The authored delta was ~52 files, which is tractable to replay
onto a fresh base.

Getting that wrong in either direction is costly: overcounting says "we can
never rebase" and undercounting says "rebase is free" when it would silently
drop real work.
"""

import ast
import pathlib

import pytest


def _load():
    """Load the pure classifier without running the clone/rebrand steps."""
    src = pathlib.Path("scripts/fork_delta.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    keep = [
        n for n in tree.body
        if isinstance(n, (ast.Import, ast.ImportFrom, ast.Assign))
        or (isinstance(n, ast.FunctionDef)
            and n.name in ("walk", "classify", "_is_noise", "_is_generated"))
    ]
    ns = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "<delta>", "exec"), ns)
    return ns


_ns = _load()
classify = _ns["classify"]
_is_noise = _ns["_is_noise"]
_is_generated = _ns["_is_generated"]


@pytest.fixture
def trees(tmp_path):
    fork, up = tmp_path / "fork", tmp_path / "up"

    def write(root, rel, body="x"):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    return fork, up, write


# ── the three buckets ──────────────────────────────────────────────────────

def test_authored_files_count_as_delta(trees):
    fork, up, write = trees
    write(fork, "tools/mitre_attack.py")
    write(fork, "skills/security-operations/alert-triage/SKILL.md")
    write(up, "agent/loop.py")
    r = classify(fork, up)
    assert r["delta_files"] == 2
    assert "tools/mitre_attack.py" in r["yours_only"]


def test_generated_docs_are_excluded(trees):
    """769 of 1597 were auto-generated docs pages. Counting them made the
    divergence look thirty times worse than it is."""
    fork, up, write = trees
    write(fork, "website/docs/user-guide/skills/bundled/a.md")
    write(fork, "website/static/api/skills-index.json")
    write(fork, "website/docs/reference/skills-catalog.md")
    r = classify(fork, up)
    assert r["delta_files"] == 0
    assert r["generated_count"] == 3


def test_build_output_and_os_cruft_are_excluded(trees):
    fork, up, write = trees
    for rel in ("apps/desktop/dist/bundle.js", "apps/desktop/build/x.js",
                "apps/desktop/release/y.dmg", "node_modules/pkg/i.js",
                "agent/__pycache__/loop.pyc", "agent/.DS_Store",
                ".venv/lib/x.py"):
        write(fork, rel)
    r = classify(fork, up)
    assert r["delta_files"] == 0, f"leaked: {r['yours_only']}"


def test_upstream_only_files_are_counted_separately(trees):
    """Post-fork additions. These are what a rebase GAINS, not what it must
    replay — client_lifecycle.py and models_detect.py are in this bucket."""
    fork, up, write = trees
    write(up, "agent/client_lifecycle.py")
    write(up, "socis_cli/models_detect.py")
    r = classify(fork, up)
    assert r["upstream_only_count"] == 2
    assert r["delta_files"] == 0


def test_files_present_in_both_are_compared_by_content(trees):
    fork, up, write = trees
    write(fork, "agent/same.py", "identical")
    write(up, "agent/same.py", "identical")
    write(fork, "agent/ours.py", "our version")
    write(up, "agent/ours.py", "their version")
    r = classify(fork, up)
    assert r["differing_count"] == 1
    assert r["differing"] == ["agent/ours.py"]


def test_same_size_different_content_is_still_detected(trees):
    """A size-only comparison would miss a one-character change — and a
    credential gate is a one-line change."""
    fork, up, write = trees
    write(fork, "agent/x.py", "aaaa")
    write(up, "agent/x.py", "aaab")
    assert classify(fork, up)["differing_count"] == 1


def test_generated_files_are_excluded_from_differing_too(trees):
    """A regenerated docs page differs on every build; reporting it as
    divergence would make the number noise."""
    fork, up, write = trees
    write(fork, "website/docs/user-guide/skills/bundled/a.md", "ours")
    write(up, "website/docs/user-guide/skills/bundled/a.md", "theirs")
    assert classify(fork, up)["differing_count"] == 0


# ── the area breakdown ─────────────────────────────────────────────────────

def test_the_delta_is_grouped_by_area(trees):
    """"52 files" is not actionable; "18 tests, 14 optional-mcps, 7 tools" is."""
    fork, up, write = trees
    write(fork, "tools/a.py")
    write(fork, "tools/b.py")
    write(fork, "tests/c.py")
    r = classify(fork, up)
    assert r["by_area"] == {"tools": 2, "tests": 1}


def test_a_root_level_file_is_reported_under_its_own_name(trees):
    fork, up, write = trees
    write(fork, "MAINTENANCE.md")
    assert "MAINTENANCE.md" in classify(fork, up)["by_area"]


# ── predicates ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("rel", [
    "agent/.DS_Store", "node_modules/a/b.js", "x/__pycache__/y.pyc",
    "apps/desktop/dist/a.js", ".venv/lib/x.py", "rebrand_report.json",
])
def test_noise_is_recognised(rel):
    assert _is_noise(rel)


@pytest.mark.parametrize("rel", [
    "tools/mitre_attack.py", "socis_cli/models.py",
    "optional-mcps/threat-intel/manifest.yaml",
])
def test_authored_paths_are_not_noise(rel):
    assert not _is_noise(rel)
    assert not _is_generated(rel)


def test_the_empty_case_is_zero_not_a_crash(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    r = classify(a, b)
    assert r["delta_files"] == 0 and r["differing_count"] == 0
