"""The provider's own /v1/models wins over the models.dev catalog.

models.dev is a third-party registry and it lags retirements. It listed
`qwen/qwen3-next-80b-a3b-instruct` for NVIDIA six weeks after NVIDIA stopped
serving it, so `socis model` set that as the default and the very first
message came back:

    HTTP 410: The model 'qwen/qwen3-next-80b-a3b-instruct' has reached its
    end of life on 2026-07-27T00:00:00Z and is no longer available.

Confirmed against the live endpoint the same day: 80 models returned, the
retired one absent. The same lag produces 404 and 405 on other providers,
which reads as "switching providers is broken" when the switch itself worked.

A provider cannot list a model it will not serve, so when a key is present its
endpoint is authoritative. Keyless setup is unchanged: models.dev, then the
curated list.
"""

import pytest


def _choose(live, mdev, curated, has_key):
    """Mirror of the resolution order in model_setup_flows.py."""
    live = live if has_key else []
    if live:
        seen = {m.lower() for m in live}
        return "live", live + [m for m in curated if m.lower() not in seen]
    if mdev:
        seen = {m.lower() for m in mdev}
        return "models.dev", mdev + [m for m in curated if m.lower() not in seen]
    if curated and len(curated) >= 8:
        return "curated", curated
    return "probe", curated


CURATED = [f"curated-{i}" for i in range(8)]


def test_live_endpoint_wins_when_a_key_is_present():
    src, models = _choose(["live-a", "live-b"], ["retired-model"], CURATED, True)
    assert src == "live"
    assert "retired-model" not in models


def test_the_retired_model_cannot_be_offered():
    """The concrete regression: models.dev listed it, the endpoint did not."""
    src, models = _choose(
        ["meta/llama-3.3-70b-instruct"],
        ["qwen/qwen3-next-80b-a3b-instruct"],
        [],
        True,
    )
    assert "qwen/qwen3-next-80b-a3b-instruct" not in models


def test_curated_models_are_merged_into_the_live_list():
    """Some endpoints list only a subset until a model is first used."""
    _, models = _choose(["live-a"], [], ["extra-model"], True)
    assert "live-a" in models and "extra-model" in models


def test_no_duplicates_when_curated_overlaps_live():
    _, models = _choose(["shared"], [], ["Shared", "other"], True)
    assert [m.lower() for m in models].count("shared") == 1


def test_models_dev_is_used_when_the_endpoint_is_unreachable():
    """A network failure must not empty the picker."""
    src, models = _choose([], ["m1", "m2"], CURATED, True)
    assert src == "models.dev"
    assert models[:2] == ["m1", "m2"]


def test_keyless_setup_is_unchanged():
    """No key means no live probe — the previous behaviour, preserved."""
    src, _ = _choose(["live-a"], ["m1"], CURATED, False)
    assert src == "models.dev"


def test_curated_is_the_last_resort():
    src, models = _choose([], [], CURATED, False)
    assert src == "curated" and models == CURATED


@pytest.mark.parametrize("has_key", [True, False])
def test_an_empty_everything_does_not_crash(has_key):
    src, models = _choose([], [], [], has_key)
    assert models == []


def test_the_source_is_named_in_the_output():
    """The picker prints where the list came from.

    'Found 65 model(s) from models.dev registry' was the only clue that the
    list was not the provider's own, and it took a 410 to notice.
    """
    import pathlib
    src = pathlib.Path("socis_cli/model_setup_flows.py").read_text(encoding="utf-8")
    assert 'model(s) from {pconfig.name} API' in src
    assert "model(s) from models.dev registry" in src
