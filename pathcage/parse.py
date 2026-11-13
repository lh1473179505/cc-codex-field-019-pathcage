"""Candidate path loader and lexical probe used by inspect."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class PathError(ValueError):
    pass


@dataclass
class PathProbe:
    raw: str
    raw_bytes: int
    has_control: bool
    has_backslash: bool
    has_nul: bool
    percent_count: int
    decoded: str | None
    segments: list[str] | None
    looks_absolute: bool
    looks_windows: bool
    has_dotdot_segment: bool
    raw_meta: dict[str, Any] = field(default_factory=dict)


def _strip_one_newline(data: bytes) -> bytes:
    if data.endswith(b"\n"):
        return data[:-1]
    return data


def load_path(path: str | Path) -> bytes:
    try:
        data = Path(path).read_bytes()
    except Exception as exc:
        raise PathError(f"failed to read path file: {exc}") from exc
    return _strip_one_newline(data)


def probe_path(raw_bytes: bytes) -> PathProbe:
    try:
        raw = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw = raw_bytes.decode("utf-8", "replace")
    has_nul = b"\x00" in raw_bytes or "\x00" in raw
    has_control = has_nul or any((ord(ch) < 32 or ord(ch) == 127) for ch in raw)
    has_backslash = "\\" in raw
    percent_count = raw.count("%")
    decoded: str | None = None
    segments: list[str] | None = None
    looks_absolute = False
    looks_windows = False
    has_dotdot = False
    # Best-effort decode for inspect only; the engine must implement the fail-closed rules.
    try:
        buf: list[bytes] | None = []
        i = 0
        s = raw
        while i < len(s):
            if s[i] == "%":
                if i + 2 < len(s) and all(c in "0123456789abcdefABCDEF" for c in s[i + 1 : i + 3]):
                    buf.append(bytes([int(s[i + 1 : i + 3], 16)]))
                    i += 3
                    continue
                buf = None
                break
            buf.append(s[i].encode("utf-8"))
            i += 1
        if buf is not None:
            decoded = b"".join(buf).decode("utf-8")
    except Exception:
        decoded = None
    if decoded is not None:
        looks_absolute = decoded.startswith("/")
        looks_windows = len(decoded) >= 2 and decoded[0].isalpha() and decoded[1] in ":"
        segs = [p for p in decoded.split("/") if p != ""]
        segments = segs
        has_dotdot = ".." in segs
    return PathProbe(
        raw=raw,
        raw_bytes=len(raw_bytes),
        has_control=has_control,
        has_backslash=has_backslash,
        has_nul=has_nul,
        percent_count=percent_count,
        decoded=decoded,
        segments=segments,
        looks_absolute=looks_absolute,
        looks_windows=looks_windows,
        has_dotdot_segment=has_dotdot,
    )


def probe_to_dict(probe: PathProbe) -> dict[str, Any]:
    return {
        "raw": probe.raw if "\x00" not in probe.raw else probe.raw.replace("\x00", "\u0000"),
        "raw_bytes": probe.raw_bytes,
        "has_control": probe.has_control,
        "has_backslash": probe.has_backslash,
        "has_nul": probe.has_nul,
        "percent_count": probe.percent_count,
        "decoded": probe.decoded,
        "segments": probe.segments,
        "looks_absolute": probe.looks_absolute,
        "looks_windows": probe.looks_windows,
        "has_dotdot_segment": probe.has_dotdot_segment,
    }
