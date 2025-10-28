# SPDX-License-Identifier: MIT
"""
Esquemas Pydantic para serializar respuestas de la API.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from pydantic import BaseModel, Field

from ..models import AnalysisError, FileSummary, ProjectTreeNode, SymbolInfo, SymbolKind
from ..state import AppState


class HealthResponse(BaseModel):
    status: str = "ok"


class AnalysisErrorSchema(BaseModel):
    message: str
    lineno: Optional[int] = None
    col_offset: Optional[int] = None


class SymbolSchema(BaseModel):
    name: str
    kind: SymbolKind
    lineno: int
    parent: Optional[str] = None
    path: Optional[str] = None
    docstring: Optional[str] = None


class FileSummarySchema(BaseModel):
    path: str
    modified_at: Optional[datetime] = None
    symbols: List[SymbolSchema] = Field(default_factory=list)
    errors: List[AnalysisErrorSchema] = Field(default_factory=list)


class TreeNodeSchema(BaseModel):
    name: str
    path: str
    is_dir: bool
    children: List["TreeNodeSchema"] = Field(default_factory=list)
    symbols: Optional[List[SymbolSchema]] = None
    errors: Optional[List[AnalysisErrorSchema]] = None
    modified_at: Optional[datetime] = None


TreeNodeSchema.model_rebuild()


class SearchResultsSchema(BaseModel):
    results: List[SymbolSchema]


class RescanResponse(BaseModel):
    files: int


class ChangeNotification(BaseModel):
    updated: List[str]
    deleted: List[str]


def serialize_symbol(symbol: SymbolInfo, state: AppState, *, include_path: bool = True) -> SymbolSchema:
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
    return AnalysisErrorSchema(
        message=error.message,
        lineno=error.lineno,
        col_offset=error.col_offset,
    )


def serialize_summary(summary: FileSummary, state: AppState) -> FileSummarySchema:
    symbols = [serialize_symbol(symbol, state, include_path=False) for symbol in summary.symbols]
    errors = [serialize_error(error) for error in summary.errors]
    return FileSummarySchema(
        path=state.to_relative(summary.path),
        modified_at=summary.modified_at,
        symbols=symbols,
        errors=errors,
    )


def serialize_tree(node: ProjectTreeNode, state: AppState) -> TreeNodeSchema:
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
    return SearchResultsSchema(results=[serialize_symbol(symbol, state) for symbol in symbols])
