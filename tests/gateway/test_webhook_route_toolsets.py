"""Per-route webhook toolsets bind to the AUTHENTICATED route.

GHSA-2fmg-cjqm-hhrj, ported from upstream 9345c67854.

`toolsets_for_source` recovered the route by splitting the session chat_id
`webhook:{route}:{delivery_id}` on ":", while authentication used the exact URL
segment. A route named "build:external" therefore resolved to route "build" and
inherited its toolsets: a caller holding the weak route's HMAC secret got the
privileged sibling's terminal and file tools.

The fix keys on `source.user_id`, which _dispatch_agent_run stamps as exactly
`webhook:{route_name}` from the authenticated segment. No split at all --
delivery_id is caller-supplied (X-GitHub-Delivery, svix-id, X-Request-ID), so
any parse of chat_id, rsplit included, stays attacker-influenced.
"""

import pathlib

import pytest


class _Source:
    def __init__(self, user_id="", chat_id=""):
        self.user_id = user_id
        self.chat_id = chat_id


class _Adapter:
    """Just the method under test, with a routes table."""

    def __init__(self, routes):
        self._routes = routes

    toolsets_for_source = None  # bound below


def _load():
    src = pathlib.Path("gateway/platforms/webhook.py").read_text(encoding="utf-8")
    start = src.index("    def toolsets_for_source(self, source)")
    end = src.index("\n    # ---", start)
    body = "\n".join(
        line[4:] if line.startswith("    ") else line
        for line in src[start:end].splitlines()
    )
    import typing
    ns = {"Optional": typing.Optional, "List": typing.List}
    exec(compile(body, "<toolsets>", "exec"), ns)
    return ns["toolsets_for_source"]


_Adapter.toolsets_for_source = _load()

PRIVILEGED = {"toolsets": ["terminal", "file"]}
ROUTES = {"build": PRIVILEGED, "build:external": {}, "plain": {"toolsets": ["web"]}}


def test_a_colon_route_cannot_inherit_its_siblings_toolsets():
    """The advisory. 'build:external' split to 'build' and took terminal+file."""
    a = _Adapter(ROUTES)
    src = _Source(user_id="webhook:build:external",
                  chat_id="webhook:build:external:delivery-123")
    assert a.toolsets_for_source(src) is None


def test_a_crafted_delivery_id_cannot_name_another_route():
    """delivery_id is caller-supplied. Pins against a future rsplit."""
    a = _Adapter(ROUTES)
    src = _Source(user_id="webhook:plain", chat_id="webhook:plain:build")
    assert a.toolsets_for_source(src) == ["web"], "resolved by chat_id, not user_id"


def test_a_colon_route_gets_the_toolsets_it_configured():
    """Upstream notes the old code silently fell back to the platform default
    for a ':' route with no colliding sibling. It should get its own."""
    a = _Adapter({"build:external": {"toolsets": ["web"]}})
    src = _Source(user_id="webhook:build:external",
                  chat_id="webhook:build:external:d1")
    assert a.toolsets_for_source(src) == ["web"]


def test_a_plain_route_is_unchanged():
    a = _Adapter(ROUTES)
    src = _Source(user_id="webhook:build", chat_id="webhook:build:d1")
    assert a.toolsets_for_source(src) == ["terminal", "file"]


@pytest.mark.parametrize("user_id", ["", "slack:general", "webhook", "notwebhook:x"])
def test_a_non_webhook_source_is_refused(user_id):
    a = _Adapter(ROUTES)
    assert a.toolsets_for_source(_Source(user_id=user_id)) is None


def test_an_unknown_route_grants_nothing():
    a = _Adapter(ROUTES)
    assert a.toolsets_for_source(_Source(user_id="webhook:nope")) is None


def test_an_empty_toolsets_list_grants_nothing():
    """An empty list must not read as 'grant everything'."""
    a = _Adapter({"r": {"toolsets": []}})
    assert a.toolsets_for_source(_Source(user_id="webhook:r")) is None


def test_chat_id_is_never_parsed():
    """Guard the mechanism, not just the outcome: any chat_id parse is
    attacker-influenced, so the source must not contain one."""
    src = pathlib.Path("gateway/platforms/webhook.py").read_text(encoding="utf-8")
    start = src.index("def toolsets_for_source")
    block = src[start: src.index("\n    # ---", start)]
    code = "\n".join(l for l in block.splitlines() if not l.strip().startswith("#"))
    assert "chat_id" not in code.split('"""')[-1], (
        "chat_id is still parsed in the body")
    assert "user_id" in code
