"""Tests for the `mitre` toolset.

The stakes here are different from most tooling: technique IDs reach CUSTOMER
DELIVERABLES. A wrong ID renders in Navigator as a cell the customer reads as
covered, and neither they nor the analyst can tell from `T1059.003` alone that
it should have been `T1059.001`. So these tests pin the refusals, not just the
happy paths.

A fixture STIX bundle stands in for the 35 MB download — no network, and the
handlers read the cache exactly as they would in an air-gapped install.
"""

import json
import time
from pathlib import Path

import pytest

FIXTURE = {
    "objects": [
        {"type": "x-mitre-collection", "x_mitre_version": "17.1"},
        {
            "type": "attack-pattern",
            "name": "Command and Scripting Interpreter",
            "description": "Adversaries may abuse command and script interpreters.",
            "external_references": [{
                "source_name": "mitre-attack", "external_id": "T1059",
                "url": "https://attack.mitre.org/techniques/T1059/",
            }],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "execution"}],
            "x_mitre_platforms": ["Windows", "Linux", "macOS"],
            "x_mitre_data_sources": ["Process: Process Creation"],
            "x_mitre_detection": "Monitor executed commands and arguments.",
        },
        {
            "type": "attack-pattern",
            "name": "PowerShell",
            "description": "Adversaries may abuse PowerShell commands.",
            "x_mitre_is_subtechnique": True,
            "external_references": [{
                "source_name": "mitre-attack", "external_id": "T1059.001",
                "url": "https://attack.mitre.org/techniques/T1059/001/",
            }],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "execution"}],
            "x_mitre_platforms": ["Windows"],
        },
        {
            "type": "attack-pattern",
            "name": "Scheduled Task",
            "description": "Adversaries may abuse task scheduling.",
            "x_mitre_is_subtechnique": True,
            "external_references": [{
                "source_name": "mitre-attack", "external_id": "T1053.005",
                "url": "https://attack.mitre.org/techniques/T1053/005/",
            }],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "persistence"}],
            "x_mitre_platforms": ["Windows"],
        },
        # Revoked by MITRE. Navigator still renders it, so excluding it here is
        # the only thing standing between a withdrawn ID and a deliverable.
        {
            "type": "attack-pattern",
            "name": "Withdrawn Technique",
            "revoked": True,
            "external_references": [{
                "source_name": "mitre-attack", "external_id": "T9999"}],
        },
        {
            "type": "attack-pattern",
            "name": "Deprecated Technique",
            "x_mitre_deprecated": True,
            "external_references": [{
                "source_name": "mitre-attack", "external_id": "T9998"}],
        },
    ]
}


@pytest.fixture(autouse=True)
def attack_data(tmp_path, monkeypatch):
    """Seed the cache and clear the per-process index between tests."""
    monkeypatch.setenv("SOCIS_AGENT_HOME", str(tmp_path))
    cache = tmp_path / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "mitre-attack-enterprise.json").write_text(json.dumps(FIXTURE))

    import tools.mitre_attack as m
    m._index_cache = None
    yield cache
    m._index_cache = None


# ── lookup ──────────────────────────────────────────────────────────────────


def test_technique_lookup_returns_tactics_and_detection():
    from tools.mitre_attack import _handle_technique
    out = _handle_technique({"technique_id": "T1059.001"})
    assert "T1059.001" in out and "PowerShell" in out
    assert "execution" in out
    assert "17.1" in out, "output must state the ATT&CK version"


def test_lookup_is_case_insensitive():
    from tools.mitre_attack import _handle_technique
    assert "PowerShell" in _handle_technique({"technique_id": "t1059.001"})


def test_revoked_technique_is_not_current():
    """MITRE withdrew T9999. Navigator renders it anyway."""
    from tools.mitre_attack import _handle_technique
    out = _handle_technique({"technique_id": "T9999"})
    assert "not a current Enterprise technique" in out


def test_deprecated_technique_is_not_current():
    from tools.mitre_attack import _handle_technique
    assert "not a current" in _handle_technique({"technique_id": "T9998"})


