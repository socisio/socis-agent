"""``x-opencode-session`` must survive the provider header chain.

The OpenCode Zen free tier requires this header. Without it the relay answers

    MissingSessionID: OpenCode's free tier can only be used in OpenCode

which the agent surfaced to the user as **"HTTP 401: Invalid API key"** —
pointing them at their credentials when the real cause was a missing header.
That misdirection cost real debugging time: the key was valid throughout, and
the same request succeeds with the header, keyless or keyed (verified by curl
against the live relay).

The mechanism already existed in ``agent/opencode_affinity.py`` and was applied
in ``chat_completion_helpers`` and ``auxiliary_client``. What broke it was
``agent_init``: nine consecutive branches each ASSIGN ``default_headers`` for
their provider, so whichever one matched replaced the dict wholesale and the
session header never reached the wire. The free-tier branch is the clearest
case — ``opencode_zen_free_headers()`` returns only Authorization, HTTP-Referer,
X-Title and User-Agent.

The fix merges after the whole chain rather than inside one branch, so a future
branch cannot reintroduce the bug. Same lesson as the model-selection guard
registry: put it where every path goes through.
"""

import ast
import pathlib

import pytest

from agent.opencode_affinity import (
    OPENCODE_SESSION_HEADER,
    is_opencode_target,
    opencode_session_headers,
)


# ── the header is computed for every OpenCode slug ─────────────────────────

@pytest.mark.parametrize("provider", [
    "opencode",        # the bare slug the failing log showed
    "opencode-zen",
    "opencode-free",
    "opencode-go",
])
def test_the_header_is_computed_for_every_opencode_slug(provider):
    """The log reported provider=opencode (bare) — normalize_provider collapses
    opencode-zen to it, so the bare form must be covered too."""
    assert is_opencode_target(provider, "https://opencode.ai/zen/v1")
    hdr = opencode_session_headers(provider, "https://opencode.ai/zen/v1", "s1")
    assert hdr == {OPENCODE_SESSION_HEADER: "s1"}


def test_it_is_a_noop_for_other_providers():
    """Merged unconditionally in agent_init, so it must not leak elsewhere."""
    assert opencode_session_headers(
        "openrouter", "https://openrouter.ai/api/v1", "s1") == {}
    assert opencode_session_headers(
        "nvidia", "https://integrate.api.nvidia.com/v1", "s1") == {}


def test_no_session_id_yields_no_header():
    """Sending an empty affinity value is worse than sending none."""
    assert opencode_session_headers("opencode-zen", "https://opencode.ai/zen/v1", "") == {}


# ── merging preserves what the branches set ────────────────────────────────

def test_merging_keeps_the_keyless_authorization_override():
    """The free tier needs Authorization: "" to suppress the SDK's bearer AND
    the session header. Losing either one breaks it."""
    branch = {
        "Authorization": "",
        "HTTP-Referer": "https://agent.socis.io",
        "X-Title": "SOCIS Agent",
        "User-Agent": "SOCISAgent/1",
    }
    merged = {**branch, **opencode_session_headers(
        "opencode", "https://opencode.ai/zen/v1", "s1")}
    assert merged["Authorization"] == "", "keyless override lost"
    assert merged[OPENCODE_SESSION_HEADER] == "s1"
    assert merged["X-Title"] == "SOCIS Agent", "attribution header lost"


# ── wiring: the merge must come after the branch chain ─────────────────────

def _agent_init_src():
    return pathlib.Path("agent/agent_init.py").read_text(encoding="utf-8")


def test_agent_init_merges_the_session_header():
    src = _agent_init_src()
    assert "opencode_session_headers" in src, (
        "agent_init never applies the affinity header — every provider branch "
        "assigns default_headers and drops it")


