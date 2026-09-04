"""Resolve SOCIS_AGENT_HOME for standalone skill scripts.

Skill scripts may run outside the SOCIS process (e.g. system Python,
nix env, CI) where ``socis_agent_constants`` is not importable.  This module
provides the same ``get_socis_agent_home()`` and ``display_socis_agent_home()``
contracts as ``socis_agent_constants`` without requiring it on ``sys.path``.

When ``socis_agent_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``socis_agent_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``SOCIS_AGENT_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from socis_agent_constants import display_socis_agent_home as display_socis_agent_home
    from socis_agent_constants import get_socis_agent_home as get_socis_agent_home
except (ModuleNotFoundError, ImportError):

    def get_socis_agent_home() -> Path:
        """Return the SOCIS home directory (default: ~/.socis-agent).

        Mirrors ``socis_agent_constants.get_socis_agent_home()``."""
        val = os.environ.get("SOCIS_AGENT_HOME", "").strip()
        return Path(val) if val else Path.home() / ".socis-agent"

    def display_socis_agent_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``socis_agent_constants.display_socis_agent_home()``."""
        home = get_socis_agent_home()
        try:
            return "~/" + home.relative_to(Path.home()).as_posix()
        except ValueError:
            return str(home)