def test_unknown_subtechnique_lists_the_valid_siblings():
    """The PowerShell/cmd confusion, caught.

    T1059.003 is Windows Command Shell; it is absent from this fixture, so the
    error must name the parent and the sub-techniques that DO exist rather
    than a bare "not found".
    """
    from tools.mitre_attack import _handle_technique
    out = _handle_technique({"technique_id": "T1059.003"})
    assert "Parent T1059 exists" in out
    assert "T1059.001" in out


def test_malformed_id_is_rejected_with_the_expected_shape():
    from tools.mitre_attack import _handle_technique
    out = _handle_technique({"technique_id": "PowerShell"})
    assert "not a technique ID" in out
    assert "attack_search" in out, "must point at the way to find one by name"


# ── search and tactics ──────────────────────────────────────────────────────


def test_search_finds_by_name():
    from tools.mitre_attack import _handle_search
    assert "T1059.001" in _handle_search({"query": "powershell"})


def test_search_finds_by_description():
    from tools.mitre_attack import _handle_search
    assert "T1053.005" in _handle_search({"query": "task scheduling"})


def test_search_scopes_by_tactic():
    from tools.mitre_attack import _handle_search
    out = _handle_search({"query": "adversaries", "tactic": "persistence"})
    assert "T1053.005" in out
    assert "T1059.001" not in out


def test_search_miss_states_the_version_not_just_no_results():
    from tools.mitre_attack import _handle_search
    out = _handle_search({"query": "zzz-nonexistent"})
    assert "No technique matches" in out and "17.1" in out


def test_invalid_tactic_lists_the_valid_ones():
    from tools.mitre_attack import _handle_tactic
    out = _handle_tactic({"tactic": "pivoting"})
    assert "not an Enterprise tactic" in out
    assert "lateral-movement" in out


# ── Navigator layers: the deliverable ───────────────────────────────────────


def test_layer_is_valid_json_with_the_versions_block():
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": ["T1059", "T1059.001"], "name": "Acme"})
    body = out.split("```json")[1].split("```")[0]
    layer = json.loads(body)
    assert layer["name"] == "Acme"
    assert layer["domain"] == "enterprise-attack"
    assert {"attack", "navigator", "layer"} <= set(layer["versions"])
    assert len(layer["techniques"]) == 2


def test_layer_stamps_the_attack_version():
    """A deliverable that does not record its matrix version cannot be
    reproduced or defended later."""
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": ["T1059"]})
    layer = json.loads(out.split("```json")[1].split("```")[0])
    assert layer["versions"]["attack"] == "17.1"


def test_layer_carries_scores_and_comments():
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": [
        {"id": "T1059.001", "score": 100, "comment": "Sigma deployed, tested"},
    ]})
    entry = json.loads(out.split("```json")[1].split("```")[0])["techniques"][0]
    assert entry["score"] == 100
    assert entry["comment"] == "Sigma deployed, tested"


def test_layer_refuses_an_unknown_technique():
    """The whole reason this is data-backed.

    An unverified ID renders in Navigator as a cell the customer reads as
    covered, so the layer must not be generated at all.
    """
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": ["T1059.001", "T1234.567"]})
    assert "NOT generated" in out
    assert "T1234.567" in out
    assert "```json" not in out, "no layer may be emitted when an ID is unknown"


def test_layer_refuses_a_revoked_technique():
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": ["T1059", "T9999"]})
    assert "NOT generated" in out and "T9999" in out


def test_layer_accepts_a_space_or_comma_separated_string():
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": "T1059, T1059.001"})
    layer = json.loads(out.split("```json")[1].split("```")[0])
    assert len(layer["techniques"]) == 2


# ── offline behaviour ───────────────────────────────────────────────────────


def test_status_reports_version_count_and_age(attack_data):
    from tools.mitre_attack import _handle_status
    out = _handle_status({})
    assert "17.1" in out
    assert "4" in out, "4 current techniques after excluding revoked/deprecated"
    assert "Navigator layer format" in out


