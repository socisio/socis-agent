"""The `skill not found` list must be relevant and must admit it is partial.

`skill_view` returned the first 20 skills ALPHABETICALLY under a key called
`available_skills`. Asking for a sigma skill therefore got apple-notes, findmy
and p5js — everything from the categories sorting before "email" — and the
caller concluded the skill did not exist. It did: `detection-engineering` was
installed the whole time, just past the cut. Nothing raised, and the reply read
as authoritative.
"""

import json
import re

import pytest

ALL_SKILLS = [
    {"name": "apple-notes", "description": "Apple Notes"},
    {"name": "architecture-diagram", "description": "diagrams"},
    {"name": "alert-triage", "description": "Triage a SIEM alert"},
    {"name": "detection-engineering",
     "description": "Author and convert Sigma rules to SIEM queries"},
    {"name": "yara-authoring", "description": "Author YARA rules with yarGen"},
    {"name": "ioc-enrichment", "description": "Enrich indicators"},
]


def _rank(name, all_skills, limit=20):
    """Mirror of the ranking in tools/skills_tool.py."""
    wanted = {t for t in re.split(r"[^a-z0-9]+", name.lower()) if t}

    def relevance(entry):
        hay = f"{entry.get('name', '')} {entry.get('description', '')}".lower()
        return (-sum(1 for t in wanted if t and t in hay), entry.get("name", ""))

    return [s["name"] for s in sorted(all_skills, key=relevance)[:limit]]


@pytest.mark.parametrize(
    "query,expected_first",
    [
        ("sigma_convert", "detection-engineering"),
        ("yargen_generate", "yara-authoring"),
        ("yara", "yara-authoring"),
    ],
)
def test_closest_skill_ranks_first(query, expected_first):
    assert _rank(query, ALL_SKILLS)[0] == expected_first


def test_an_unrelated_query_still_returns_something():
    """No match must not mean an empty list — alphabetical is a fine fallback."""
    assert _rank("nonsense_xyz", ALL_SKILLS)


def test_the_error_declares_truncation_and_the_total():
    """A short list under a key named `available_skills` reads as complete."""
    src = __import__("pathlib").Path("tools/skills_tool.py").read_text(encoding="utf-8")
    block = src[src.index("Skill '{name}' not found."):][:2000]
    assert "closest_skills" in block, "key must not imply completeness"
    assert "skills_total" in block, "total must be reported"
    assert "NOT the full list" in block, "truncation must be stated"
    assert "skills_list" in block, "must point at the complete listing"
