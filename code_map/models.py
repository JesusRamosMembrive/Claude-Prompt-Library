# SPDX-License-Identifier: MIT
"""
Dataclasses y tipos para representar la información del análisis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class SymbolKind(str, Enum):
    """Tipos de símbolos soportados por el motor."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    ELEMENT = "element"


@dataclass(slots=True)
class SymbolInfo:
    """
    Representa una función libre, una clase o un método detectado en un archivo.
    `parent` se utiliza para enlazar métodos con la clase que los contiene.
    """

    name: str
    kind: SymbolKind
    path: Path
    lineno: int
    parent: Optional[str] = None
    docstring: Optional[str] = None


@dataclass(slots=True)
class AnalysisError:
    """Errores asociados al procesamiento de un archivo."""

    message: str
    lineno: Optional[int] = None
    col_offset: Optional[int] = None


@dataclass(slots=True)
class FileSummary:
    """Resumen de símbolos y errores de un archivo concreto."""

    path: Path
    symbols: List[SymbolInfo] = field(default_factory=list)
    errors: List[AnalysisError] = field(default_factory=list)
    modified_at: Optional[datetime] = None

    def has_errors(self) -> bool:
        return bool(self.errors)


@dataclass(slots=True)
class ProjectTreeNode:
    """Nodo de la jerarquía carpeta → archivo → símbolos."""

    name: str
    path: Path
    is_dir: bool
    children: Dict[str, "ProjectTreeNode"] = field(default_factory=dict)
    file_summary: Optional[FileSummary] = None

    def add_child(self, node: "ProjectTreeNode") -> None:
        self.children[node.name] = node

    def ensure_child(self, name: str, path: Path, is_dir: bool) -> "ProjectTreeNode":
        child = self.children.get(name)
        if child is None:
            child = ProjectTreeNode(name=name, path=path, is_dir=is_dir)
            self.children[name] = child
        return child
