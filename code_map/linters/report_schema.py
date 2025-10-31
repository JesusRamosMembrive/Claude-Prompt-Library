# SPDX-License-Identifier: MIT
"""
Esquema de datos para reportar resultados del pipeline de linters.

El objetivo es proporcionar un payload rico en información y preparado para
visualizaciones en el frontend (tablas, tarjetas-resumen, charts).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class CheckStatus(str, Enum):
    """Posibles estados de una verificación."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIPPED = "skipped"
    ERROR = "error"


class Severity(str, Enum):
    """Niveles de severidad para incidencias."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class IssueDetail:
    """
    Detalle de una incidencia reportada por un linter o regla personalizada.
    """

    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    code: Optional[str] = None
    severity: Severity = Severity.MEDIUM
    suggestion: Optional[str] = None


@dataclass(frozen=True)
class ToolRunResult:
    """
    Resultado de ejecutar una herramienta estándar (ruff, black, etc.).
    """

    key: str
    name: str
    status: CheckStatus
    command: Optional[str] = None
    duration_ms: Optional[int] = None
    exit_code: Optional[int] = None
    version: Optional[str] = None
    issues_found: int = 0
    issues_sample: List[IssueDetail] = field(default_factory=list)
    stdout_excerpt: Optional[str] = None
    stderr_excerpt: Optional[str] = None


@dataclass(frozen=True)
class CustomRuleResult:
    """
    Resultado de una regla personalizada (ej. longitud de archivo).
    """

    key: str
    name: str
    status: CheckStatus
    description: str
    threshold: Optional[int] = None
    violations: List[IssueDetail] = field(default_factory=list)


@dataclass(frozen=True)
class CoverageSnapshot:
    """
    Métricas de cobertura de tests (si aplica).
    """

    statement_coverage: Optional[float] = None
    branch_coverage: Optional[float] = None
    missing_lines: Optional[int] = None


@dataclass(frozen=True)
class ReportSummary:
    """
    Resumen agregando información para tarjetas en la UI.
    """

    overall_status: CheckStatus
    total_checks: int
    checks_passed: int
    checks_warned: int
    checks_failed: int
    duration_ms: Optional[int] = None
    files_scanned: Optional[int] = None
    lines_scanned: Optional[int] = None
    issues_total: int = 0
    critical_issues: int = 0


@dataclass(frozen=True)
class ChartData:
    """
    Datos preparados para visualizaciones rápidas en frontend.
    """

    issues_by_tool: Dict[str, int] = field(default_factory=dict)
    issues_by_severity: Dict[Severity, int] = field(default_factory=dict)
    top_offenders: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class LintersReport:
    """
    Payload completo para representar la salida del pipeline de linters.
    """

    root_path: str
    generated_at: datetime
    summary: ReportSummary
    tools: List[ToolRunResult]
    custom_rules: List[CustomRuleResult]
    coverage: Optional[CoverageSnapshot] = None
    metrics: Dict[str, int] = field(default_factory=dict)
    chart_data: ChartData = field(default_factory=ChartData)
    notes: List[str] = field(default_factory=list)
