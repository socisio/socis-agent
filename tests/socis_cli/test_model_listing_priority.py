"""Curation decides what is SUITABLE; the live endpoint decides what is SERVED.

Neither source alone is correct, and using either alone shipped a bug:

  * models.dev lags retirements. It offered
    `qwen/qwen3-next-80b-a3b-instruct` for NVIDIA six weeks after NVIDIA
    stopped serving it, so the picker wrote a default that returned
    "HTTP 410 ... reached its end of life" on the first message.

  * The live endpoint is not a substitute. NVIDIA's /v1/models returns 80 IDs
    including `riva-translate-4b-instruct-v2` (translation) and
    `nemotron-3.5-content-safety` (a safety classifier). Both accept
    POST /chat/completions, so they survive a probe while being useless as an
    agent's model. Nous /models is worse — ~400 IDs with TTS, embeddings,
    rerankers and image/video generators.

Switching the picker from the first to the second traded one bug for the other.
The fix intersects them: take the curated list (filtered on tool_call=True with
noise patterns stripped), then remove anything the live endpoint no longer
lists.
"""

import pytest


def _load():
    """Load the pure helper without the module's interactive dependencies.

    An earlier version of this file tested a hand-written MIRROR of the
    logic. That was worthless as a guard: mutating the real implementation
    (removing the live-endpoint filter entirely) left every test green,
    because the tests never touched the code under test. The logic was
    extracted into a pure function specifically so these tests can exercise
    it directly.
    """
    import ast
    import pathlib

    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "intersect_catalog_with_live"
    )
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<x>", "exec"), ns)
    return ns["intersect_catalog_with_live"]


intersect_catalog_with_live = _load()


def _choose(curated, mdev, live, has_key):
    """Call the REAL helper; has_key gates the live listing as the caller does."""
    models, source, dropped = intersect_catalog_with_live(
        curated, mdev, live if has_key else []
    )
    return source, models


CURATED8 = [f"curated-{i}" for i in range(8)]


# ── the two real regressions ───────────────────────────────────────────────

def test_a_retired_model_is_dropped():
    """models.dev lists it; the live endpoint does not."""
    src, models = _choose(
        [], ["good-model", "qwen/qwen3-next-80b-a3b-instruct"], ["good-model"], True)
    assert src == "intersection"
    assert "qwen/qwen3-next-80b-a3b-instruct" not in models
    assert "good-model" in models


def test_non_chat_models_never_appear():
    """The live endpoint lists them and they pass a probe, but they are a
    translation model and a safety classifier."""
    live = [
        "nvidia/nemotron-3-super-120b-a12b",
        "nvidia/riva-translate-4b-instruct-v2",
        "nvidia/nemotron-3.5-content-safety",
    ]
    _, models = _choose([], ["nvidia/nemotron-3-super-120b-a12b"], live, True)
    assert models == ["nvidia/nemotron-3-super-120b-a12b"]
    assert not any("riva-translate" in m or "content-safety" in m for m in models)


def test_curated_order_is_preserved():
    """Curation encodes preference, not just eligibility."""
    _, models = _choose([], ["first", "second", "third"],
                        ["third", "second", "first"], True)
    assert models == ["first", "second", "third"]


def test_models_dev_entries_come_before_curated_extras():
    """Order matters: models.dev is the ranked source, and the curated list
    exists to APPEND anything models.dev has not picked up yet. Flipping the
    concatenation silently demotes the ranked entries to the tail."""
    models, source, _ = intersect_catalog_with_live(
        ["curated-only"], ["ranked-1", "ranked-2"],
        ["ranked-1", "ranked-2", "curated-only"],
    )
    assert source == "intersection"
    assert models == ["ranked-1", "ranked-2", "curated-only"], (
        "curated extras must follow the models.dev ranking, not precede it")


# ── it must never empty the picker ─────────────────────────────────────────

def test_no_id_overlap_falls_back_to_the_catalog():
    """Some endpoints use a different id scheme than models.dev. An empty
    picker is worse than an unfiltered one, and the availability guard still
    checks whatever the user picks."""
    src, models = _choose([], ["a", "b"], ["vendor/a", "vendor/b"], True)
    assert src == "catalog-unfiltered"
    assert models == ["a", "b"]


def test_an_unreachable_endpoint_falls_back_to_the_catalog():
    src, models = _choose(CURATED8, ["m1"], [], True)
    assert src == "models.dev"
    assert "m1" in models


def test_keyless_setup_is_unchanged():
    """No key means no live probe — the behaviour before any of this."""
    src, _ = _choose(CURATED8, ["m1"], ["m1"], False)
    assert src == "models.dev"


def test_a_provider_with_no_catalog_uses_the_raw_listing():
    """Last resort, and explicitly unfiltered — better than nothing for a
    provider models.dev has never heard of."""
    src, models = _choose([], [], ["l1", "l2"], True)
    assert src == "live-unfiltered"
    assert models == ["l1", "l2"]


@pytest.mark.parametrize("has_key", [True, False])
def test_empty_everywhere_does_not_crash(has_key):
    _, models = _choose([], [], [], has_key)
    assert models == []


# ── the output must say which source was used ──────────────────────────────

def test_the_source_is_named_in_the_output():
    """'Found 65 model(s) from models.dev registry' was the only clue the list
    was not the provider's own, and it took an HTTP 410 to notice. Each branch
    now says what it did — including when it could NOT filter."""
    import pathlib
    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    assert "cross-checked against its live endpoint" in src
    assert "no longer served" in src
    assert "live endpoint ids did not match" in src
    assert "unfiltered — no curated catalog" in src
