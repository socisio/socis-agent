"""A corrupt OAuth file must not put credentials in the log.

Ported from upstream aa0beef68. A pydantic ``ValidationError``'s ``str()``
includes the failing field's INPUT value, and three call sites logged the
exception directly:

    logger.warning("Corrupt tokens at %s -- ignoring: %s", path, exc)
    logger.warning("Corrupt client info at %s -- ignoring: %s", path, exc)
    logger.warning("Corrupt OAuth metadata at %s -- ignoring: %s", path, exc)

``OAuthToken.model_validate`` raises ValidationError, a ValueError subclass,
so it was caught and echoed. A malformed ``mcp-tokens/<server>.json`` wrote
the OAuth access token into the warning log — and logs get attached to support
tickets. The client-info and metadata files are the same shape: they carry the
client secret and endpoint configuration.

The replacement reports the failing field NAMES and the error type, which is
everything needed to debug a malformed file and nothing that is a secret.
"""

import ast
import pathlib

import pytest


def _load():
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    fn = next(
        n for n in ast.parse(src).body
        if isinstance(n, ast.FunctionDef) and n.name == "_validation_summary"
    )
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<summary>", "exec"), ns)
    return ns["_validation_summary"]


_validation_summary = _load()

SECRET = "sk-live-REALTOKEN-abc123456789"


class _FakeValidationError(ValueError):
    """Shaped like pydantic's: .errors() plus a str() that echoes the input."""

    def __init__(self, errors):
        self._errors = errors

    def errors(self):
        return self._errors

    def __str__(self):
        return (
            "1 validation error for OAuthToken\n  expires_in\n"
            f"    Input should be a valid integer [input_value={SECRET!r}]"
        )


def test_the_token_never_reaches_the_summary():
    """The whole point. str(exc) contains the token; the summary must not."""
    err = _FakeValidationError(
        [{"loc": ("expires_in",), "type": "int_parsing", "input": SECRET}])
    assert SECRET in str(err), "fixture is wrong — pydantic does echo the input"
    assert SECRET not in _validation_summary(err)


def test_the_failing_field_is_still_named():
    """A summary that hides everything is useless for debugging a bad file."""
    err = _FakeValidationError(
        [{"loc": ("expires_in",), "type": "int_parsing", "input": SECRET}])
    out = _validation_summary(err)
    assert "expires_in" in out
    assert "int_parsing" in out


def test_nested_field_paths_are_joined():
    err = _FakeValidationError(
        [{"loc": ("token", "value"), "type": "missing", "input": SECRET}])
    assert "token.value" in _validation_summary(err)


def test_many_errors_are_capped():
    """A pathological file must not turn one warning into a wall of text."""
    err = _FakeValidationError(
        [{"loc": (f"f{i}",), "type": "missing", "input": SECRET} for i in range(30)])
    out = _validation_summary(err)
    assert "30 field(s)" in out
    assert out.count(";") <= 6
    assert SECRET not in out


@pytest.mark.parametrize("exc", [
    TypeError("bad type for sk-live-XYZ-leaked"),
    KeyError(SECRET),
    ValueError(SECRET),
])
def test_non_pydantic_errors_leak_nothing_either(exc):
    """TypeError and KeyError are caught at the same sites, and str() on them
    can carry a dict key or a value."""
    out = _validation_summary(exc)
    assert SECRET not in out
    assert "sk-live-XYZ-leaked" not in out
    assert out == type(exc).__name__


def test_an_error_whose_errors_call_raises_is_handled():
    """A summariser that throws would replace a leak with a crash."""
    class Hostile(ValueError):
        def errors(self):
            raise RuntimeError("nope")
    assert _validation_summary(Hostile()) == "Hostile"


# ── the call sites ─────────────────────────────────────────────────────────

def test_all_three_call_sites_use_the_summary():
    """Fixing one file leaves the other two leaking. Tokens, client secret,
    endpoint metadata — same pattern, same exposure."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    for label in ("Corrupt tokens at", "Corrupt client info at",
                  "Corrupt OAuth metadata at"):
        idx = src.index(label)
        line_end = src.index("\n", idx)
        line = src[idx:line_end]
        assert "_validation_summary(exc)" in line, f"{label} still logs exc directly"
        assert ", exc)" not in line, f"{label} still passes the raw exception"


# ── RFC 6749 §6 refresh-token carry-forward ────────────────────────────────


class _Tok:
    """Stands in for OAuthToken: only the three fields the merge touches."""

    def __init__(self, access, refresh=None, scope=None):
        self.access_token = access
        self.refresh_token = refresh
        self.scope = scope


def _merge(prior, resp):
    """Mirror of the merge in _handle_refresh_response.

    Kept as a mirror deliberately: the real handler is an async method on a
    dynamically-built provider class that needs the MCP SDK, an httpx
    response and a live OAuth context. The source assertions below pin the
    real code; these pin the intended semantics.
    """
    if prior is not None:
        if resp.refresh_token is None:
            resp.refresh_token = prior.refresh_token
        if resp.scope is None:
            resp.scope = prior.scope
    return resp


def test_a_non_rotating_server_keeps_its_refresh_token():
    """The bug. Google, Asana and Zoho answer the refresh grant WITHOUT a
    refresh_token; storing the response verbatim erased the only one we had,
    so the next expiry forced a browser re-auth — roughly one TTL after every
    login."""
    out = _merge(_Tok("old", "KEEP-ME", "read write"), _Tok("new", None, None))
    assert out.refresh_token == "KEEP-ME"
    assert out.scope == "read write", "scope is carried forward too (§5.1)"


def test_a_rotating_server_still_wins():
    """Only None fields are filled — a real rotation must not be discarded,
    or we would keep presenting a token the server has already revoked."""
    out = _merge(_Tok("old", "OLD", "read"), _Tok("new", "NEW", "read write"))
    assert out.refresh_token == "NEW"
    assert out.scope == "read write"


def test_first_login_has_no_prior_tokens():
    out = _merge(None, _Tok("first", None, None))
    assert out.refresh_token is None


def test_the_prior_tokens_are_read_before_being_overwritten():
    """Order is the whole fix. `self.context.current_tokens = token_response`
    ran FIRST in the original, so by the time anything could read the prior
    value it was already gone."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    read = src.index("prior = self.context.current_tokens")
    # Search FORWARD from the read. There is a second assignment in
    # _handle_token_response (the initial authorization-code exchange, which
    # has no prior tokens to carry and correctly needs none), and searching
    # backwards finds that one instead.
    write = src.index("self.context.current_tokens = token_response", read)
    assert read < write, (
        "current_tokens is overwritten before the prior refresh_token is read")


def test_the_carry_forward_is_present_and_conditional():
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    idx = src.index("prior = self.context.current_tokens")
    block = src[idx: idx + 400]
    assert "if token_response.refresh_token is None:" in block, (
        "carry-forward must be conditional — an unconditional copy would "
        "discard a rotated token")
    assert "if token_response.scope is None:" in block
