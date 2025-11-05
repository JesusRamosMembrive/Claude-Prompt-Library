# SPDX-License-Identifier: MIT
"""
Esquema de datos para reportar resultados del pipeline de linters.

El objetivo es proporcionar un payload rico en información y preparado para
visualizaciones en el frontend (tablas, tarjetas-resumen, charts).
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional


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
    metrics: Dict[str, float] = field(default_factory=dict)
    chart_data: ChartData = field(default_factory=ChartData)
    notes: List[str] = field(default_factory=list)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            field.name: _serialize_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        serialized: Dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(key, Enum):
                serialized[key.value] = _serialize_value(item)
            else:
                serialized[str(key)] = _serialize_value(item)
        return serialized
    return value


def report_to_dict(report: LintersReport) -> Dict[str, Any]:
    """Serializa un LintersReport a un diccionario listo para JSON."""
    data = _serialize_value(report)
    assert isinstance(data, dict)
    return data


def _parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def _safe_status(value: Any, default: CheckStatus = CheckStatus.PASS) -> CheckStatus:
    try:
        return CheckStatus(value)
    except Exception:
        return default


def _safe_severity(value: Any, default: Severity = Severity.MEDIUM) -> Severity:
    try:
        return Severity(value)
    except Exception:
        return default


def _parse_issue(data: Mapping[str, Any]) -> IssueDetail:
    return IssueDetail(
        message=str(data.get("message", "")),
        file=data.get("file"),
        line=data.get("line"),
        column=data.get("column"),
        code=data.get("code"),
        severity=_safe_severity(data.get("severity")),
        suggestion=data.get("suggestion"),
    )


def _parse_tool(data: Mapping[str, Any]) -> ToolRunResult:
    return ToolRunResult(
        key=str(data.get("key", "")),
        name=str(data.get("name", "")),
        status=_safe_status(data.get("status")),
        command=data.get("command"),
        duration_ms=data.get("duration_ms"),
        exit_code=data.get("exit_code"),
        version=data.get("version"),
        issues_found=int(data.get("issues_found", 0) or 0),
        issues_sample=[_parse_issue(item) for item in data.get("issues_sample", [])],
        stdout_excerpt=data.get("stdout_excerpt"),
        stderr_excerpt=data.get("stderr_excerpt"),
    )


def _parse_custom_rule(data: Mapping[str, Any]) -> CustomRuleResult:
    rule_status = _safe_status(data.get("status"))
    violations = [_parse_issue(item) for item in data.get("violations", [])]
    return CustomRuleResult(
        key=str(data.get("key", "")),
        name=str(data.get("name", "")),
        status=rule_status,
        description=str(data.get("description", "")),
        threshold=data.get("threshold"),
        violations=violations,
    )


def _parse_coverage(data: Mapping[str, Any]) -> CoverageSnapshot:
    return CoverageSnapshot(
        statement_coverage=data.get("statement_coverage"),
        branch_coverage=data.get("branch_coverage"),
        missing_lines=data.get("missing_lines"),
    )


def _parse_summary(data: Mapping[str, Any]) -> ReportSummary:
    return ReportSummary(
        overall_status=_safe_status(data.get("overall_status")),
        total_checks=int(data.get("total_checks", 0) or 0),
        checks_passed=int(data.get("checks_passed", 0) or 0),
        checks_warned=int(data.get("checks_warned", 0) or 0),
        checks_failed=int(data.get("checks_failed", 0) or 0),
        duration_ms=data.get("duration_ms"),
        files_scanned=data.get("files_scanned"),
        lines_scanned=data.get("lines_scanned"),
        issues_total=int(data.get("issues_total", 0) or 0),
        critical_issues=int(data.get("critical_issues", 0) or 0),
    )


def _parse_chart_data(data: Mapping[str, Any]) -> ChartData:
    issues_by_tool_raw = data.get("issues_by_tool", {})
    issues_by_severity_raw = data.get("issues_by_severity", {})
    issues_by_severity = {
        _safe_severity(key): int(value) for key, value in issues_by_severity_raw.items()
    }
    return ChartData(
        issues_by_tool={str(k): int(v) for k, v in issues_by_tool_raw.items()},
        issues_by_severity=issues_by_severity,
        top_offenders=[str(item) for item in data.get("top_offenders", [])],
    )


def report_from_dict(data: Mapping[str, Any]) -> LintersReport:
    summary = _parse_summary(data.get("summary", {}))
    tools = [_parse_tool(item) for item in data.get("tools", [])]
    custom_rules = [_parse_custom_rule(item) for item in data.get("custom_rules", [])]
    coverage_data = data.get("coverage")
    coverage = (
        _parse_coverage(coverage_data) if isinstance(coverage_data, Mapping) else None
    )
    chart_data = _parse_chart_data(data.get("chart_data", {}))

    metrics_raw = data.get("metrics", {})
    metrics: Dict[str, float] = {}
    for key, value in metrics_raw.items():
        if isinstance(value, (int, float)):
            metrics[str(key)] = float(value)
        else:
            try:
                metrics[str(key)] = float(value)
            except (TypeError, ValueError):
                continue

    notes = [str(item) for item in data.get("notes", [])]

    generated_at_raw = data.get("generated_at")
    generated_at = (
        _parse_datetime(generated_at_raw)
        if isinstance(generated_at_raw, str)
        else datetime.now()
    )

    return LintersReport(
        root_path=str(data.get("root_path", "")),
        generated_at=generated_at,
        summary=summary,
        tools=tools,
        custom_rules=custom_rules,
        coverage=coverage,
        metrics=metrics,
        chart_data=chart_data,
        notes=notes,
    )
