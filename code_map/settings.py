# SPDX-License-Identifier: MIT
"""
Persistencia y modelo de configuración de la aplicación.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
import sqlite3
from pathlib import Path
from typing import Iterable, Mapping, Optional, Tuple
import logging

from .constants import META_DIR_NAME
from .scanner import DEFAULT_EXCLUDED_DIRS

ENV_ROOT_PATH = "CODE_MAP_ROOT"
ENV_INCLUDE_DOCSTRINGS = "CODE_MAP_INCLUDE_DOCSTRINGS"
ENV_DB_PATH = "CODE_MAP_DB_PATH"
ENV_DISABLE_LINTERS = "CODE_MAP_DISABLE_LINTERS"
SETTINGS_VERSION = 2
DB_FILENAME = "state.db"


def _normalize_exclusions(additional: Iterable[str] | None = None) -> Tuple[str, ...]:
    """Combina las exclusiones por defecto con exclusiones adicionales."""
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
    return tuple(sorted(base))


@dataclass(frozen=True)
class AppSettings:
    """Define la configuración de la aplicación."""
    root_path: Path
    exclude_dirs: Tuple[str, ...] = field(default_factory=tuple)
    include_docstrings: bool = True
    ollama_insights_enabled: bool = False

    def to_payload(self) -> dict:
        """Convierte la configuración a un diccionario serializable."""
        return {
            "root_path": str(self.root_path),
            "exclude_dirs": list(self.exclude_dirs),
            "include_docstrings": self.include_docstrings,
            "ollama_insights_enabled": self.ollama_insights_enabled,
            "version": SETTINGS_VERSION,
        }

    def with_updates(
        self,
        *,
        root_path: Path | None = None,
        include_docstrings: bool | None = None,
        exclude_dirs: Iterable[str] | None = None,
        ollama_insights_enabled: bool | None = None,
    ) -> "AppSettings":
        """Crea una nueva instancia de AppSettings con actualizaciones."""
        return AppSettings(
            root_path=(root_path or self.root_path).expanduser().resolve(),
            exclude_dirs=_normalize_exclusions(exclude_dirs) if exclude_dirs is not None else self.exclude_dirs,
            include_docstrings=(
                include_docstrings
                if include_docstrings is not None
                else self.include_docstrings
            ),
            ollama_insights_enabled=(
                ollama_insights_enabled
                if ollama_insights_enabled is not None
                else self.ollama_insights_enabled
            ),
        )

def _parse_env_flag(raw: Optional[str]) -> Optional[bool]:
    """Parsea una variable de entorno como un booleano."""
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return None


def _coerce_path(value: Optional[str | Path]) -> Optional[Path]:
    """Convierte un valor a una ruta absoluta."""
    if value is None:
        return None
    return Path(value).expanduser().resolve()


def database_path(env: Optional[Mapping[str, str]] = None) -> Path:
    """Obtiene la ruta del archivo SQLite para estado global."""
    effective_env: Mapping[str, str] = env or os.environ
    custom_path = effective_env.get(ENV_DB_PATH)
    if custom_path:
        return Path(custom_path).expanduser().resolve()
    return Path.home() / META_DIR_NAME / DB_FILENAME


def open_database(env: Optional[Mapping[str, str]] = None) -> sqlite3.Connection:
    """Abre una conexión a la base de datos y asegura el esquema."""
    path = database_path(env)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    _ensure_db_schema(connection)
    return connection


def _ensure_db_schema(connection: sqlite3.Connection) -> None:
    """Crea la tabla de configuración si no existe."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            root_path TEXT NOT NULL,
            exclude_dirs TEXT NOT NULL,
            include_docstrings INTEGER NOT NULL,
            ollama_insights_enabled INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS linter_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generated_at TEXT NOT NULL,
            root_path TEXT NOT NULL,
            overall_status TEXT NOT NULL,
            issues_total INTEGER NOT NULL DEFAULT 0,
            critical_issues INTEGER NOT NULL DEFAULT 0,
            payload TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_linter_reports_generated_at
            ON linter_reports(generated_at DESC)
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            channel TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            payload TEXT,
            root_path TEXT,
            read INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_notifications_created_at
            ON notifications(created_at DESC)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_notifications_root_path
            ON notifications(root_path)
        """
    )

    # Asegurar columna ollama_insights_enabled en instalaciones existentes.
    cursor = connection.execute("PRAGMA table_info(app_settings)")
    columns = {row["name"] for row in cursor.fetchall()}
    if "ollama_insights_enabled" not in columns:
        try:
            connection.execute(
                "ALTER TABLE app_settings ADD COLUMN ollama_insights_enabled INTEGER NOT NULL DEFAULT 0"
            )
            connection.commit()
        except sqlite3.OperationalError:
            pass

    connection.commit()


def _load_settings_from_db(
    db_path: Path,
    default_root: Path,
    *,
    default_include_docstrings: bool = True,
) -> Optional[AppSettings]:
    """Carga la configuración desde la base de datos SQLite si existe."""
    with open_database(env={ENV_DB_PATH: str(db_path)}) as connection:
        insights_supported = True
        try:
            cursor = connection.execute(
                "SELECT root_path, exclude_dirs, include_docstrings, ollama_insights_enabled FROM app_settings WHERE id = 1"
            )
        except sqlite3.OperationalError:
            insights_supported = False
            cursor = connection.execute(
                "SELECT root_path, exclude_dirs, include_docstrings FROM app_settings WHERE id = 1"
            )
        row = cursor.fetchone()
        if row is None:
            return None

        stored_root_raw = row["root_path"]
        stored_root = Path(stored_root_raw).expanduser().resolve() if stored_root_raw else default_root
        excludes_raw = row["exclude_dirs"] or "[]"
        try:
            data = json.loads(excludes_raw)
        except json.JSONDecodeError:
            data = []

        include_flag = bool(row["include_docstrings"]) if row["include_docstrings"] is not None else default_include_docstrings
        if insights_supported and "ollama_insights_enabled" in row.keys():
            insights_raw = row["ollama_insights_enabled"]
            insights_flag = bool(insights_raw) if insights_raw is not None else False
        else:
            insights_flag = False
        effective_root = stored_root if stored_root.exists() else default_root

        return AppSettings(
            root_path=effective_root,
            exclude_dirs=_normalize_exclusions(data),
            include_docstrings=include_flag,
            ollama_insights_enabled=insights_flag,
        )


def _save_settings_to_db(db_path: Path, settings: AppSettings) -> None:
    """Persiste la configuración actual en SQLite."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with open_database(env={ENV_DB_PATH: str(db_path)}) as connection:
        cursor = connection.execute("PRAGMA table_info(app_settings)")
        columns = {row["name"] for row in cursor.fetchall()}
        has_insights_column = "ollama_insights_enabled" in columns

        if not has_insights_column:
            try:
                connection.execute(
                    "ALTER TABLE app_settings ADD COLUMN ollama_insights_enabled INTEGER NOT NULL DEFAULT 0"
                )
                connection.commit()
                has_insights_column = True
            except sqlite3.OperationalError:
                has_insights_column = False

        if has_insights_column:
            connection.execute(
                """
                INSERT INTO app_settings (id, root_path, exclude_dirs, include_docstrings, ollama_insights_enabled, updated_at)
                VALUES (1, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                ON CONFLICT(id) DO UPDATE SET
                    root_path = excluded.root_path,
                    exclude_dirs = excluded.exclude_dirs,
                    include_docstrings = excluded.include_docstrings,
                    ollama_insights_enabled = excluded.ollama_insights_enabled,
                    updated_at = excluded.updated_at
                """,
                (
                    str(settings.root_path),
                    json.dumps(list(settings.exclude_dirs)),
                    1 if settings.include_docstrings else 0,
                    1 if settings.ollama_insights_enabled else 0,
                ),
            )
        else:
            connection.execute(
                """
                INSERT INTO app_settings (id, root_path, exclude_dirs, include_docstrings, updated_at)
                VALUES (1, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                ON CONFLICT(id) DO UPDATE SET
                    root_path = excluded.root_path,
                    exclude_dirs = excluded.exclude_dirs,
                    include_docstrings = excluded.include_docstrings,
                    updated_at = excluded.updated_at
                """,
                (
                    str(settings.root_path),
                    json.dumps(list(settings.exclude_dirs)),
                    1 if settings.include_docstrings else 0,
                ),
            )
        connection.commit()