def test_stale_cache_still_answers_but_says_so(attack_data, monkeypatch):
    """An air-gapped install lives on the cache permanently.

    That is fine — ATT&CK ships twice a year — but the output must not imply
    the data is current.
    """
    import tools.mitre_attack as m
    old = time.time() - (400 * 86400)
    cache = attack_data / "mitre-attack-enterprise.json"
    import os
    os.utime(cache, (old, old))
    monkeypatch.setattr(m, "_fetch", lambda force=False: (
        FIXTURE, "offline — using cached ATT&CK data 400 day(s) old (no network)"))
    m._index_cache = None
    out = m._handle_technique({"technique_id": "T1059"})
    assert "T1059" in out
    assert "400 day" in out and "offline" in out


def test_missing_data_names_the_install_command(tmp_path, monkeypatch):
    import tools.mitre_attack as m
    monkeypatch.setenv("SOCIS_AGENT_HOME", str(tmp_path / "empty"))
    monkeypatch.setattr(m, "_fetch", lambda force=False: (None, (
        "No ATT&CK data available and the download failed: offline\n"
        "Install it with `bash scripts/install.sh --ensure mitre`.")))
    m._index_cache = None
    out = m._handle_technique({"technique_id": "T1059"})
    assert "--ensure mitre" in out


def test_every_registered_tool_is_in_the_mitre_toolset():
    """Guards the toolset name: a typo would scatter these across toolsets and
    silently break `-t mitre`."""
    import re
    src = Path("tools/mitre_attack.py").read_text(encoding="utf-8")
    pairs = re.findall(r'registry\.register\(\s*name="(\w+)",\s*toolset="([\w-]+)"', src)
    assert len(pairs) == 5, f"expected 5 registrations, found {len(pairs)}"
    assert all(ts == "mitre" for _, ts in pairs)


# ── the shapes a caller actually reaches for ────────────────────────────────


def test_layer_accepts_navigators_own_techniqueID_key():
    """`techniqueID` is what Navigator calls this field in layer JSON, so it is
    the first thing a caller tries.

    It used to be unrecognised and the entry was dropped SILENTLY — the tool
    returned a ✅ over `"techniques": []`. Ten turns of an agent guessing at
    the shape, against a tool whose entire purpose is catching bad layers.
    """
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": [
        {"techniqueID": "T1059.001", "score": 100},
        {"techniqueID": "T1053.005", "score": 40},
    ]})
    layer = json.loads(out.split("```json")[1].split("```")[0])
    assert len(layer["techniques"]) == 2
    assert layer["techniques"][0]["score"] == 100
    assert layer["techniques"][1]["score"] == 40


def test_layer_refuses_an_object_with_no_recognised_id_key():
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": [{"foo": "bar", "score": 1}]})
    assert "NOT generated" in out
    assert "no recognised ID key" in out
    assert "foo" in out, "must name the keys it actually received"
    assert "Accepted shapes" in out
    assert "```json" not in out


def test_layer_never_emits_an_empty_techniques_list():
    """An empty layer LOADS in Navigator and shows a blank matrix, which reads
    as 'no coverage' rather than 'the call was wrong'."""
    from tools.mitre_attack import _handle_layer
    for bad in ([{"nope": 1}], [None], [{}]):
        out = _handle_layer({"techniques": bad})
        assert "NOT generated" in out, f"{bad} produced a layer"
        assert '"techniques": []' not in out


def test_layer_rejects_a_stix_id_rather_than_silently_dropping_it():
    """STIX `attack-pattern--…` ids are a plausible confusion; they are not
    technique IDs and must be named as unknown."""
    from tools.mitre_attack import _handle_layer
    out = _handle_layer({"techniques": [
        {"id": "attack-pattern--970a3432-3237-47ad-bcca-7d8cbb217736", "score": 1}]})
    assert "NOT generated" in out
    assert "ATTACK-PATTERN" in out.upper()
