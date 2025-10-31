# SPDX-License-Identifier: MIT
"""Persistencia de reportes de linters y notificaciones en SQLite."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from ..settings import open_database
from .report_schema import (
    CheckStatus,
    LintersReport,
    Severity,
    report_from_dict,
    report_to_dict,
)


def _normalize_root(root: Optional[str | Path]) -> Optional[str]:
    if root is None:
        return None
    return str(Path(root).expanduser().resolve())


def _parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def _safe_check_status(value: Any) -> CheckStatus:
    try:
        return CheckStatus(value)
    except Exception:
        return CheckStatus.PASS


def _safe_severity(value: Any) -> Severity:
    try:
        return Severity(value)
    except Exception:
        return Severity.INFO


@dataclass(frozen=True)
class StoredLintersReport:
    """Representa un reporte almacenado con metadatos."""

    id: int
    generated_at: datetime
    root_path: str
    overall_status: CheckStatus
    issues_total: int
    critical_issues: int
    report: LintersReport


@dataclass(frozen=True)
class StoredNotification:
    """Representa una notificación persistida."""

    id: int
    created_at: datetime
    channel: str
    severity: Severity
    title: str
    message: str
    payload: Optional[Dict[str, Any]]
    root_path: Optional[str]
    read: bool


def record_linters_report(report: LintersReport, *, env: Optional[Mapping[str, str]] = None) -> int:
    """Inserta un nuevo reporte de linters en la base de datos."""
    payload = report_to_dict(report)
    summary = payload.get("summary", {})
    overall_status = summary.get("overall_status", CheckStatus.PASS.value)
    issues_total = int(summary.get("issues_total", 0) or 0)
    critical_issues = int(summary.get("critical_issues", 0) or 0)

    with open_database(env) as connection:
        cursor = connection.execute(
            """
            INSERT INTO linter_reports (generated_at, root_path, overall_status, issues_total, critical_issues, payload)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("generated_at"),
                _normalize_root(payload.get("root_path")) or "",
                overall_status,
                issues_total,
                critical_issues,
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def _row_to_report(row: Mapping[str, Any]) -> StoredLintersReport:
    payload = json.loads(row["payload"])
    return StoredLintersReport(
        id=int(row["id"]),
        generated_at=_parse_datetime(row["generated_at"]),
        root_path=row["root_path"],
        overall_status=_safe_check_status(row["overall_status"]),
        issues_total=int(row["issues_total"]),
        critical_issues=int(row["critical_issues"]),
        report=report_from_dict(payload),
    )


def get_linters_report(report_id: int, *, env: Optional[Mapping[str, str]] = None) -> Optional[StoredLintersReport]:
    """Obtiene un reporte por ID."""
    with open_database(env) as connection:
        row = connection.execute(
            """
            SELECT id, generated_at, root_path, overall_status, issues_total, critical_issues, payload
            FROM linter_reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_report(row)


def get_latest_linters_report(
    *,
    env: Optional[Mapping[str, str]] = None,
    root_path: Optional[str | Path] = None,
) -> Optional[StoredLintersReport]:
    """Obtiene el reporte más reciente, opcionalmente filtrado por root."""
    normalized_root = _normalize_root(root_path)
    with open_database(env) as connection:
        if normalized_root:
            row = connection.execute(
                """
                SELECT id, generated_at, root_path, overall_status, issues_total, critical_issues, payload
                FROM linter_reports
                WHERE root_path = ?
                ORDER BY generated_at DESC
                LIMIT 1
                """,
                (normalized_root,),
            ).fetchone()
        else:
            row = connection.execute(
                """
                SELECT id, generated_at, root_path, overall_status, issues_total, critical_issues, payload
                FROM linter_reports
                ORDER BY generated_at DESC
                LIMIT 1
                """
            ).fetchone()
    if row is None:
        return None
    return _row_to_report(row)


def list_linters_reports(
    *,
    limit: int = 20,
    offset: int = 0,
    env: Optional[Mapping[str, str]] = None,
    root_path: Optional[str | Path] = None,
) -> List[StoredLintersReport]:
    """Lista reportes ordenados por fecha de creación descendente."""
    normalized_root = _normalize_root(root_path)
    params: List[Any] = []
    query = (
        "SELECT id, generated_at, root_path, overall_status, issues_total, critical_issues, payload "
        "FROM linter_reports"
    )
    if normalized_root:
        query += " WHERE root_path = ?"
        params.append(normalized_root)
    query += " ORDER BY generated_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with open_database(env) as connection:
        rows = connection.execute(query, params).fetchall()

    return [_row_to_report(row) for row in rows]


def record_notification(
    *,
    channel: str,
    severity: Severity,
    title: str,
    message: str,
    root_path: Optional[str | Path] = None,
    payload: Optional[Dict[str, Any]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> int:
    """Almacena una notificación vinculada al ecosistema de linters."""
    created_at = datetime.now(timezone.utc).isoformat()
    serialized_payload = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) if payload else None
    normalized_root = _normalize_root(root_path)

    with open_database(env) as connection:
        cursor = connection.execute(
            """
            INSERT INTO notifications (created_at, channel, severity, title, message, payload, root_path, read)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                created_at,
                channel,
                severity.value,
                title,
                message,
                serialized_payload,
                normalized_root,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def _row_to_notification(row: Mapping[str, Any]) -> StoredNotification:
    payload_raw = row["payload"]
    payload = json.loads(payload_raw) if payload_raw else None
    return StoredNotification(
        id=int(row["id"]),
        created_at=_parse_datetime(row["created_at"]),
        channel=row["channel"],
        severity=_safe_severity(row["severity"]),
        title=row["title"],
        message=row["message"],
        payload=payload,
        root_path=row["root_path"],
        read=bool(row["read"]),
    )


def get_notification(
    notification_id: int,
    *,
    env: Optional[Mapping[str, str]] = None,
) -> Optional[StoredNotification]:
    """Obtiene una notificación por ID."""
    with open_database(env) as connection:
        row = connection.execute(
            """
            SELECT id, created_at, channel, severity, title, message, payload, root_path, read
            FROM notifications
            WHERE id = ?
            """,
            (notification_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_notification(row)


def list_notifications(
    *,
    limit: int = 50,
    unread_only: bool = False,
    env: Optional[Mapping[str, str]] = None,
    root_path: Optional[str | Path] = None,
) -> List[StoredNotification]:
    """Recupera notificaciones ordenadas por fecha descendente."""
    normalized_root = _normalize_root(root_path)
    params: List[Any] = []
    clauses: List[str] = []

    if unread_only:
        clauses.append("read = 0")
    if normalized_root:
        clauses.append("(root_path IS NULL OR root_path = ?)")
        params.append(normalized_root)

    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    query = (
        "SELECT id, created_at, channel, severity, title, message, payload, root_path, read "
        "FROM notifications"
        f"{where} ORDER BY created_at DESC LIMIT ?"
    )
    params.append(limit)

    with open_database(env) as connection:
        rows = connection.execute(query, params).fetchall()

    return [_row_to_notification(row) for row in rows]


def mark_notification_read(
    notification_id: int,
    *,
    env: Optional[Mapping[str, str]] = None,
    read: bool = True,
) -> bool:
    """Actualiza el estado de leído de una notificación."""
    with open_database(env) as connection:
        cursor = connection.execute(
            """
            UPDATE notifications
            SET read = ?
            WHERE id = ?
            """,
            (1 if read else 0, notification_id),
        )
        connection.commit()
        return cursor.rowcount > 0
