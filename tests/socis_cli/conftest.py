"""Fixtures shared across socis_cli kanban tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def all_assignees_spawnable(monkeypatch):
    """Pretend every assignee maps to a real SOCIS profile.

    Most dispatcher tests use synthetic assignees ("alice", "bob") that
    don't correspond to actual profile directories on disk. Without this
    patch, the dispatcher's profile-exists guard (PR #20105) routes
    those tasks into ``skipped_nonspawnable`` instead of spawning, which
    would break tests that assert spawn behavior.
    """
    from socis_cli import profiles
    monkeypatch.setattr(profiles, "profile_exists", lambda name: True)


@pytest.fixture(autouse=True)
def _suppress_concurrent_socis_gate(request, monkeypatch):
    """Default ``_detect_concurrent_socis_instances`` to ``[]`` for every test.

    The Windows update path now refuses to proceed when another
    ``socis.exe`` is detected (issue #26670). On a developer's Windows
    machine running the test suite via ``socis`` itself, this would
    flag the running agent as a concurrent instance and abort every
    ``cmd_update`` test. Tests that want to exercise the gate explicitly
    re-patch ``_detect_concurrent_socis_instances`` with their own
    return value — autouse here gives a clean default without touching
    the rest of the suite.

    Tests that need to call the REAL function (e.g. unit tests for the
    helper itself) opt out with ``@pytest.mark.real_concurrent_gate``.
    """
    if request.node.get_closest_marker("real_concurrent_gate"):
        return
    try:
        from socis_cli import main as _cli_main
    except Exception:
        return
    # raising=False: under pytest's per-test spawn isolation, a concurrent
    # xdist worker importing a module that transitively touches socis_cli.main
    # can briefly expose a partially-initialized module object here — one where
    # _detect_concurrent_socis_instances isn't defined yet. A bare setattr
    # would raise AttributeError and error the (unrelated) test. The attribute
    # always exists once main.py finishes importing, so a no-op when it's
    # transiently absent is the correct, race-free default.
    monkeypatch.setattr(
        _cli_main,
        "_detect_concurrent_socis_instances",
        lambda *_a, **_k: [],
        raising=False,
    )


@pytest.fixture
def no_macos_host_mutation(monkeypatch):
    """Neutralise the macOS-only steps ``socis update`` takes on a real Mac.

    The end-to-end update tests already stub the Windows service helpers
    (``_pause_windows_gateways_for_update``) and the systemd ones
    (``supports_systemd_services``, ``find_gateway_pids``). They missed
    macOS, so on a developer's Mac ``cmd_update`` went on to:

    * restart launchd gateways — the tests' fake subprocess answered
      "loaded" but printed no PID, so the restart verified as failed and
      ``cmd_update`` exited 1 (11 tests failed on every Mac, passing only
      on Linux CI, whose macOS job runs just ``-m macos_only``);
    * run the REAL cua-driver installer, gated only on
      ``shutil.which("cua-driver")`` — stopped merely because /Applications
      was not writable;
    * stage copies of the interpreter into the REAL ``.venv/bin`` via
      ``ensure_tcc_anchor()``, which is called without a project root.

    Opt in with ``pytestmark = pytest.mark.usefixtures(
    "no_macos_host_mutation")``. Not autouse: the functions are tested
    directly elsewhere (test_install_cua_driver, test_macos_tcc_anchor,
    test_update_launchd_*), and a blanket stub would hollow those out.
    """
    from socis_cli import update_cmd

    monkeypatch.setattr(update_cmd, "_restart_macos_launchd_gateways",
                        lambda *a, **k: None)
    try:
        from socis_cli import tools_config
        monkeypatch.setattr(tools_config, "install_cua_driver", lambda *a, **k: None)
    except ImportError:
        pass
    try:
        from socis_cli import macos_tcc_anchor
        monkeypatch.setattr(macos_tcc_anchor, "ensure_tcc_anchor", lambda *a, **k: None)
    except ImportError:
        pass
