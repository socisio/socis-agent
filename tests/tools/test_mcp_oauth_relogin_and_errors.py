"""MCP re-login keeps discovered metadata; token errors say WHY they failed.

Ported from upstream f44e73dab6 (#115329). Two defects:

1. `socis mcp login` cleared every OAuth file including `.meta.json` before
   probing. When the authorization server's metadata document cannot be
   re-fetched -- WAF-fronted split-host servers refuse the discovery request --
   the SDK falls back to `{mcp-origin}/authorize`, which does not exist. The
   cached document was the only thing announcing the real
   `authorization_endpoint`, so re-login broke a server that had worked.

2. `_handle_token_response` raised a bare `Token exchange failed (403)`. The
   non-2xx body carries no tokens and is the only thing distinguishing a WAF's
   HTML "Request blocked" from the issuer's `invalid_grant`. That exact
   ambiguity cost debugging time twice on 2026-09-10 and 11.

`socis mcp remove` is deliberately unchanged: deleting a server should delete
all of its state.
"""

import pathlib
import re

import pytest


# ── remove(keep_metadata=) ─────────────────────────────────────────────────

class _Storage:
    """Just enough of SOCISTokenStorage to exercise remove()."""

    def __init__(self, root):
        self.root = root

    def _tokens_path(self):        return self.root / "srv.json"
    def _client_info_path(self):   return self.root / "srv.client.json"
    def _meta_path(self):          return self.root / "srv.meta.json"
    def _cimd_rejected_path(self): return self.root / "srv.cimd-rejected"


def _load_remove():
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    start = src.index("    def remove(self, *, keep_metadata: bool = False) -> None:")
    end = src.index("\n    def ", start + 10)
    body = "\n".join(
        l[4:] if l.startswith("    ") else l for l in src[start:end].splitlines())
    ns = {}
    exec(compile(body, "<remove>", "exec"), ns)
    return ns["remove"]


_Storage.remove = _load_remove()


@pytest.fixture
def storage(tmp_path):
    s = _Storage(tmp_path)
    for p in (s._tokens_path(), s._client_info_path(),
              s._meta_path(), s._cimd_rejected_path()):
        p.write_text("x")
    return s


def test_relogin_keeps_the_metadata(storage):
    """The regression: the cached document was the only thing that knew the
    real authorize URL on a WAF-fronted server."""
    storage.remove(keep_metadata=True)
    assert storage._meta_path().exists()


def test_relogin_still_drops_the_grant_and_registration(storage):
    """Keeping metadata must not keep the credentials a re-login replaces."""
    storage.remove(keep_metadata=True)
    assert not storage._tokens_path().exists()
    assert not storage._client_info_path().exists()
    assert not storage._cimd_rejected_path().exists()


def test_full_removal_is_unchanged(storage):
    """Default behaviour: everything goes. `socis mcp remove` relies on it."""
    storage.remove()
    for p in (storage._tokens_path(), storage._client_info_path(),
              storage._meta_path(), storage._cimd_rejected_path()):
        assert not p.exists(), p.name


def test_the_relogin_path_uses_keep_metadata():
    src = pathlib.Path("socis_cli/mcp_config.py").read_text(encoding="utf-8")
    assert "SOCISTokenStorage(name).remove(keep_metadata=True)" in src
    assert "get_manager().evict(name)" in src


def test_server_removal_still_wipes_everything():
    """`socis mcp remove` deletes the server -- its metadata should go too.
    Only the RE-LOGIN path was changed."""
    src = pathlib.Path("socis_cli/mcp_config.py").read_text(encoding="utf-8")
    idx = src.index('_success(f"Removed \'{name}\' from config")')
    window = src[idx: idx + 600]
    assert "get_manager().remove(name)" in window


# ── the redacted body excerpt ──────────────────────────────────────────────

def _excerpt(raw):
    """Mirror of the excerpt shaping in _handle_token_response."""
    text = re.sub(r"<[^>]*>", " ", raw)
    return " ".join(text.split())[:200]


def test_a_waf_block_is_distinguishable():
    waf = ("<html><head><title>403</title></head><body>"
           "<h1>Request blocked.</h1><p>CloudFront</p></body></html>")
    assert "Request blocked" in _excerpt(waf)
    assert "<" not in _excerpt(waf), "tags must be stripped"


def test_an_issuer_rejection_is_distinguishable():
    assert "invalid_grant" in _excerpt(
        '{"error":"invalid_grant","error_description":"expired"}')


def test_the_excerpt_is_bounded():
    """A 5 MB error page must not become a 5 MB exception message."""
    assert len(_excerpt("x" * 5000)) == 200


def test_the_error_carries_the_excerpt():
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    idx = src.index("async def _handle_token_response")
    block = src[idx: src.index("async def _handle_refresh_response", idx)]
    assert '({response.status_code}){excerpt}' in block, (
        "the error is still a bare status code")


def test_the_excerpt_is_force_redacted():
    """The redactor can be switched off by config. A token-endpoint body can
    echo credentials, so this boundary must redact regardless."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    idx = src.index("async def _handle_token_response")
    block = src[idx: src.index("async def _handle_refresh_response", idx)]
    assert "redact_sensitive_text(text, force=True)" in block


def test_a_missing_redactor_omits_the_body_rather_than_leaking_it():
    """Fail closed: no redactor means no body, not a raw one."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    idx = src.index("async def _handle_token_response")
    block = src[idx: src.index("async def _handle_refresh_response", idx)]
    assert "[body omitted: redactor unavailable]" in block


def test_success_bodies_never_reach_the_excerpt():
    """2xx bodies can carry real tokens. The excerpt must only run after the
    2xx branch has returned."""
    src = pathlib.Path("tools/mcp_oauth.py").read_text(encoding="utf-8")
    idx = src.index("async def _handle_token_response")
    block = src[idx: src.index("async def _handle_refresh_response", idx)]
    success_return = block.index("                return\n")
    excerpt_read = block.index("await response.aread()")
    assert success_return < excerpt_read
