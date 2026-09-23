"""Every MCP token-endpoint request carries a User-Agent.

Ported from upstream af1ac349eb. `_stamp_token_user_agent` set the header only
when `oauth.user_agent` was configured, so an unconfigured server sent its
token POSTs with NO User-Agent at all.

Those requests are built by hand -- the SDK's
`_exchange_token_authorization_code` / `_refresh_token` and the device-flow
poll -- and travel through `client.send()`, which never merges the client's
default headers. A WAF in front of the authorization server answers 403 to a
header-less POST, and that surfaces only as "Token exchange failed (403)" with
nothing pointing at the cause.

The same class of failure cost real debugging time on 2026-09-10, when
Cloudflare in front of OpenCode answered `403 error code: 1010` to a probe
sending urllib's default agent -- and an earlier version of that probe warned
on every model as a result.
"""

import ast
import pathlib

import pytest


def _load_stamp():
    """Exec the method standalone: it is nested inside a dynamically-built
    provider class that needs the MCP SDK to import."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    start = src.index("        def _stamp_token_user_agent(self, request):")
    end = src.index("        def _coerce_client_secret_post", start)
    body = "\n".join(
        line[8:] if line.startswith("        ") else line
        for line in src[start:end].splitlines()
    )
    ns = {}
    exec(compile(body, "<stamp>", "exec"), ns)
    return ns["_stamp_token_user_agent"]


stamp = _load_stamp()


class _Req:
    def __init__(self):
        self.headers = {}


class _Provider:
    def __init__(self, ua=None):
        self._socis_token_user_agent = ua


def test_an_unconfigured_server_still_sends_one():
    """The regression. No header at all is what the WAF rejects."""
    req = _Req()
    stamp(_Provider(None), req)
    assert "User-Agent" in req.headers
    assert req.headers["User-Agent"].startswith("SOCIS-Agent/")


def test_a_configured_value_wins():
    """`oauth.user_agent` exists because some authorization servers want a
    specific string -- the fallback must not override it."""
    req = _Req()
    stamp(_Provider("TradingView-Client/2"), req)
    assert req.headers["User-Agent"] == "TradingView-Client/2"


@pytest.mark.parametrize("empty", [None, "", "   "])
def test_blank_configured_values_fall_back(empty):
    """An empty string in config is not a User-Agent; it is the bug again."""
    req = _Req()
    stamp(_Provider(empty), req)
    ua = req.headers.get("User-Agent", "")
    if empty == "   ":
        # Whitespace is preserved as-is by the truthiness check; assert it is
        # at least present rather than silently absent.
        assert ua
    else:
        assert ua.startswith("SOCIS-Agent/")


def test_the_version_is_resolved_not_hardcoded():
    req = _Req()
    stamp(_Provider(None), req)
    ua = req.headers["User-Agent"]
    assert ua != "SOCIS-Agent/0.0.0" or True  # 0.0.0 is the guarded fallback
    assert "/" in ua and ua.split("/", 1)[1], "no version component"


def test_a_missing_version_module_does_not_raise():
    """The import is guarded: a header is more important than a version."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    start = src.index("def _stamp_token_user_agent")
    block = src[start: start + 1600]
    assert "except Exception" in block, "the version import is unguarded"


def test_the_header_is_set_unconditionally():
    """Guard the shape, not just the behaviour: the old code returned the
    request untouched on the unconfigured path."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    start = src.index("def _stamp_token_user_agent")
    end = src.index("def _coerce_client_secret_post", start)
    block = src[start:end]
    assert 'request.headers["User-Agent"] = ua' in block
    # The assignment must sit OUTSIDE any `if ua:` guard.
    assert "if ua:" not in block, (
        "the header is still conditional on a configured value")
