# SPDX-License-Identifier: MIT
"""
Analizador para archivos JavaScript/TypeScript usando esprima.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .analyzer import get_modified_time
from .models import FileSummary, SymbolInfo, SymbolKind

try:
    import esprima  # type: ignore[import]
except ImportError:  # pragma: no cover - opcional
    esprima = None

logger = logging.getLogger(__name__)


class JsAnalyzer:
    def __init__(self, *, include_docstrings: bool = True) -> None:
        self.include_docstrings = include_docstrings
        if esprima is None:  # pragma: no cover - dependiente del entorno
            logger.warning(
                "La librería 'esprima' no está instalada; el análisis de JS/TS se degradará."
            )

    def parse(self, path: Path) -> FileSummary:
        abs_path = path.resolve()
        if esprima is None:
            return FileSummary(
                path=abs_path,
                symbols=[],
                errors=[],
                modified_at=get_modified_time(abs_path),
            )

        try:
            source = abs_path.read_text(encoding="utf-8")
        except OSError as exc:
            return FileSummary(
                path=abs_path,
                symbols=[],
                errors=[],
                modified_at=None,
            )

        try:
            module = esprima.parseModule(
                source, comment=True, range=True, loc=True, tolerant=True
            )
        except Exception as exc:  # pragma: no cover - errores de parseo
            logger.debug("Error parseando %s: %s", abs_path, exc)
            return FileSummary(
                path=abs_path,
                symbols=[],
                errors=[],
                modified_at=get_modified_time(abs_path),
            )

        comments = module.get("comments", []) or []
        comment_map = self._build_comment_map(comments)

        symbols: List[SymbolInfo] = []
        body = module.get("body", []) or []
        for node in body:
            self._collect_from_node(node, symbols, comment_map, parent=None, file_path=abs_path)

        return FileSummary(
            path=abs_path,
            symbols=symbols,
            errors=[],
            modified_at=get_modified_time(abs_path),
        )

    def _collect_from_node(
        self,
        node: Dict[str, Any],
        symbols: List[SymbolInfo],
        comment_map: Dict[int, str],
        parent: Optional[str],
        file_path: Path,
    ) -> None:
        node_type = node.get("type")

        if node_type == "FunctionDeclaration":
            name = node.get("id", {}).get("name")
            if name:
                line = node.get("loc", {}).get("start", {}).get("line")
                doc = self._docstring_for(line, comment_map)
                symbols.append(
                    SymbolInfo(
                        name=name,
                        kind=SymbolKind.FUNCTION,
                        path=file_path,
                        lineno=line or 0,
                        docstring=doc,
                    )
                )
        elif node_type == "ClassDeclaration":
            class_name = node.get("id", {}).get("name")
            line = node.get("loc", {}).get("start", {}).get("line")
            doc = self._docstring_for(line, comment_map)
            if class_name:
                symbols.append(
                    SymbolInfo(
                        name=class_name,
                        kind=SymbolKind.CLASS,
                        path=file_path,
                        lineno=line or 0,
                        docstring=doc,
                    )
                )
                for item in (node.get("body", {}) or {}).get("body", []) or []:
                    if item.get("type") == "MethodDefinition":
                        method_name = self._method_name(item)
                        if method_name:
                            method_line = (
                                item.get("value", {})
                                .get("loc", {})
                                .get("start", {})
                                .get("line")
                            )
                            method_doc = self._docstring_for(method_line, comment_map)
                            symbols.append(
                                SymbolInfo(
                                    name=method_name,
                                    kind=SymbolKind.METHOD,
                                    parent=class_name,
                                    path=file_path,
                                    lineno=method_line or 0,
                                    docstring=method_doc,
                                )
                            )
        elif node_type in {"ExportNamedDeclaration", "ExportDefaultDeclaration"}:
            declaration = node.get("declaration")
            if declaration:
                self._collect_from_node(
                    declaration, symbols, comment_map, parent=None, file_path=file_path
                )
        elif node_type == "VariableDeclaration":
            for declarator in node.get("declarations", []) or []:
                self._handle_variable_declarator(declarator, symbols, comment_map, file_path)

    def _handle_variable_declarator(
        self,
        declarator: Dict[str, Any],
        symbols: List[SymbolInfo],
        comment_map: Dict[int, str],
        file_path: Path,
    ) -> None:
        id_node = declarator.get("id")
        init = declarator.get("init")
        if not id_node or not init:
            return

        name = id_node.get("name")
        init_type = init.get("type")
        if name and init_type in {"FunctionExpression", "ArrowFunctionExpression"}:
            line = init.get("loc", {}).get("start", {}).get("line")
            doc = self._docstring_for(line, comment_map)
            symbols.append(
                SymbolInfo(
                    name=name,
                    kind=SymbolKind.FUNCTION,
                    path=file_path,
                    lineno=line or 0,
                    docstring=doc,
                )
            )

    def _method_name(self, node: Dict[str, Any]) -> Optional[str]:
        key = node.get("key")
        if not key:
            return None
        if key.get("type") == "Identifier":
            return key.get("name")
        if key.get("type") == "Literal":
            return str(key.get("value"))
        return None

    def _build_comment_map(self, comments: List[Dict[str, Any]]) -> Dict[int, str]:
        if not self.include_docstrings:
            return {}
        result: Dict[int, str] = {}
        for comment in comments:
            loc = comment.get("loc")
            if not loc:
                continue
            end_line = loc.get("end", {}).get("line")
            if end_line is None:
                continue
            value = comment.get("value", "")
            cleaned = self._clean_comment(value)
            result[end_line] = cleaned
        return result

    def _docstring_for(self, line: Optional[int], comment_map: Dict[int, str]) -> Optional[str]:
        if not self.include_docstrings or line is None:
            return None
        # Buscar comentario inmediatamente anterior (línea anterior o dos líneas antes).
        for offset in (1, 2):
            doc = comment_map.get(line - offset)
            if doc:
                return doc
        return None

    def _clean_comment(self, value: str) -> str:
        stripped = value.strip()
        # Eliminar asteriscos de bloque JSDoc
        lines = [line.strip(" *") for line in stripped.splitlines()]
        return " ".join(line for line in lines if line).strip()
