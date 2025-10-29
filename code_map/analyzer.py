# SPDX-License-Identifier: MIT
"""
Lógica de análisis individual de archivos Python usando AST.
"""

from __future__ import annotations

import ast
import tokenize
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Union

from .models import AnalysisError, FileSummary, SymbolInfo, SymbolKind


def get_modified_time(path: Path) -> Optional[datetime]:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None

AstFunction = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class FileAnalyzer:
    """
    Extrae símbolos soportados (funciones, clases, métodos) de un archivo Python.
    """

    def __init__(self, *, include_docstrings: bool = False) -> None:
        self.include_docstrings = include_docstrings

    def parse(self, path: Path) -> FileSummary:
        abs_path = Path(path).resolve()
        try:
            source = self._read_source(abs_path)
            tree = ast.parse(source, filename=str(abs_path))
        except SyntaxError as exc:  # análisis continúa pese a errores
            error = AnalysisError(
                message=str(exc.msg),
                lineno=exc.lineno,
                col_offset=exc.offset,
            )
            return FileSummary(
                path=abs_path,
                symbols=[],
                errors=[error],
                modified_at=get_modified_time(abs_path),
            )
        except OSError as exc:
            error = AnalysisError(message=f"No se pudo leer el archivo: {exc}")
            return FileSummary(path=abs_path, errors=[error])

        symbols: List[SymbolInfo] = []

        for node in tree.body:
            if self._is_function(node):
                symbols.append(self._build_function_symbol(node, abs_path))
            elif isinstance(node, ast.ClassDef):
                symbols.append(self._build_class_symbol(node, abs_path))
                symbols.extend(self._build_method_symbols(node, abs_path))

        return FileSummary(
            path=abs_path,
            symbols=symbols,
            modified_at=get_modified_time(abs_path),
        )

    def _read_source(self, path: Path) -> str:
        with path.open("rb") as buffer:
            encoding, _ = tokenize.detect_encoding(buffer.readline)
            buffer.seek(0)
            data = buffer.read()
        return data.decode(encoding)

    def _build_function_symbol(self, node: AstFunction, path: Path) -> SymbolInfo:
        return SymbolInfo(
            name=node.name,
            kind=SymbolKind.FUNCTION,
            path=path,
            lineno=node.lineno,
            docstring=self._docstring_for(node),
        )

    def _build_class_symbol(self, node: ast.ClassDef, path: Path) -> SymbolInfo:
        return SymbolInfo(
            name=node.name,
            kind=SymbolKind.CLASS,
            path=path,
            lineno=node.lineno,
            docstring=self._docstring_for(node),
        )

    def _build_method_symbols(
        self, class_node: ast.ClassDef, path: Path
    ) -> Iterable[SymbolInfo]:
        for item in class_node.body:
            if self._is_function(item):
                yield SymbolInfo(
                    name=item.name,
                    kind=SymbolKind.METHOD,
                    path=path,
                    lineno=item.lineno,
                    parent=class_node.name,
                    docstring=self._docstring_for(item),
                )

    def _docstring_for(self, node: ast.AST) -> Optional[str]:
        if not self.include_docstrings:
            return None
        return ast.get_docstring(node)

    @staticmethod
    def _is_function(node: ast.AST) -> bool:
        return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
