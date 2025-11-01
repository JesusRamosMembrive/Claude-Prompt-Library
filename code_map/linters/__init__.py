# SPDX-License-Identifier: MIT
"""
Utilidades relacionadas con linters y verificaciones de calidad.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .discovery import discover_linters
from .report_schema import (
    ChartData,
    CheckStatus,
    CoverageSnapshot,
    CustomRuleResult,
    IssueDetail,
    LintersReport,
    ReportSummary,
    Severity,
    ToolRunResult,
    report_from_dict,
    report_to_dict,
)
from .pipeline import LinterRunOptions, run_linters_pipeline
from .storage import (
    StoredLintersReport,
    StoredNotification,
    get_latest_linters_report,
    get_linters_report,
    list_linters_reports,
    list_notifications,
    mark_notification_read,
    get_notification,
    record_linters_report,
    record_notification,
)

__all__ = [
    "discover_linters",
    "linters_discovery_payload",
    "LintersReport",
    "ReportSummary",
    "ToolRunResult",
    "CustomRuleResult",
    "CoverageSnapshot",
    "ChartData",
    "IssueDetail",
    "CheckStatus",
    "Severity",
    "report_to_dict",
    "report_from_dict",
    "run_linters_pipeline",
    "LinterRunOptions",
    "record_linters_report",
    "get_linters_report",
    "get_latest_linters_report",
    "list_linters_reports",
    "StoredLintersReport",
    "record_notification",
    "list_notifications",
    "mark_notification_read",
    "StoredNotification",
    "get_notification",
]


async def linters_discovery_payload(root: Path) -> Dict[str, Any]:
    """
    Obtiene el payload listo para consumir por la API con información de linters.
    """
    return await discover_linters(root)
