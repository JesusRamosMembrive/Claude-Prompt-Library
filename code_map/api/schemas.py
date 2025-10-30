# SPDX-License-Identifier: MIT
"""
Esquemas Pydantic para serializar respuestas de la API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List, Optional

from pydantic import BaseModel, Field

from ..models import AnalysisError, FileSummary, ProjectTreeNode, SymbolInfo, SymbolKind
from ..state import AppState
from ..stage_toolkit import AgentSelection


class HealthResponse(BaseModel):
    """Respuesta del endpoint de health."""
    status: str = "ok"


class AnalysisErrorSchema(BaseModel):
    """Esquema para un error de análisis."""
    message: str
    lineno: Optional[int] = None
    col_offset: Optional[int] = None


class SymbolSchema(BaseModel):
    """Esquema para un símbolo de código."""
    name: str
    kind: SymbolKind
    lineno: int
    parent: Optional[str] = None
    path: Optional[str] = None
    docstring: Optional[str] = None


class FileSummarySchema(BaseModel):
    """Esquema para el resumen de un archivo."""
    path: str
    modified_at: Optional[datetime] = None
    symbols: List[SymbolSchema] = Field(default_factory=list)
    errors: List[AnalysisErrorSchema] = Field(default_factory=list)


class TreeNodeSchema(BaseModel):
    """Esquema para un nodo del árbol de archivos."""
    name: str
    path: str
    is_dir: bool
    children: List["TreeNodeSchema"] = Field(default_factory=list)
    symbols: Optional[List[SymbolSchema]] = None
    errors: Optional[List[AnalysisErrorSchema]] = None
    modified_at: Optional[datetime] = None


TreeNodeSchema.model_rebuild()


class SearchResultsSchema(BaseModel):
    """Esquema para los resultados de una búsqueda."""
    results: List[SymbolSchema]


class RescanResponse(BaseModel):
    """Respuesta del endpoint de rescan."""
    files: int


class ChangeNotification(BaseModel):
    """Notificación de cambios en el sistema de archivos."""
    updated: List[str]
    deleted: List[str]


class SettingsResponse(BaseModel):
    """Respuesta del endpoint de settings."""
    root_path: str
    absolute_root: str
    exclude_dirs: List[str]
    include_docstrings: bool
    watcher_active: bool


class SettingsUpdateRequest(BaseModel):
    """Petición para actualizar los settings."""
    root_path: Optional[str] = None
    include_docstrings: Optional[bool] = None
    exclude_dirs: Optional[List[str]] = None


class SettingsUpdateResponse(BaseModel):
    """Respuesta de la actualización de settings."""
    updated: List[str]
    settings: SettingsResponse


class AnalyzerCapabilitySchema(BaseModel):
    """Esquema para una capacidad del analizador."""
    key: str
    description: str
    extensions: List[str]
    available: bool
    dependency: Optional[str] = None
    error: Optional[str] = None
    degraded_extensions: List[str] = Field(default_factory=list)


class StatusResponse(BaseModel):
    """Respuesta del endpoint de status."""
    root_path: str
    absolute_root: str
    watcher_active: bool
    include_docstrings: bool
    last_full_scan: Optional[datetime]
    last_event_batch: Optional[datetime]
    files_indexed: int
    symbols_indexed: int
    pending_events: int
    capabilities: List[AnalyzerCapabilitySchema] = Field(default_factory=list)


class PreviewResponse(BaseModel):
    """Respuesta del endpoint de preview."""
    content: str
    content_type: str


class OptionalFilesStatus(BaseModel):
    """Estado opcional (archivos recomendados pero no obligatorios)."""
    expected: List[str]
    present: List[str]
    missing: List[str]


class AgentInstallStatus(BaseModel):
    """Estado de instalación para un agente (Claude o Codex)."""
    expected: List[str]
    present: List[str]
    missing: List[str]
    installed: bool
    optional: Optional[OptionalFilesStatus] = None


class DocsStatus(BaseModel):
    """Estado de los documentos de referencia."""
    expected: List[str]
    present: List[str]
    missing: List[str]
    complete: bool


class StageDetectionStatus(BaseModel):
    """Resultado de la detección automática de etapa."""
    available: bool
    recommended_stage: Optional[int] = None
    confidence: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    metrics: Optional[dict] = None
    error: Optional[str] = None
    checked_at: Optional[datetime] = None


class StageStatusResponse(BaseModel):
    """Payload completo con el estado stage-aware del proyecto."""
    root_path: str
    claude: AgentInstallStatus
    codex: AgentInstallStatus
    docs: DocsStatus
    detection: StageDetectionStatus


class StageInitRequest(BaseModel):
    """Petición para inicializar los assets stage-aware."""
    agents: AgentSelection = Field(default="both")


class StageInitResponse(BaseModel):
    """Respuesta tras ejecutar init_project.py."""
    success: bool
    exit_code: int
    command: List[str]
    stdout: str
    stderr: str
    status: StageStatusResponse


class ClassGraphNode(BaseModel):
    """Nodo del grafo de clases."""
    id: str
    name: str
    module: str
    file: str


class ClassGraphEdge(BaseModel):
    """Arista del grafo de clases."""
    source: str
    target: str
    type: str
    internal: bool
    raw_target: str


class ClassGraphStats(BaseModel):
    """Métricas del grafo generado."""
    nodes: int
    edges: int
    edges_by_type: Dict[str, int]


class ClassGraphResponse(BaseModel):
    """Respuesta completa del grafo de clases."""
    nodes: List[ClassGraphNode]
    edges: List[ClassGraphEdge]
    stats: ClassGraphStats


def serialize_symbol(symbol: SymbolInfo, state: AppState, *, include_path: bool = True) -> SymbolSchema:
    """Serializa un objeto SymbolInfo a un SymbolSchema."""
    path = state.to_relative(symbol.path) if include_path else None
    return SymbolSchema(
        name=symbol.name,
        kind=symbol.kind,
        lineno=symbol.lineno,
        parent=symbol.parent,
        path=path,
        docstring=symbol.docstring,
    )


def serialize_error(error: AnalysisError) -> AnalysisErrorSchema:
    """Serializa un objeto AnalysisError a un AnalysisErrorSchema."""
    return AnalysisErrorSchema(
        message=error.message,
        lineno=error.lineno,
        col_offset=error.col_offset,
    )


def serialize_summary(summary: FileSummary, state: AppState) -> FileSummarySchema:
    """Serializa un objeto FileSummary a un FileSummarySchema."""
    symbols = [serialize_symbol(symbol, state, include_path=False) for symbol in summary.symbols]
    errors = [serialize_error(error) for error in summary.errors]
    return FileSummarySchema(
        path=state.to_relative(summary.path),
        modified_at=summary.modified_at,
        symbols=symbols,
        errors=errors,
    )


def serialize_tree(node: ProjectTreeNode, state: AppState) -> TreeNodeSchema:
    """Serializa un objeto ProjectTreeNode a un TreeNodeSchema."""
    children = [
        serialize_tree(child, state)
        for child in sorted(node.children.values(), key=lambda n: n.name)
    ]
    summary = node.file_summary
    symbols = None
    errors = None
    modified_at = None
    if summary:
        symbols = [serialize_symbol(symbol, state, include_path=False) for symbol in summary.symbols]
        errors = [serialize_error(error) for error in summary.errors]
        modified_at = summary.modified_at

    return TreeNodeSchema(
        name=node.name,
        path=state.to_relative(node.path),
        is_dir=node.is_dir,
        children=children,
        symbols=symbols,
        errors=errors,
        modified_at=modified_at,
    )


def serialize_search_results(symbols: Iterable[SymbolInfo], state: AppState) -> SearchResultsSchema:
    """Serializa una lista de SymbolInfo a un SearchResultsSchema."""
    return SearchResultsSchema(results=[serialize_symbol(symbol, state) for symbol in symbols])


def serialize_settings(state: AppState) -> SettingsResponse:
    """Serializa el estado de la configuración a un SettingsResponse."""
    payload = state.get_settings_payload()
    return SettingsResponse(**payload)


def serialize_status(state: AppState) -> StatusResponse:
    """Serializa el estado de la aplicación a un StatusResponse."""
    payload = state.get_status_payload()
    return StatusResponse(**payload)
