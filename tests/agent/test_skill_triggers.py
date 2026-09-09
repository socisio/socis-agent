"""Skill `triggers:` reach the prompt index.

Ten skills have declared trigger phrases in their frontmatter since they were
written, and no code read the field. Loading was decided entirely by lexical
overlap with the 60-character description, which works for a question phrased
like the skill and fails for one phrased like a person:

  "Walk me through the incident response phases"      -> loaded
  "How do I decide whether an alert is a true positive?" -> did not

The second missed even though alert-triage declares the trigger "is this a
true positive". These tests pin that the field is read, capped, and defensive
about the shapes real frontmatter contains.
"""

import pytest

from agent.skill_utils import (
    SKILL_PROMPT_TRIGGER_CHARS,
    SKILL_PROMPT_TRIGGER_LIMIT,
    extract_skill_triggers,
)


def test_triggers_are_extracted():
    fm = {"triggers": ["triage this alert", "is this a true positive"]}
    assert extract_skill_triggers(fm) == [
        "triage this alert", "is this a true positive"]


def test_the_phrase_that_missed_is_now_present():
    """The concrete regression: this exact trigger exists in alert-triage and
    never reached the model."""
    fm = {"triggers": ["triage this alert", "is this a true positive",
                       "investigate this detection"]}
    assert "is this a true positive" in extract_skill_triggers(fm)


def test_capped_so_the_index_stays_affordable():
    """Every skill in the index pays this cost on every turn."""
    fm = {"triggers": [f"phrase {i}" for i in range(20)]}
    assert len(extract_skill_triggers(fm)) == SKILL_PROMPT_TRIGGER_LIMIT


def test_overlong_phrases_are_skipped_not_truncated():
    """A truncated trigger matches nothing and costs context anyway."""
    long = "x" * (SKILL_PROMPT_TRIGGER_CHARS + 1)
    out = extract_skill_triggers({"triggers": [long, "short one"]})
    assert out == ["short one"]


def test_quotes_are_stripped():
    """YAML frontmatter quotes these inconsistently."""
    assert extract_skill_triggers({"triggers": ["'quoted'", '"double"']}) == [
        "quoted", "double"]


def test_blank_entries_are_dropped():
    assert extract_skill_triggers({"triggers": ["", "   ", "real"]}) == ["real"]


@pytest.mark.parametrize("value", [None, "", "a string", 42, {"a": 1}])
def test_a_non_list_triggers_field_is_ignored(value):
    """Frontmatter is hand-written; a scalar here must not raise."""
    assert extract_skill_triggers({"triggers": value}) == []


def test_missing_field_is_fine():
    assert extract_skill_triggers({}) == []
    assert extract_skill_triggers({"description": "x"}) == []
