"""shell.exec output is scrubbed before it leaves the gateway.

Ported from upstream a5c044d2e7. The TUI gateway's `shell.exec` RPC returned
stdout, stderr and exception text RAW. The child inherits the gateway's full
environment, so `printenv` or `env` through this RPC printed every configured
API key straight back to the client -- and any command echoing a token did the
same.

Three outputs, all scrubbed: stdout, stderr, and the exception message (which
can carry the command line, and the command line can carry a secret --
`curl -H "Authorization: Bearer ..."`).
"""

import pathlib

import pytest


def _load_scrub():
    src = pathlib.Path("tui_gateway/methods_tools.py").read_text(encoding="utf-8")
    start = src.index("def _scrub_shell_output(text: str) -> str:")
    end = src.index('@method("shell.exec")', start)
    ns = {}
    exec(compile(src[start:end], "<scrub>", "exec"), ns)
    return ns["_scrub_shell_output"]


scrub = _load_scrub()


def _real_redactor_available():
    try:
        from agent.redact import redact_sensitive_text  # noqa: F401
        return True
    except Exception:
        return False


needs_redactor = pytest.mark.skipif(
    not _real_redactor_available(), reason="agent.redact not importable here")


@needs_redactor
def test_printenv_output_is_scrubbed():
    """The concrete exposure: env vars printed through the RPC."""
    out = scrub("OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwx\nHOME=/Users/x\n")
    assert "sk-proj-abcdefghijklmnopqrstuvwx" not in out
    assert "HOME=/Users/x" in out, "non-secret output must survive"


@needs_redactor
def test_a_zhipu_key_is_scrubbed():
    """This fork has GLM_API_KEY configured; the Zhipu pattern was only added
    to the redactor in the same batch, so pin it here too."""
    key = "a" * 32 + ".ZabcdefghijklmnP"
    assert key not in scrub(f"GLM_API_KEY={key}")


def test_empty_output_is_returned_as_is():
    assert scrub("") == ""
    assert scrub(None) is None


def test_a_missing_redactor_withholds_rather_than_leaks(monkeypatch):
    """Fail closed. An import failure must not return a raw printenv."""
    import builtins

    real_import = builtins.__import__

    def fake(name, *a, **kw):
        if name == "agent.redact":
            raise ImportError("simulated")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake)
    assert scrub("OPENAI_API_KEY=sk-secret") == (
        "[output withheld: redactor unavailable]")


# ── wiring ─────────────────────────────────────────────────────────────────

def _shell_exec_block():
    src = pathlib.Path("tui_gateway/methods_tools.py").read_text(encoding="utf-8")
    start = src.index('@method("shell.exec")')
    return src[start: src.index("\ndef register(server)", start)]


def test_stdout_and_stderr_are_both_scrubbed():
    block = _shell_exec_block()
    assert '"stdout": _scrub_shell_output(r.stdout[-4000:])' in block
    assert '"stderr": _scrub_shell_output(r.stderr[-2000:])' in block


def test_the_exception_message_is_scrubbed():
    """`str(e)` can carry the command line and its secrets."""
    block = _shell_exec_block()
    assert "_err(rid, 5003, _scrub_shell_output(str(e)))" in block
    assert "_err(rid, 5003, str(e))" not in block


def test_output_is_truncated_before_redaction():
    """Slicing AFTER redaction can cut a mask in half and expose part of a
    secret at the boundary."""
    block = _shell_exec_block()
    assert "_scrub_shell_output(r.stdout[-4000:])" in block, (
        "truncate first, then redact")


def test_redaction_is_forced():
    src = pathlib.Path("tui_gateway/methods_tools.py").read_text(encoding="utf-8")
    start = src.index("def _scrub_shell_output")
    block = src[start: src.index('@method("shell.exec")', start)]
    assert "redact_sensitive_text(text, force=True)" in block
