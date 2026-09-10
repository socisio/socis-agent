"""The availability guard runs on every model-selection surface.

Four surfaces pick models — the CLI picker, the desktop app
(`POST /api/model/set`), the dashboard and the TUI — and all four trusted a
catalogue. The desktop app failed with

    Provider: opencode-zen  Model: x-preview-f-free
    HTTP 401: Model x-preview-f-free is not supported

because that model was delisted on 2026-08-26, months after it was written to
config.yaml, and nothing revalidated it. Fixing the CLI picker alone left the
other three broken, which is why this lives in ``_GUARDS``: the registry's own
comment says adding a guard there "makes it appear on every surface at once".

The guard must be RELUCTANT to condemn. An empty balance, a missing session
header, Cloudflare, or a network blip all pass. A guard that fires on
conditions unrelated to the model is one people learn to click through.
"""

import io
import urllib.error
import urllib.request

import pytest

from socis_cli.model_selection_guards import (
    _GUARDS,
    _availability_guard,
    selection_warnings,
)


class _Err(urllib.error.HTTPError):
    def __init__(self, code, body=""):
        super().__init__("u", code, "e", {}, io.BytesIO(body.encode()))


@pytest.fixture
def respond(monkeypatch):
    def _install(code=200, body="", exc=None):
        def fake(req, timeout=0):
            if exc is not None:
                raise exc
            if 200 <= code < 300:
                class R:
                    status = code
                    def __enter__(s): return s
                    def __exit__(s, *a): return False
                return R()
            raise _Err(code, body)
        monkeypatch.setattr(urllib.request, "urlopen", fake)
    return _install


def _warns(**kw):
    ws = selection_warnings(
        kw.pop("model", "m"),
        provider=kw.pop("provider", "opencode-zen"),
        base_url=kw.pop("base_url", "https://opencode.ai/zen/v1"),
        api_key=kw.pop("api_key", "k"),
        **kw,
    )
    return [w for w in ws if w.kind == "availability"]


# ── it is registered, not just defined ─────────────────────────────────────

def test_the_guard_is_in_the_registry():
    """Defining it is not enough. The registry is what reaches all four
    surfaces; a guard outside it fixes nothing."""
    assert _availability_guard in _GUARDS


def test_it_runs_last():
    """It makes a network call. No point probing a model the user is about to
    reject on cost or data-policy grounds."""
    assert _GUARDS[-1] is _availability_guard


# ── verdicts on real provider responses ────────────────────────────────────

DEAD = [
    ("Zen delisted (the desktop failure)", 401,
     '{"error":{"type":"ModelError",'
     '"message":"Model x-preview-f-free is not supported"}}'),
    ("NVIDIA retired", 410, '{"detail":"has reached its end of life"}'),
    ("not servable here", 404, "404 page not found"),
]

ALIVE = [
    ("empty balance", 401,
     '{"error":{"type":"CreditsError","message":"Insufficient balance"}}'),
    ("OpenCode Go session header", 400,
     '{"error":{"type":"MissingSessionID","message":"x"}}'),
    ("Cloudflare block", 403, "error code: 1010"),
    ("throttled", 429, "too many requests"),
]


@pytest.mark.parametrize("label,code,body", DEAD)
def test_a_dead_model_warns(respond, label, code, body):
    respond(code, body)
    got = _warns()
    assert got, f"{label} did not warn"
    assert got[0].title == "Model Unavailable"
    assert got[0].model == "m"


@pytest.mark.parametrize("label,code,body", ALIVE)
def test_a_non_model_failure_does_not_warn(respond, label, code, body):
    respond(code, body)
    assert not _warns(), f"{label} warned — that trains users to click through"


def test_a_served_model_does_not_warn(respond):
    respond(200)
    assert not _warns()


def test_the_provider_message_reaches_the_user(respond):
    """The confirm dialog shows warning.message, so the provider's own words
    have to survive into it."""
    respond(401, '{"error":{"type":"ModelError","message":"Model foo is not supported"}}')
    got = _warns()
    assert "not supported" in got[0].message
    assert "Pick another model" in got[0].message


# ── it must not break selection ────────────────────────────────────────────

@pytest.mark.parametrize("missing", ["provider", "base_url", "api_key", "model"])
def test_it_is_silent_without_the_four_inputs(missing):
    """Keyless and OAuth providers have their own flows. Without all four
    there is nothing to ask, and guessing would warn on working setups."""
    kw = {"model": "m", "provider": "p", "base_url": "https://x/v1", "api_key": "k"}
    kw[missing] = ""
    assert _availability_guard(
        kw["model"], kw["provider"], kw["base_url"], kw["api_key"], None) is None


@pytest.mark.parametrize("exc", [OSError("refused"), TimeoutError("slow")])
def test_a_network_failure_does_not_warn(respond, exc):
    respond(exc=exc)
    assert not _warns()


def test_a_raising_guard_would_be_silently_swallowed(respond, monkeypatch):
    """selection_warnings() swallows guard exceptions by design, so a broken
    guard fails OPEN and invisibly.

    This is not hypothetical: the first version of this guard built a
    SelectionWarning without its required title/model/provider fields, raised
    TypeError on every call, and the chain reported no warnings at all — it
    looked like every model was fine. The DEAD cases above are what catch
    that; this test documents why they must exist.
    """
    respond(401, '{"error":{"type":"ModelError","message":"not supported"}}')
    # Sanity: the guard returns a warning rather than raising.
    assert _availability_guard(
        "m", "p", "https://x/v1", "k", None) is not None
