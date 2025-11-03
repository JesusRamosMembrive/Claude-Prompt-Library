# SPDX-License-Identifier: MIT
"""
Persistencia de resultados generados por el pipeline de insights de Ollama.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Optional

from ..settings import open_database


@dataclass(frozen=True)
class StoredInsight:
    id: int
    model: str
    message: str
    generated_at: datetime
    root_path: Optional[str]


def _ensure_table(env: Optional[Mapping[str, str]] = None) -> None:
    with open_database(env) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ollama_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                message TEXT NOT NULL,
                raw_payload TEXT,
                generated_at TEXT NOT NULL,
                root_path TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ollama_insights_generated_at
            ON ollama_insights(generated_at DESC)
            """
        )
        connection.commit()


def record_insight(
    *,
    model: str,
    message: str,
    raw: Mapping[str, object] | None = None,
    root_path: Optional[Path | str] = None,
    env: Optional[Mapping[str, str]] = None,
) -> int:
    """Persiste un insight generado automáticamente."""
    _ensure_table(env)
    generated_at = datetime.now(timezone.utc).isoformat()
    normalized_root = _normalize_root(root_path)
    payload = json.dumps(raw, ensure_ascii=False, separators=(",", ":")) if raw else None

    with open_database(env) as connection:
        cursor = connection.execute(
            """
            INSERT INTO ollama_insights (model, message, raw_payload, generated_at, root_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (model, message, payload, generated_at, normalized_root),
        )
        connection.commit()
        return int(cursor.lastrowid)


def list_insights(
    *,
    limit: int = 20,
    root_path: Optional[Path | str] = None,
    env: Optional[Mapping[str, str]] = None,
) -> list[StoredInsight]:
    """Recupera insights ordenados por fecha descendente."""
    _ensure_table(env)
    normalized_root = _normalize_root(root_path)
    params: list[object] = []
    where = ""
    if normalized_root:
        where = "WHERE (root_path IS NULL OR root_path = ?)"
        params.append(normalized_root)
    params.append(limit)

    with open_database(env) as connection:
        rows = connection.execute(
            f"""
            SELECT id, model, message, generated_at, root_path
            FROM ollama_insights
            {where}
            ORDER BY generated_at DESC
            LIMIT ?
            """,
            params,
        ).fetchall()

    insights: list[StoredInsight] = []
    for row in rows:
        generated_at = datetime.fromisoformat(row["generated_at"].replace("Z", "+00:00"))
        insights.append(
            StoredInsight(
                id=int(row["id"]),
                model=row["model"],
                message=row["message"],
                generated_at=generated_at,
                root_path=row["root_path"],
            )
        )
    return insights
def _normalize_root(root: Optional[Path | str]) -> Optional[str]:
    if root is None:
        return None
    value = Path(root).expanduser().resolve()
    return value.as_posix()
