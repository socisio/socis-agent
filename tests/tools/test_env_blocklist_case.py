"""Provider credential env names are matched case-insensitively.

Ported from upstream b534f4b8c8. The blocklist is built from
`api_key_env_vars` and config keys -- all uppercase -- and every check was
`key in BLOCKLIST`, an exact set-membership test.

Environment variable names are case-SENSITIVE on Linux, so `openai_api_key`
and `OpenAI_Api_Key` are perfectly valid names that are not in that set. A
credential under one of those names was handed to a terminal or execute_code
child while the uppercase spelling was correctly withheld.

There were four such checks: three in tools/environments/local.py (the
terminal env, the execute_code env, and the merged-env path) and one in
tools/env_passthrough.py. Fixing one would have left the others open, which is
why this goes through a single predicate.

Comparing case-insensitively is the safe direction: a false positive withholds
a variable that merely looks credential-shaped, recoverable via passthrough
registration. A false negative leaks a key.
"""

import ast
import pathlib

import pytest


def _load_predicate():
    """Exec the predicate and its case-folded set standalone."""
    src = pathlib.Path("tools/environments/local.py").read_text(encoding="utf-8")
    start = src.index("_SOCIS_AGENT_PROVIDER_ENV_BLOCKLIST_CI = frozenset(")
    end = src.index("\n\n", src.index("def _is_blocked_provider_env"))
    block = src[start:end]
    ns = {"_SOCIS_AGENT_PROVIDER_ENV_BLOCKLIST": frozenset(
        {"OPENAI_API_KEY", "GLM_API_KEY", "ZAI_API_KEY", "SHODAN_API_KEY"})}
    exec(compile(block, "<pred>", "exec"), ns)
    return ns["_is_blocked_provider_env"]


is_blocked = _load_predicate()


@pytest.mark.parametrize("name", [
    "OPENAI_API_KEY",      # the spelling that was already blocked
    "openai_api_key",      # the bypass
    "OpenAI_Api_Key",
    "oPeNaI_aPi_kEy",
    "glm_api_key",         # this fork has GLM_API_KEY configured
    "Zai_Api_Key",
])
def test_every_casing_of_a_credential_is_blocked(name):
    assert is_blocked(name)


@pytest.mark.parametrize("name", ["HOME", "PATH", "TERM", "LANG", "hostname"])
def test_ordinary_variables_still_pass(name):
    """Over-blocking is the safe direction but not free -- a child that loses
    PATH is broken, not secured."""
    assert not is_blocked(name)


@pytest.mark.parametrize("name", ["", None])
def test_an_empty_name_is_not_blocked(name):
    assert not is_blocked(name)


def test_a_similar_but_different_name_is_not_blocked():
    """Case-folding must not become substring matching."""
    assert not is_blocked("MY_OPENAI_API_KEY_PATH")


# ── every call site uses the predicate ─────────────────────────────────────

def test_local_py_has_no_exact_membership_checks_left():
    """Three sites. Fixing one leaves the other two open, and they guard
    different children -- terminal, execute_code, and the merged env."""
    src = pathlib.Path("tools/environments/local.py").read_text(encoding="utf-8")
    code = "\n".join(
        line for line in src.splitlines()
        if not line.strip().startswith("#")
    )
    # The frozenset comprehension that BUILDS the folded view is allowed to
    # reference the raw set; a membership test against it is not.
    # `for key in BLOCKLIST` is an iteration, not a membership test — match
    # the `if` form specifically so the check does not flag it.
    for bad in ("if key in _SOCIS_AGENT_PROVIDER_ENV_BLOCKLIST",
                "if k in _SOCIS_AGENT_PROVIDER_ENV_BLOCKLIST"):
        assert bad not in code, f"case-sensitive check remains: {bad}"
    assert code.count("_is_blocked_provider_env(") >= 5, (
        "expected the predicate at its definition plus four call sites")


def test_credentials_are_stripped_by_iterating_the_environment():
    """The fourth site, and the worst of them.

    `for key in BLOCKLIST: env.pop(key)` removes only the blocklist's own
    uppercase spellings, so `openai_api_key` present in the environment was
    never popped and survived into the child while `OPENAI_API_KEY` was
    correctly removed. Iterating the ENVIRONMENT and testing each name is the
    only order that works.
    """
    src = pathlib.Path("tools/environments/local.py").read_text(encoding="utf-8")
    code = "\n".join(
        line for line in src.splitlines() if not line.strip().startswith("#"))
    assert "for key in _SOCIS_AGENT_PROVIDER_ENV_BLOCKLIST:" not in code, (
        "still iterating the blocklist instead of the environment")
    assert "for key in [k for k in env if _is_blocked_provider_env(k)]" in code


def test_the_strip_removes_every_casing():
    """Behavioural mirror of the loop above."""
    env = {"OPENAI_API_KEY": "a", "openai_api_key": "b",
           "glm_api_key": "c", "HOME": "/h"}
    for key in [k for k in env if is_blocked(k)]:
        env.pop(key, None)
    assert sorted(env) == ["HOME"]


def test_env_passthrough_uses_the_predicate():
    src = pathlib.Path("tools/env_passthrough.py").read_text(encoding="utf-8")
    assert "_is_blocked_provider_env" in src
    code = "\n".join(
        line for line in src.splitlines() if not line.strip().startswith("#"))
    assert "return name in _SOCIS_AGENT_PROVIDER_ENV_BLOCKLIST" not in code


def test_env_passthrough_has_a_fallback():
    """It imports the predicate from local.py; an ImportError must not turn
    the check off."""
    src = pathlib.Path("tools/env_passthrough.py").read_text(encoding="utf-8")
    idx = src.index("from tools.environments.local import _is_blocked_provider_env")
    window = src[idx: idx + 420]
    assert "except ImportError" in window
    assert "casefold()" in window, "the fallback must still fold case"
