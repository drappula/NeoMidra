# SteaMidra - Steam game setup and manifest tool (SFF)
# Copyright (c) 2025-2026 Midrag (https://github.com/Midrags)
#
# This file is part of SteaMidra.
#
# SteaMidra is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SteaMidra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SteaMidra.  If not, see <https://www.gnu.org/licenses/>.
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_KEY = "bootstrapperinhibitall"


def _atomic_write(target: Path, payload: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(target)


def get_state(steam_path: Path) -> str:
    """'blocked', 'unblocked', or 'unknown' (no file / no such line)."""
    cfg = steam_path / "steam.cfg"
    try:
        if not cfg.is_file():
            return "unknown"
        for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, val = stripped.partition("=")
            if key.strip().lower() != _KEY:
                continue
            value = val.strip().lower()
            if value in ("enable", "enabled", "true", "1", "yes"):
                return "blocked"
            if value in ("false", "0", "no", "disable", "disabled"):
                return "unblocked"
            return "unknown"
        return "unknown"
    except OSError as exc:
        logger.warning("steam_updates get_state failed: %s", exc)
        return "unknown"


def _set_inhibit(steam_path: Path, value: str) -> None:
    """Rewrite the BootStrapperInhibitAll line, keeping every other line."""
    target = steam_path / "steam.cfg"
    lines = []
    if target.is_file():
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    out = []
    replaced = False
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            key, _, _ = stripped.partition("=")
            if key.strip().lower() == _KEY:
                out.append(f"BootStrapperInhibitAll={value}")
                replaced = True
                continue
        out.append(line)
    if not replaced:
        out.append(f"BootStrapperInhibitAll={value}")
    _atomic_write(target, "\n".join(out).rstrip() + "\n")


def block_updates(steam_path: Path) -> None:
    _set_inhibit(steam_path, "Enable")


def unblock_updates(steam_path: Path) -> None:
    _set_inhibit(steam_path, "False")
