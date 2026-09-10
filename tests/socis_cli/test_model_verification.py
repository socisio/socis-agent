"""A model is verified against the provider before it is saved.

No catalogue is trustworthy. models.dev offered
`qwen/qwen3-next-80b-a3b-instruct` for NVIDIA six weeks after NVIDIA stopped
serving it, so `socis model` wrote it as the default and the first message
returned HTTP 410. Switching the picker to the provider's own /v1/models did
not fix it: of NVIDIA's 80 listed models, `meta/llama-3.3-70b-instruct`
returned 410 (retired) and `z-ai/glm-5.3` returned 404 (not servable on that
endpoint). Only a handful — mostly Nemotron — actually answered.

Both catalogues are wrong in different ways, so the only reliable signal is a
one-token request. These tests pin what must and must not block a save.
"""

import io
import json
import urllib.error
import urllib.request

import pytest


def _load():
    """Load the probe without importing the module's heavy dependencies."""
    import ast
    import pathlib

    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "verify_model_serves"
    )
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<probe>", "exec"), ns)
    return ns["verify_model_serves"]


verify_model_serves = _load()


class _Err(urllib.error.HTTPError):
    def __init__(self, code, body=""):
        super().__init__("u", code, "e", {}, io.BytesIO(body.encode()))


@pytest.fixture
def respond(monkeypatch):
    """Install a fake urlopen returning a chosen status or raising."""
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


def test_a_served_model_passes(respond):
    respond(200)
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert ok and "200" in detail


def test_a_retired_model_is_rejected_with_the_reason(respond):
    """The NVIDIA 410 that started this."""
    respond(410, json.dumps(
        {"detail": "The model 'qwen/qwen3-next-80b-a3b-instruct' has reached "
                   "its end of life on 2026-07-27T00:00:00Z"}))
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert not ok
    assert "410" in detail
    assert "end of life" in detail, "the provider's own words are the useful part"


def test_a_model_not_servable_here_is_rejected(respond):
    """z-ai/glm-5.3 was listed by /v1/models and 404s on chat/completions."""
    respond(404, "404 page not found")
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert not ok and "404" in detail


def test_rate_limiting_does_not_condemn_the_model(respond):
    """429 says the account is throttled, not that the model is dead."""
    respond(429, "too many requests")
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert ok
    assert "429" in detail


@pytest.mark.parametrize("exc", [
    OSError("connection refused"),
    TimeoutError("timed out"),
])
def test_an_inconclusive_probe_does_not_block(respond, exc):
    """Refusing to save a working model because the setup machine's link
    blipped is worse than the problem this solves."""
    respond(exc=exc)
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert ok
    assert "could not verify" in detail


def test_the_url_is_built_from_base_url(monkeypatch):
    """base_url already ends in /v1; appending a second one 404s."""
    seen = {}

    def fake(req, timeout=0):
        seen["url"] = req.full_url
        class R:
            status = 200
            def __enter__(s): return s
            def __exit__(s, *a): return False
        return R()

    monkeypatch.setattr(urllib.request, "urlopen", fake)
    verify_model_serves("m", "k", "https://integrate.api.nvidia.com/v1/")
    assert seen["url"] == "https://integrate.api.nvidia.com/v1/chat/completions"


def test_the_request_is_cheap(monkeypatch):
    """One token. This runs during setup and must not cost anything real."""
    seen = {}

    def fake(req, timeout=0):
        seen["body"] = json.loads(req.data.decode())
        class R:
            status = 200
            def __enter__(s): return s
            def __exit__(s, *a): return False
        return R()

    monkeypatch.setattr(urllib.request, "urlopen", fake)
    verify_model_serves("my-model", "k", "https://x/v1")
    assert seen["body"]["max_tokens"] == 1
    assert seen["body"]["model"] == "my-model"


def test_the_save_path_calls_the_probe():
    """Guard the wiring, not just the helper.

    This is a SOURCE-TEXT check, and a weak one: it catches the call being
    deleted but not the guard being disabled, because the whole flow needs the
    module's setup dependencies to exercise for real. Treat it as a tripwire,
    not proof. The eight tests above are the real coverage.
    """
    import ast
    import pathlib

    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    tree = ast.parse(src)

    # Scope to the function that contains the probe. The file has 17
    # _save_model_choice call sites across the per-provider flows, so a
    # whole-file ordering check compares against an unrelated one.
    probe_fn = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                    and inner.func.id == "verify_model_serves"):
                probe_fn = node
                break
        if probe_fn:
            break
    assert probe_fn is not None, "no function calls verify_model_serves"

    calls = sorted(
        (n.lineno, n.func.id)
        for n in ast.walk(probe_fn)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id in ("verify_model_serves", "_save_model_choice")
    )
    names = [n for _, n in calls]
    assert names.index("verify_model_serves") < names.index("_save_model_choice"), (
        f"in {probe_fn.name}, the probe runs after the save — it is decoration")

    # And the guard must be a real condition, not disabled.
    assert "if _probe_key and effective_base:" in src, (
        "the probe guard was removed or disabled")