def test_the_merge_runs_after_every_branch_assignment():
    """Merging inside one branch would leave the other eight broken.

    Uses the AST rather than text matching: the merge is itself an assignment
    to default_headers spanning several lines, so a line-based scan counts it
    as one of the branches it is supposed to follow.
    """
    tree = ast.parse(_agent_init_src())

    branch_lines, merge_lines = [], []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        tgt = node.targets[0]
        if not (isinstance(tgt, ast.Subscript)
                and isinstance(tgt.value, ast.Name)
                and tgt.value.id == "client_kwargs"):
            continue
        key = getattr(tgt.slice, "value", None)
        if key != "default_headers":
            continue
        # The merge is the one whose value re-reads client_kwargs.
        src = ast.unparse(node.value)
        (merge_lines if "client_kwargs.get" in src else branch_lines).append(node.lineno)

    assert branch_lines, "no provider header assignments found — file restructured?"
    assert merge_lines, "the merge is gone"
    assert max(merge_lines) > max(branch_lines), (
        "the merge runs before the last branch assignment, so that branch "
        "still clobbers the session header")


def test_the_merge_does_not_replace_the_branch_headers():
    """Assigning instead of merging would drop the attribution and keyless
    headers the branches set — trading one bug for another."""
    tree = ast.parse(_agent_init_src())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        src_val = ast.unparse(node.value)
        if "_oc_session" in src_val:
            found = True
            assert "client_kwargs.get" in src_val, (
                "the session merge assigns rather than merges, dropping the "
                "branch headers")
    assert found, "no assignment consumes the computed session header"


def test_the_merge_is_guarded_against_import_failure():
    """A header optimisation must never break client construction."""
    src = _agent_init_src()
    idx = src.index("from agent.opencode_affinity import opencode_session_headers")
    window = src[idx - 200: idx + 900]
    assert "except Exception" in window, "an import failure would break the client"


def test_the_computed_header_is_actually_consumed():
    """`if _oc_session:` guarding a no-op would pass every other test here.

    The AST checks confirm the merge exists and comes last, but not that it
    runs. Assert the assignment sits inside the truthiness guard so disabling
    the guard cannot leave the merge unreachable and the tests green.
    """
    tree = ast.parse(_agent_init_src())
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test_src = ast.unparse(node.test)
        if "_oc_session" not in test_src:
            continue
        body = " ".join(ast.unparse(n) for n in node.body)
        if "client_kwargs['default_headers']" in body.replace('"', "'"):
            return
    raise AssertionError(
        "no `if _oc_session:` guard wraps the default_headers merge — the "
        "computed header may never be applied")


# ── the responses/codex transport needs it too ─────────────────────────────

def _codex_src():
    return pathlib.Path("agent/transports/codex.py").read_text(encoding="utf-8")


def test_the_responses_transport_applies_the_session_header():
    """A model routed through the responses transport still 401'd after the
    agent_init fix.

    The log showed `codex_stream_request` for muse-spark-1.3-contributor-free
    and `chat_completion_stream_request` for big-pickle — same provider, same
    key, seconds apart, and only the second worked. This transport builds its
    own client and its own extra_headers, so neither agent_init's
    default_headers merge nor chat_completion_helpers' per-request merge
    reaches it. Codex and xAI affinity were already handled here; OpenCode was
    missed.
    """
    src = _codex_src()
    assert "opencode_session_headers" in src, (
        "the responses transport never applies the OpenCode affinity header")


def test_it_merges_rather_than_replaces_extra_headers():
    """Codex `session_id` and xAI `x-grok-conv-id` are set on the same dict —
    assigning would drop whichever ran first."""
    src = _codex_src()
    idx = src.index("_oc = opencode_session_headers")
    window = src[idx: idx + 900]
    assert "_merged.update(_oc)" in window, "assigns instead of merging"
    assert 'kwargs.get("extra_headers")' in window, (
        "does not read the existing extra_headers before writing")


def test_it_reads_provider_and_base_url_from_params():
    """`agent` is not in scope in build_kwargs — an earlier version of this
    patch referenced it and would have raised NameError on every OpenCode
    request through this transport, silently swallowed by the try/except."""
    src = _codex_src()
    idx = src.index("_oc = opencode_session_headers")
    window = src[idx: idx + 260]
    assert 'params.get("provider")' in window
    assert 'params.get("base_url")' in window
    assert "getattr(agent" not in window, "references an out-of-scope `agent`"


def test_the_transport_merge_is_guarded():
    src = _codex_src()
    idx = src.index("from agent.opencode_affinity import opencode_session_headers")
    assert "except Exception" in src[idx: idx + 1200], (
        "an import failure here would break every responses-transport request")
