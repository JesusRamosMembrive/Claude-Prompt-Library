# SPDX-License-Identifier: MIT
"""
Persistencia y modelo de configuración de la aplicación.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

from .constants import META_DIR_NAME
from .scanner import DEFAULT_EXCLUDED_DIRS

SETTINGS_FILENAME = "code-map-settings.json"
ENV_ROOT_PATH = "CODE_MAP_ROOT"
ENV_INCLUDE_DOCSTRINGS = "CODE_MAP_INCLUDE_DOCSTRINGS"


def _normalize_exclusions(additional: Iterable[str] | None = None) -> List[str]:
    base = set(DEFAULT_EXCLUDED_DIRS)
    if additional:
        for item in additional:
            if not item:
                continue
            normalized = item.strip()
            if not normalized:
                continue
            if normalized.startswith("/"):
                continue
            base.add(normalized)
    return sorted(base)


@dataclass
class AppSettings:
    root_path: Path
    exclude_dirs: List[str] = field(default_factory=list)
    include_docstrings: bool = True

    def to_payload(self) -> dict:
        return {
            "root_path": str(self.root_path),
            "exclude_dirs": self.exclude_dirs,
            "include_docstrings": self.include_docstrings,
            "version": 1,
        }

    def with_updates(
        self,
        *,
        root_path: Path | None = None,
        include_docstrings: bool | None = None,
        exclude_dirs: Iterable[str] | None = None,
    ) -> "AppSettings":
        return AppSettings(
            root_path=(root_path or self.root_path).expanduser().resolve(),
            exclude_dirs=_normalize_exclusions(exclude_dirs) if exclude_dirs is not None else self.exclude_dirs,
            include_docstrings=(
                include_docstrings
                if include_docstrings is not None
                else self.include_docstrings
            ),
        )


def settings_storage_path(root_path: Path) -> Path:
    root = root_path.expanduser().resolve()
    return root / META_DIR_NAME / SETTINGS_FILENAME


def _load_settings_from_disk(
    default_root: Path,
    *,
    default_include_docstrings: bool = True,
) -> AppSettings:
    default_root = default_root.expanduser().resolve()
    path = settings_storage_path(default_root)

    if not path.exists():
        return AppSettings(
            root_path=default_root,
            exclude_dirs=_normalize_exclusions(),
            include_docstrings=default_include_docstrings,
        )

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return AppSettings(
            root_path=default_root,
            exclude_dirs=_normalize_exclusions(),
            include_docstrings=default_include_docstrings,
        )

    stored_root = Path(data.get("root_path", default_root)).expanduser().resolve()
    exclude_dirs = data.get("exclude_dirs", [])
    include_docstrings = data.get("include_docstrings")
    include_value = (
        bool(include_docstrings)
        if include_docstrings is not None
        else default_include_docstrings
    )

    return AppSettings(
        root_path=stored_root if stored_root.exists() else default_root,
        exclude_dirs=_normalize_exclusions(exclude_dirs),
        include_docstrings=include_value,
    )


def _parse_env_flag(raw: Optional[str]) -> Optional[bool]:
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return None


def _coerce_path(value: Optional[str | Path]) -> Optional[Path]:
    if value is None:
        return None
    return Path(value).expanduser().resolve()


def load_settings(
    *,
    root_override: Optional[str | Path] = None,
    env: Optional[Mapping[str, str]] = None,
) -> AppSettings:
    effective_env: Mapping[str, str] = env or os.environ

    env_root = _coerce_path(effective_env.get(ENV_ROOT_PATH))
    override_path = _coerce_path(root_override)
    base_root = override_path or env_root or Path.cwd().expanduser().resolve()

    include_flag = _parse_env_flag(effective_env.get(ENV_INCLUDE_DOCSTRINGS))
    default_include = include_flag if include_flag is not None else True

    settings = _load_settings_from_disk(
        base_root,
        default_include_docstrings=default_include,
    )

    if (override_path or env_root) and settings.root_path != base_root:
        settings = settings.with_updates(root_path=base_root)

    if include_flag is not None and settings.include_docstrings != include_flag:
        settings = settings.with_updates(include_docstrings=include_flag)

    return settings


def save_settings(settings: AppSettings) -> None:
    path = settings_storage_path(settings.root_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(settings.to_payload(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
