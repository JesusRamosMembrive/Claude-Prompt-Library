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
]


async def linters_discovery_payload(root: Path) -> Dict[str, Any]:
    """
    Obtiene el payload listo para consumir por la API con información de linters.
    """
    return await discover_linters(root)