def load_settings(
    *,
    root_override: Optional[str | Path] = None,
    env: Optional[Mapping[str, str]] = None,
) -> AppSettings:
    """Carga la configuración de la aplicación desde el disco y el entorno."""
    effective_env: Mapping[str, str] = env or os.environ

    env_root = _coerce_path(effective_env.get(ENV_ROOT_PATH))
    override_path = _coerce_path(root_override)
    base_root = override_path or env_root or Path.cwd().expanduser().resolve()

    include_flag = _parse_env_flag(effective_env.get(ENV_INCLUDE_DOCSTRINGS))
    default_include = include_flag if include_flag is not None else True

    db_path = database_path(effective_env)
    settings = _load_settings_from_db(
        db_path,
        base_root,
        default_include_docstrings=default_include,
    )

    if settings is None:
        settings = AppSettings(
            root_path=base_root,
            exclude_dirs=_normalize_exclusions(),
            include_docstrings=default_include,
            ollama_insights_enabled=False,
        )
        _save_settings_to_db(db_path, settings)

    if (override_path or env_root) and settings.root_path != base_root:
        settings = settings.with_updates(root_path=base_root)

    if include_flag is not None and settings.include_docstrings != include_flag:
        settings = settings.with_updates(include_docstrings=include_flag)

    return settings


def save_settings(settings: AppSettings, *, env: Optional[Mapping[str, str]] = None) -> None:
    """Guarda la configuración en el disco."""
    db_path = database_path(env)
    try:
        _save_settings_to_db(db_path, settings)
    except sqlite3.OperationalError as exc:
        logger.warning("No se pudo guardar la configuración en %s: %s", db_path, exc)
logger = logging.getLogger(__name__)
