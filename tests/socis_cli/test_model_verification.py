"""A model is verified against the provider before it is saved.

No catalogue is trustworthy. models.dev offered
`qwen/qwen3-next-80b-a3b-instruct` for NVIDIA six weeks after NVIDIA stopped
serving it (HTTP 410 on the first message). Switching the picker to the
provider's own /v1/models did not fix it: NVIDIA lists 80 models of which the
mainstream ones return 410 or 404, and OpenCode Zen still lists
`ox-alpha-free` after removing it.

So a probe is the only reliable signal — but the FIRST version of that probe
was worse than useless, and these tests exist because of how it failed:

  * It sent no User-Agent, so Cloudflare in front of OpenCode answered
    `403 error code: 1010` for every model, dead or alive.
  * It condemned any 401/403, so `CreditsError` ("Insufficient balance" — the
    model is fine) and `MissingSessionID` (OpenCode Go needs a session header)
    both produced "will not serve this model", which is false.

A check that fires on conditions unrelated to the model is a check people
learn to click through. Every case below is a verbatim response captured from
a real provider during setup.
"""

import ast
import io
import json
import pathlib
import urllib.error
import urllib.request

import pytest


def _load():
    """Load the probe and its marker tables without the module's imports."""
    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    keep = [
        n for n in tree.body
        if (isinstance(n, ast.Assign) and any(
                getattr(t, "id", "").startswith(("_MODEL_DEAD", "_PROBE_INCONCL"))
                for t in n.targets))
        or (isinstance(n, ast.FunctionDef) and n.name == "verify_model_serves")
    ]
    ns = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "<probe>", "exec"), ns)
    return ns["verify_model_serves"]


verify_model_serves = _load()


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


# ── verdicts on real provider responses ────────────────────────────────────

DEAD = [
    ("NVIDIA retired (410)", 410,
     '{"detail":"The model \'q\' has reached its end of life on 2026-07-27T00:00:00Z"}'),
    ("NVIDIA not servable (404)", 404, "404 page not found"),
    ("Zen removed model (401 ModelError)", 401,
     '{"type":"error","error":{"type":"ModelError",'
     '"message":"Model ox-alpha-free is not supported"}}'),
]

ALIVE = [
    ("Zen no balance (401 CreditsError)", 401,
     '{"type":"error","error":{"type":"CreditsError",'
     '"message":"Insufficient balance. Manage your billing"}}'),
    ("Go needs a session (400 MissingSessionID)", 400,
     '{"type":"error","error":{"type":"MissingSessionID",'
     '"message":"Error from provider (Console)"}}'),
    ("Go contributor opt-in (403)", 403,
     '{"error":{"message":"This model collects data and requires explicit opt in"}}'),
    ("Cloudflare block (403 1010)", 403, "error code: 1010"),
    ("rate limited (429)", 429, "too many requests"),
]


@pytest.mark.parametrize("label,code,body", DEAD)
def test_a_dead_model_is_rejected(respond, label, code, body):
    respond(code, body)
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert not ok, f"{label} should have been rejected"
    assert str(code) in detail


@pytest.mark.parametrize("label,code,body", ALIVE)
def test_a_non_model_failure_does_not_condemn_the_model(respond, label, code, body):
    """These are account, transport or probe problems. Warning about them is
    false, and it is how a safeguard becomes noise."""
    respond(code, body)
    ok, _ = verify_model_serves("m", "k", "https://x/v1")
    assert ok, f"{label} must not be reported as a dead model"


@pytest.mark.parametrize("label,code,body", [
    ("Zen no balance", 401,
     '{"type":"error","error":{"type":"CreditsError",'
     '"message":"Insufficient balance. Manage your billing"}}'),
    ("Go needs a session", 400,
     '{"type":"error","error":{"type":"MissingSessionID",'
     '"message":"Error from provider (Console)"}}'),
])
def test_a_known_non_model_failure_says_so_explicitly(respond, label, code, body):
    """The verdict alone is not enough — the message has to explain WHY.

    Without the marker tables these still return ok=True via the catch-all
    ("could not classify"), so the verdict is safe either way. But the user
    reading it needs to know their balance is empty, not that the probe was
    confused. This test is what makes those tables load-bearing.
    """
    respond(code, body)
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert ok
    assert "not a model problem" in detail, (
        f"{label}: classified as unknown rather than a known non-model failure")


