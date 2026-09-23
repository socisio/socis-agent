"""The rebrand leaves Nous infrastructure alone.

SOCIS uses Nous as an LLM provider, so Nous's servers and identifiers are not
branding. Rebranding current upstream on 2026-09-23 showed the map did not know
that: blanket ("nousresearch", "socis") and ("nousresearch.com", "socis.io")
entries rewrote ~280 references to Nous's live infrastructure.

  inference-api.nousresearch.com -> inference-api.socis.io   Nous provider dead
  portal.nousresearch.com        -> portal.socis.io          Nous login dead
  com.nousresearch.hermes        -> com.socis.socis          every install loses its
                                                             Keychain items and granted
                                                             macOS permissions
  DEFAULT_NOUS_CLIENT_ID "hermes-cli" -> "socis-cli"         rejected by Nous OAuth

The fork had corrected these by hand after the original rebrand; the fixes were
never encoded back into the map, so a fresh rebrand undid them. And the
post-flight checks passed, because all of it was valid code.

These tests exercise the real apply_text_replacements.
"""

import importlib.util
import pathlib
import sys

import pytest

_DIR = pathlib.Path("scripts/rebrand")


def _load():
    sys.path.insert(0, str(_DIR))
    spec = importlib.util.spec_from_file_location("run_rebrand", _DIR / "run_rebrand.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rr = _load()
TABLE = rr.build_replacement_table()


def rebrand(text):
    out, _ = rr.apply_text_replacements(text, TABLE)
    return out


# ── Nous infrastructure survives ───────────────────────────────────────────

@pytest.mark.parametrize("host", [
    "inference-api.nousresearch.com",
    "stg-inference-api.nousresearch.com",
    "inference.nousresearch.com",
    "portal.nousresearch.com",
    "portal.staging-nousresearch.com",
    "telemetry.nousresearch.com",
    "gateway-gateway.nousresearch.com",
    "ares-3009.agents.nousresearch.com",
])
def test_a_nous_service_host_survives(host):
    assert rebrand(f"https://{host}/v1") == f"https://{host}/v1"


def test_a_nous_host_unknown_to_any_list_still_survives():
    """The point of a RULE over a list: a list fell behind on the first real
    run, missing 24 test fixtures and a Windows installer URL."""
    assert "brand-new-service.nousresearch.com" in rebrand(
        "https://brand-new-service.nousresearch.com/")


def test_a_leading_dot_suffix_survives():
    """Product code checks `host.endswith(".agents.nousresearch.com")`. A
    pattern that required a label first skipped this form."""
    src = 'host.endswith(".agents.nousresearch.com")'
    assert rebrand(src) == src


def test_the_bundle_id_survives():
    """Changing it orphans Keychain items and every granted permission."""
    assert rebrand('"appId": "com.nousresearch.hermes"') == (
        '"appId": "com.nousresearch.hermes"')


def test_the_oauth_client_id_survives():
    src = 'DEFAULT_NOUS_CLIENT_ID = "hermes-cli"'
    assert rebrand(src) == src


# ── branding still rebrands ────────────────────────────────────────────────

def test_the_docs_site_rebrands():
    assert "agent.socis.io" in rebrand("https://hermes-agent.nousresearch.com/docs/")


def test_the_installer_site_rebrands():
    assert "setup.agent.socis.io" in rebrand("https://setup.hermes-agent.nousresearch.com/x")


def test_the_shields_escaped_docs_host_rebrands():
    """shields.io writes a literal "-" as "--". Unmapped, the catch-all turned
    the README badge into "socis--agent.socis.io" -- a host that does not exist."""
    out = rebrand("https://img.shields.io/badge/Docs-hermes--agent.nousresearch.com-FFD700")
    assert "Docs-agent.socis.io" in out
    assert "socis--agent" not in out


def test_the_cli_toolset_name_still_rebrands():
    """"hermes-cli" is ALSO the CLI's default toolset. Protecting the bare
    string left the toolset as "hermes-cli" while config asked for
    "socis-cli", so the CLI loaded with no default tools."""
    assert rebrand('default_toolset="hermes-cli"') == 'default_toolset="socis-cli"'
    assert rebrand('"toolsets": ["hermes-cli"]') == '"toolsets": ["socis-cli"]'


def test_protection_does_not_leak_sentinels():
    """The masking must restore every token it inserted."""
    out = rebrand("a https://portal.nousresearch.com b com.nousresearch.hermes c")
    assert "\x00" not in out
    assert "REBRAND_PROTECTED" not in out


# ── the post-flight check ──────────────────────────────────────────────────

def test_the_host_check_flags_a_rewritten_nous_host(tmp_path):
    (tmp_path / "x.py").write_text('URL = "https://inference-api.socis.io/v1"\n')
    hits = rr.unknown_host_check(tmp_path)
    assert [h for _, _, h in hits] == ["inference-api.socis.io"]


def test_the_host_check_accepts_real_socis_hosts(tmp_path):
    (tmp_path / "x.py").write_text('A = "https://agent.socis.io/docs"\n')
    assert rr.unknown_host_check(tmp_path) == []


def test_the_host_check_ignores_a_badge_separator(tmp_path):
    """A DNS label cannot start with "-"; in "Docs-agent.socis.io" the dash is
    the badge's separator."""
    (tmp_path / "README.md").write_text("badge/Docs-agent.socis.io-FFD700\n")
    assert rr.unknown_host_check(tmp_path) == []


def test_post_flight_failures_set_the_exit_code():
    """They used to be printed while the script exited 0, so a caller using
    check=True -- scripts/fork_delta.py -- passed on syntax errors too."""
    src = (_DIR / "run_rebrand.py").read_text(encoding="utf-8")
    assert "if errors or stale or hosts:\n            return 1" in src
    assert "raise SystemExit(main() or 0)" in src


def test_upstreams_own_repo_becomes_the_forks_repo():
    """The GitHub ORG is "socisio", not the brand name. The prose rule
    ("NousResearch", "SOCIS") turned github.com/NousResearch/hermes-agent into
    github.com/SOCIS/socis-agent -- 515 differences against the fork."""
    assert rebrand("https://github.com/NousResearch/hermes-agent/issues/1") == (
        "https://github.com/socisio/socis-agent/issues/1")


def test_a_bare_repo_reference_uses_the_org_too():
    """`gh search issues --repo SOCIS/socis-agent` fails: there is no SOCIS org.
    The fork had 103 of these, written by hand -- the rebrand now gets them
    right where the fork did not."""
    assert rebrand("gh search issues --repo NousResearch/hermes-agent") == (
        "gh search issues --repo socisio/socis-agent")


def test_the_brand_name_itself_still_becomes_socis():
    """Only the repo reference uses the org; prose keeps the brand."""
    assert rebrand("Built by NousResearch") == "Built by SOCIS"



# ── NousResearch/<name>: only the repo is ours ─────────────────────────────

def test_a_nous_huggingface_dataset_is_not_rewritten_as_our_repo():
    """REGRESSION. An earlier plain-substring entry, ("NousResearch/hermes-
    agent", "socisio/socis-agent"), matched the PREFIX of this dataset name and
    produced "socisio/socis-agent-megascience-sft1" -- which does not exist."""
    src = '"NousResearch/hermes-agent-megascience-sft1"'
    assert rebrand(src) == src


@pytest.mark.parametrize("ref", [
    "NousResearch/Hermes-4-70B",                # HF model: a provider rejects SOCIS/SOCIS-4-70B
    "NousResearch/Hermes-3-Llama-3.1-70B",
    "NousResearch/hermes-example-plugins",      # the fork had 27 of these damaged
    "NousResearch/hermes-example-plugins.git",
    "NousResearch/atropos",
    "NousResearch/hermes-media-studio",
])
def test_nous_owned_resources_keep_their_owner(ref):
    assert rebrand(ref) == ref


def test_the_repo_with_a_git_suffix_becomes_ours():
    assert rebrand("github.com/NousResearch/hermes-agent.git") == (
        "github.com/socisio/socis-agent.git")


def test_a_sentence_ending_after_the_repo_is_not_part_of_it():
    assert rebrand("see NousResearch/hermes-agent.") == "see socisio/socis-agent."


def test_the_nous_org_page_is_left_as_an_attribution_link():
    src = "https://github.com/NousResearch)"
    assert rebrand(src) == src


def test_the_map_has_no_plain_substring_repo_entry():
    """A substring entry cannot express the word boundary this needs."""
    import rebrand_map
    olds = [o for o, _ in rebrand_map.DOMAIN_REPLACEMENTS]
    assert "NousResearch/hermes-agent" not in olds
