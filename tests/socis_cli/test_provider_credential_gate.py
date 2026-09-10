"""A model-name guess may not switch to a provider with no credentials.

Ported from upstream 2466684db. `detect_provider_for_model()` infers a
provider from a model NAME, and `/model <name>` where the name is only known
to another provider used to switch the session there regardless of whether
that provider was usable.

For most vendors that is an immediate 401 — noisy, but honest. For OpenRouter
it is worse: its runtime resolves with an EMPTY key instead of raising, so the
session moved silently onto a metered aggregator the user never chose and
never authenticated to.

Two cases are deliberately NOT gated:
  * current_provider is "auto" or unset — nothing to protect, and the
    credential step should fail loudly rather than swallow the user's input
  * `_resolve_provider_prefix` (vendor/model naming a provider declared in
    `providers:`) — that is a selection, not a guess
"""

import ast
import pathlib
import types

import pytest


def _load():
    """Exec the two functions with stubs so the REAL logic is exercised."""
    src = pathlib.Path("socis_cli/models.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    want = {"provider_has_credentials", "detect_provider_for_model"}
    nodes = [n for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name in want]
    assert len(nodes) == 2, f"expected both functions, found {[n.name for n in nodes]}"
    import os
    import typing
    ns = {
        "Optional": typing.Optional,
        "os": os,
        "logger": types.SimpleNamespace(debug=lambda *a, **k: None),
        "detect_static_provider_for_model": lambda n, c: None,
        "_model_in_provider_catalog": lambda a, b: False,
        "_provider_keys": lambda p: (),
        "_find_openrouter_slug": lambda n: f"vendor/{n}" if n == "known-model" else None,
        "_resolve_provider_prefix": lambda n: None,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<detect>", "exec"), ns)
    return ns


@pytest.fixture
def detect():
    ns = _load()

    def _run(name, current, *, has_creds):
        ns["provider_has_credentials"] = lambda p: has_creds
        return ns["detect_provider_for_model"](name, current)

    return _run


# ── the regression ─────────────────────────────────────────────────────────

def test_no_silent_switch_to_an_uncredentialed_provider(detect):
    """The bug: on nvidia, naming a model OpenRouter knows moved the session
    to OpenRouter with no key — and OpenRouter does not raise on an empty
    key, so nothing surfaced."""
    assert detect("known-model", "nvidia", has_creds=False) is None


def test_a_switch_is_allowed_when_the_target_is_usable(detect):
    assert detect("known-model", "nvidia", has_creds=True) == (
        "openrouter", "vendor/known-model")


# ── the deliberate exceptions ──────────────────────────────────────────────

@pytest.mark.parametrize("current", ["auto", "", "  "])
def test_no_current_provider_hands_the_guess_back(detect, current):
    """With nothing selected there is no session to protect, and the
    credential step failing loudly beats silently ignoring what was typed."""
    assert detect("known-model", current, has_creds=False) == (
        "openrouter", "vendor/known-model")


def test_staying_on_the_same_provider_is_never_gated(detect):
    """Resolving a slug within the CURRENT provider is not a switch."""
    ns = _load()
    ns["provider_has_credentials"] = lambda p: False
    ns["_find_openrouter_slug"] = lambda n: "vendor/x"
    # already on openrouter: returns the resolved slug, no gate involved
    assert ns["detect_provider_for_model"]("x", "openrouter") == (
        "openrouter", "vendor/x")


# ── the credential check itself ────────────────────────────────────────────

def test_the_gate_checks_all_three_credential_homes():
    """env/.env key, auth-store login, credential pool. Missing any one of
    them would report a usable provider as unusable and block a valid
    switch — the opposite failure, and just as bad."""
    src = pathlib.Path("socis_cli/models.py").read_text(encoding="utf-8")
    start = src.index("def provider_has_credentials(")
    body = src[start: src.index("def detect_provider_for_model(", start)]
    assert "api_key_env_vars" in body, "env-var key check missing"
    assert "_load_auth_store" in body, "auth-store check missing"
    assert "load_pool" in body, "credential-pool check missing"
    assert "has_available()" in body, (
        "a pool with no AVAILABLE entry is not a usable credential")


def test_a_broken_credential_source_reads_as_no_credential():
    """Errors must not make an unusable provider look available — that is
    the exact failure this gate exists to prevent."""
    src = pathlib.Path("socis_cli/models.py").read_text(encoding="utf-8")
    start = src.index("def provider_has_credentials(")
    body = src[start: src.index("def detect_provider_for_model(", start)]
    assert body.count("except Exception") >= 3, (
        "each credential source must fail closed independently")
    assert body.rstrip().endswith("return False"), (
        "the default must be False, not True")