def test_a_served_model_passes(respond):
    respond(200)
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert ok and "200" in detail


def test_the_provider_message_survives_into_the_detail(respond):
    """The provider's own words are the useful part of the warning."""
    respond(410, '{"detail":"The model has reached its end of life on 2026-07-27"}')
    _, detail = verify_model_serves("m", "k", "https://x/v1")
    assert "end of life" in detail


def test_the_error_type_is_kept(respond):
    """'ModelError' vs 'CreditsError' is the whole signal, and it is not
    always inside the message string."""
    respond(401, '{"type":"error","error":{"type":"ModelError","message":"nope"}}')
    _, detail = verify_model_serves("m", "k", "https://x/v1")
    assert "ModelError" in detail


@pytest.mark.parametrize("exc", [OSError("refused"), TimeoutError("slow")])
def test_an_inconclusive_probe_does_not_block(respond, exc):
    respond(exc=exc)
    ok, detail = verify_model_serves("m", "k", "https://x/v1")
    assert ok and "could not verify" in detail


# ── request shape ──────────────────────────────────────────────────────────

def _capture(monkeypatch):
    seen = {}
    def fake(req, timeout=0):
        seen["url"] = req.full_url
        seen["headers"] = {k.lower(): v for k, v in req.header_items()}
        seen["body"] = json.loads(req.data.decode())
        class R:
            status = 200
            def __enter__(s): return s
            def __exit__(s, *a): return False
        return R()
    monkeypatch.setattr(urllib.request, "urlopen", fake)
    return seen


def test_a_user_agent_is_sent(monkeypatch):
    """Without one, Cloudflare answered 403/1010 for every model on OpenCode
    and the probe warned indiscriminately."""
    seen = _capture(monkeypatch)
    verify_model_serves("m", "k", "https://x/v1")
    assert seen["headers"].get("User-agent".lower(), "").startswith("socis-agent")


def test_the_url_is_built_from_base_url(monkeypatch):
    seen = _capture(monkeypatch)
    verify_model_serves("m", "k", "https://integrate.api.nvidia.com/v1/")
    assert seen["url"] == "https://integrate.api.nvidia.com/v1/chat/completions"


def test_the_request_is_cheap(monkeypatch):
    seen = _capture(monkeypatch)
    verify_model_serves("my-model", "k", "https://x/v1")
    assert seen["body"]["max_tokens"] == 1
    assert seen["body"]["model"] == "my-model"


# ── wiring ─────────────────────────────────────────────────────────────────

def test_the_probe_runs_before_the_save():
    """Source-level tripwire. The full flow needs the module's setup
    dependencies to exercise, so this checks statement order within the
    function that calls the probe — the file has 18 save sites, so a
    whole-file comparison would match an unrelated one."""
    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    tree = ast.parse(src)

    probe_fn = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(isinstance(i, ast.Call) and isinstance(i.func, ast.Name)
               and i.func.id == "verify_model_serves" for i in ast.walk(node)):
            probe_fn = node
            break
    assert probe_fn is not None, "no function calls verify_model_serves"

    names = [
        n.func.id for n in sorted(
            (n for n in ast.walk(probe_fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id in ("verify_model_serves", "_save_model_choice")),
            key=lambda n: n.lineno)
    ]
    assert names.index("verify_model_serves") < names.index("_save_model_choice"), (
        f"in {probe_fn.name}, the probe runs after the save — it is decoration")
    assert "if _probe_key and effective_base:" in src, "the probe guard was removed"


def test_an_unconfirmed_model_is_not_reported_as_verified():
    """Three outcomes, not two.

    A 401 CreditsError means the model exists and the balance is empty — the
    probe never confirmed it serves. Printing "✓ verified" there is a lie by
    omission: the user hits the same 401 on their first message with no
    forewarning, which is exactly what happened on OpenCode Zen.
    """
    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    block = src[src.index("_probe_key = existing_key"):]
    block = block[:block.index("_save_model_choice(selected)")]
    assert "could not be confirmed" in block, (
        "an unconfirmed probe still prints the verified tick")
    # The tick must be gated behind the unconfirmed branch, not the default.
    assert block.index("could not be confirmed") < block.index("verified:"), (
        "the unconfirmed case must be handled before the success message")
