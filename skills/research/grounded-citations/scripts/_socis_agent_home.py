"""Resolve SOCIS_AGENT_HOME for standalone skill scripts.

Skill scripts may run outside the SOCIS process (system Python, nix env,
CI) where ``socis_agent_constants`` is not importable.  This module provides the
same ``get_socis_agent_home()`` contract without requiring it on ``sys.path``.

When ``socis_agent_constants`` IS available it is used directly so profile
resolution and any future enhancements are picked up automatically.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from socis_agent_constants import get_socis_agent_home as get_socis_agent_home
except (ModuleNotFoundError, ImportError):

    def get_socis_agent_home() -> Path:
        """Return the SOCIS home directory (default: ``~/.socis-agent``)."""
        val = os.environ.get("SOCIS_AGENT_HOME", "").strip()
        return Path(val) if val else Path.home() / ".socis-agent"
