"""Lexical path admission. Not implemented in this snapshot."""

from __future__ import annotations

from typing import Any

from pathcage.parse import PathProbe
from pathcage.policy import Policy


def admit_path(probe: PathProbe, policy: Policy) -> dict[str, Any]:
    raise NotImplementedError("admit_path is not implemented in this snapshot")
