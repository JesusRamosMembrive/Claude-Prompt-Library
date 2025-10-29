# SPDX-License-Identifier: MIT
"""
Persistencia y modelo de configuración de la aplicación.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

from .scanner import DEFAULT_EXCLUDED_DIRS

SETTINGS_FILENAME = "code-map-settings.json"


def _default_exclusions(additional: Iterable[str] | None = None) -> List[str]:
    base = set(DEFAULT_EXCLUDED_DIRS)
    if additional:
        base.update(additional)
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
            exclude_dirs=list(exclude_dirs) if exclude_dirs is not None else self.exclude_dirs,
            include_docstrings=(
                include_docstrings
                if include_docstrings is not None
                else self.include_docstrings
            ),
        )


def settings_storage_path(root_path: Path) -> Path:
    root = root_path.expanduser().resolve()
    return root / ".cache" / SETTINGS_FILENAME


def load_settings(
    default_root: Path,
    *,
    default_include_docstrings: bool = True,
) -> AppSettings:
    default_root = default_root.expanduser().resolve()
    path = settings_storage_path(default_root)

    if not path.exists():
        return AppSettings(
            root_path=default_root,
            exclude_dirs=_default_exclusions(),
            include_docstrings=default_include_docstrings,
        )

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return AppSettings(
            root_path=default_root,
            exclude_dirs=_default_exclusions(),
            include_docstrings=default_include_docstrings,
        )

    stored_root = Path(data.get("root_path", default_root)).expanduser().resolve()
    exclude_dirs = data.get("exclude_dirs", [])
    include_docstrings = data.get("include_docstrings", default_include_docstrings)

    return AppSettings(
        root_path=stored_root if stored_root.exists() else default_root,
        exclude_dirs=_default_exclusions(exclude_dirs),
        include_docstrings=bool(include_docstrings),
    )


def save_settings(settings: AppSettings) -> None:
    path = settings_storage_path(settings.root_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(settings.to_payload(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
