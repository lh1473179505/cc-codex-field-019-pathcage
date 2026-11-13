"""Path admission policy loader."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class PolicyError(ValueError):
    pass


@dataclass
class Policy:
    jail_root: str
    max_bytes: int
    allow_absolute: bool
    raw: dict[str, Any] = field(default_factory=dict)


def load_policy(path: str | Path) -> Policy:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        raise PolicyError(f"failed to read policy: {exc}") from exc
    if not isinstance(data, dict):
        raise PolicyError("policy must be a JSON object")
    jail = data.get("jail_root")
    if not isinstance(jail, str) or not jail.startswith("/") or "\\" in jail or "\x00" in jail:
        raise PolicyError("jail_root must be an absolute POSIX path")
    if jail != "/" and jail.endswith("/"):
        raise PolicyError("jail_root must not have a trailing slash")
    max_bytes = data.get("max_bytes", 256)
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 1:
        raise PolicyError("max_bytes must be a positive integer")
    allow_abs = data.get("allow_absolute", False)
    if not isinstance(allow_abs, bool):
        raise PolicyError("allow_absolute must be a boolean")
    return Policy(jail_root=jail, max_bytes=max_bytes, allow_absolute=allow_abs, raw=data)
