"""Dotted `sk-` bodies and unprefixed Zhipu keys are redacted.

Ported from upstream 7b57cda6d9 and its follow-up aebc71d78c. Two gaps:

1. The `sk-` body was `[A-Za-z0-9_-]{10,}`, which STOPS at a dot. Provider keys
   with dot-delimited bodies (Alibaba `sk-sp-…`, `sk-ws-…`) had everything after
   the first dot left in the clear.

2. Zhipu / Z.ai keys are an UNPREFIXED `id.secret` form, so no prefix pattern
   could match them at all. A GLM_API_KEY / ZAI_API_KEY value passed straight
   through the redactor — and this fork has one configured.

Both fixes have a trap, which is why the upstream follow-up exists:

- A wider dotted matcher ate its own output. tool_executor redacts to
  `sk-pro...EFGH`, build_tool_preview redacts again, and the `...` was consumed
  so the mask collapsed to `***`. The body must never span `..`.
- A loose Zhipu matcher (`[A-Za-z0-9]{32,40}\\.[A-Za-z0-9]{6,}`) matched
  content-hash filenames: `<sha>.bundle`, `<md5>.sqlite3`, `<36-alnum>.example`.
"""

import pathlib
import re

import pytest


def _pattern(name):
    """Pull a compiled pattern's source out of the module without importing it
    (agent.redact pulls in the whole agent package)."""
    src = pathlib.Path("agent/redact.py").read_text(encoding="utf-8")
    if name == "dotted":
        m = re.search(r'r"(sk-\[A-Za-z0-9_-\]\(\?:[^"]+)"', src)
        assert m, "the dotted sk- pattern is gone"
        return re.compile(r"(?<![A-Za-z0-9_-])(" + m.group(1) + r")(?![A-Za-z0-9_-])")
    m = re.search(r'_ZHIPU_API_KEY_RE = re\.compile\(\s*r"([^"]+)"', src)
    assert m, "the Zhipu pattern is gone"
    return re.compile(m.group(1))


DOTTED = _pattern("dotted")
ZHIPU = _pattern("zhipu")


# ── dotted sk- bodies ──────────────────────────────────────────────────────

@pytest.mark.parametrize("text,secret", [
    ("key=sk-sp-abcdef123.ghijkl456xyz done", "sk-sp-abcdef123.ghijkl456xyz"),
    ("sk-ws-aaaaaaaaaa.bbbbbbbbbb", "sk-ws-aaaaaaaaaa.bbbbbbbbbb"),
])
def test_a_dotted_body_is_matched_whole(text, secret):
    """The old body stopped at the dot, leaking the suffix."""
    m = DOTTED.search(text)
    assert m and m.group(1) == secret


def test_a_display_mask_survives_a_second_pass():
    """THE regression in upstream's first attempt: a wider matcher consumed
    the `...` in `sk-pro...EFGH` and collapsed an already-masked value to
    `***`. Redaction runs twice on tool previews."""
    assert DOTTED.search("sk-pro...EFGH") is None


def test_trailing_punctuation_is_not_consumed():
    """`Use sk-abcdefghijk.` — the full stop belongs to the sentence."""
    m = DOTTED.search("use sk-abcdefghijk. next")
    assert m and m.group(1) == "sk-abcdefghijk"


def test_an_undotted_key_still_matches():
    m = DOTTED.search("sk-abcdefghijklmnop")
    assert m and m.group(1) == "sk-abcdefghijklmnop"


def test_a_short_token_is_not_matched():
    """The 10-char floor stops `sk-` prose fragments becoming secrets."""
    assert DOTTED.search("sk-abc") is None


# ── unprefixed Zhipu keys ──────────────────────────────────────────────────

def test_a_zhipu_key_is_matched():
    key = "a" * 32 + ".ZabcdefghijklmnP"
    assert ZHIPU.search(f"GLM_API_KEY={key}")


@pytest.mark.parametrize("filename", [
    "0" * 40 + ".bundle",
    "b" * 32 + ".sqlite3",
    "c" * 32 + ".example",
])
def test_content_hash_filenames_are_not_secrets(filename):
    """Upstream's loose matcher flagged these. A redactor that masks filenames
    makes its own output untrustworthy."""
    assert ZHIPU.search(filename) is None


def test_the_id_must_be_lowercase_hex():
    """32 alphanumerics is a filename shape; 32 lowercase hex is the provider's."""
    assert ZHIPU.search("A" * 32 + ".abcdefghijklmnop") is None


def test_the_secret_must_be_long_enough():
    assert ZHIPU.search("a" * 32 + ".short") is None


# ── wiring ─────────────────────────────────────────────────────────────────

def test_the_zhipu_pattern_is_actually_applied():
    """A compiled pattern nobody calls redacts nothing."""
    src = pathlib.Path("agent/redact.py").read_text(encoding="utf-8")
    assert "_ZHIPU_API_KEY_RE.sub(" in src, "the Zhipu pattern is never applied"
    # It must respect the same file_read masking mode as the prefix pass.
    idx = src.index("_ZHIPU_API_KEY_RE.sub(")
    window = src[idx - 260: idx]
    assert "_mask_token_nonreusable if file_read else _mask_token" in window
