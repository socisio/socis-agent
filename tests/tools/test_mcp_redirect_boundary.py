"""Cross-origin redirects do not carry MCP credentials.

Ported from upstream a8afb3b567 (#115155). The boundary NEVER WORKED: it was
an httpx response event hook reading `response.next_request`, which httpx does
not populate until AFTER response hooks run. The guard always early-returned,
so `strict_redirect_headers` silently did nothing -- while its own docstring
cited Agent Plugins v1 spec 7.2.1.

Two exposures, for as long as the option existed:

  * configured headers (`X-API-Key` and the like) forwarded to any redirect
    target on the Streamable HTTP client
  * the preflight probe followed redirects with no boundary at all, leaking
    those headers before the handshake had even started

The fix overrides `_build_redirect_request` on an AsyncClient subclass -- the
only seam that sees exclusively redirect follow-ups. A REQUEST hook would also
fire on the OAuth flow's token and registration requests to a different-origin
authorization server and strip their credentials, breaking auth to fix a leak.
"""

import pathlib

import pytest


# ── a minimal httpx stand-in ───────────────────────────────────────────────

class _URL:
    def __init__(self, scheme, host, port):
        self.scheme, self.host, self.port = scheme, host, port


class _Headers(dict):
    def pop(self, key, default=None):
        for k in list(self):
            if k.lower() == str(key).lower():
                return super().pop(k)
        return default

    def __contains__(self, key):
        return any(k.lower() == str(key).lower() for k in self)

    def __delitem__(self, key):
        for k in list(self):
            if k.lower() == str(key).lower():
                super().__delitem__(k)
                return
        raise KeyError(key)


class _Request:
    def __init__(self, url, headers):
        self.url, self.headers = url, _Headers(headers)


class _BaseAsyncClient:
    """Stands in for httpx.AsyncClient: returns the follow-up unguarded."""

    _next = None

    def _build_redirect_request(self, request, response):
        return _Request(self._next.url, dict(self._next.headers))


class _Httpx:
    AsyncClient = _BaseAsyncClient
    URL = _URL


def _load_factory():
    src = pathlib.Path("tools/mcp_tool.py").read_text(encoding="utf-8")
    start = src.index("def _make_redirect_header_stripper(")
    end = src.index("def _format_connect_error", start)
    ns = {}
    exec(compile(src[start:end], "<stripper>", "exec"), ns)
    return ns["_make_redirect_header_stripper"]


make = _load_factory()
ORIGIN = _URL("https", "mcp.example.com", 443)
HEADERS = {"Authorization": "Bearer tok", "X-API-Key": "SECRET", "Accept": "*/*"}


def _follow(target, *, strict, configured=("x-api-key",)):
    cls = make(_Httpx, ORIGIN, strict=strict,
               configured_header_names=set(configured))
    client = cls()
    client._next = _Request(target, HEADERS)
    return client._build_redirect_request(None, None).headers


# ── the boundary ───────────────────────────────────────────────────────────

def test_authorization_is_stripped_cross_origin():
    out = _follow(_URL("https", "evil.example", 443), strict=False)
    assert "authorization" not in out


def test_configured_headers_are_stripped_under_strict():
    """The exposure. X-API-Key went to the redirect target."""
    out = _follow(_URL("https", "evil.example", 443), strict=True)
    assert "x-api-key" not in out
    assert "authorization" not in out


def test_configured_headers_survive_when_not_strict():
    """Documented compat contract: non-strict forwards them."""
    out = _follow(_URL("https", "evil.example", 443), strict=False)
    assert out.get("X-API-Key") == "SECRET"


def test_same_origin_keeps_everything():
    out = _follow(_URL("https", "mcp.example.com", 443), strict=True)
    assert out.get("Authorization") == "Bearer tok"
    assert out.get("X-API-Key") == "SECRET"


@pytest.mark.parametrize("target", [
    _URL("http", "mcp.example.com", 443),    # scheme differs
    _URL("https", "mcp.example.com", 8443),  # port differs
    _URL("https", "sub.mcp.example.com", 443),  # host differs
])
def test_any_origin_component_triggers_the_boundary(target):
    assert "authorization" not in _follow(target, strict=True)


def test_unconfigured_headers_are_never_stripped():
    """Only headers the package configured are in scope."""
    out = _follow(_URL("https", "evil.example", 443), strict=True)
    assert out.get("Accept") == "*/*"


# ── the mechanism, not just the behaviour ──────────────────────────────────

def test_the_guard_is_not_a_response_event_hook():
    """A response hook cannot work: httpx populates next_request only after
    response hooks run, so the old guard always early-returned.

    Checks the AST for an actual `.next_request` attribute access rather than
    searching the text -- the function's own docstring names the attribute
    while explaining why it is gone.
    """
    import ast

    src = pathlib.Path("tools/mcp_tool.py").read_text(encoding="utf-8")
    start = src.index("def _make_redirect_header_stripper(")
    block = src[start: src.index("def _format_connect_error", start)]
    tree = ast.parse(block)

    accesses = [
        n.attr for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr == "next_request"
    ]
    assert not accesses, (
        "still reading response.next_request -- that is the broken seam")

    overrides = [
        n.name for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_build_redirect_request"
    ]
    assert overrides, "the redirect seam is not overridden"


def test_the_transport_client_uses_the_subclass():
    """Building the subclass and then instantiating httpx.AsyncClient would
    leave the boundary unenforced."""
    src = pathlib.Path("tools/mcp_tool.py").read_text(encoding="utf-8")
    assert "async with _client_cls(**client_kwargs) as http_client:" in src


def test_the_preflight_probe_enforces_the_boundary():
    """The probe followed redirects with no boundary at all."""
    src = pathlib.Path("tools/mcp_tool.py").read_text(encoding="utf-8")
    assert "_probe_client_cls" in src
    assert "async with _probe_client_cls(**client_kwargs) as client:" in src


def test_the_probe_receives_the_config_flag():
    """A boundary defaulting to non-strict on the probe would be a no-op for
    the packages that asked for it."""
    src = pathlib.Path("tools/mcp_tool.py").read_text(encoding="utf-8")
    assert "strict_redirect_headers: bool = False" in src
    assert 'strict_redirect_headers=bool(\n                            config.get("strict_redirect_headers"))' in src
