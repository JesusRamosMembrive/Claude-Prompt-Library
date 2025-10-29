# SPDX-License-Identifier: MIT
"""
Analizador para archivos TypeScript / TSX usando tree-sitter.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

try:
    from tree_sitter import Node, Parser  # type: ignore
    from tree_sitter_languages import get_language  # type: ignore
except ImportError:  # pragma: no cover - dependiente del entorno
    Parser = None  # type: ignore
    Node = object  # type: ignore
    get_language = None  # type: ignore

from .analyzer import get_modified_time
from .models import FileSummary, SymbolInfo, SymbolKind


@dataclass
class _TsParser:
    parser: Parser

    @classmethod
    def for_language(cls, name: str) -> "_TsParser":
        if get_language is None or Parser is None:
            raise RuntimeError("tree_sitter_languages no disponible")
        language = get_language(name)
        parser = Parser()
        parser.set_language(language)
        return cls(parser=parser)


class TsAnalyzer:
    def __init__(self, *, include_docstrings: bool = False, is_tsx: bool = False) -> None:
        self.include_docstrings = include_docstrings
        self.parser_wrapper = None
        if Parser is not None and get_language is not None:
            try:
                self.parser_wrapper = _TsParser.for_language("tsx" if is_tsx else "typescript")
            except Exception:  # pragma: no cover
                self.parser_wrapper = None

    def parse(self, path: Path) -> FileSummary:
        abs_path = path.resolve()
        try:
            source = abs_path.read_text(encoding="utf-8")
        except OSError:
            return FileSummary(path=abs_path, symbols=[], errors=[], modified_at=None)

        if not self.parser_wrapper:
            return FileSummary(
                path=abs_path,
                symbols=[],
                errors=[],
                modified_at=get_modified_time(abs_path),
            )

        tree = self.parser_wrapper.parser.parse(bytes(source, "utf-8"))
        symbols: List[SymbolInfo] = []
        root = tree.root_node
        self._collect_from_children(root, path, symbols, source.splitlines())

        return FileSummary(
            path=abs_path,
            symbols=symbols,
            errors=[],
            modified_at=get_modified_time(abs_path),
        )

    def _collect_from_children(
        self,
        node: Node,
        file_path: Path,
        symbols: List[SymbolInfo],
        lines: List[str],
        parent: Optional[str] = None,
    ) -> None:
        for child in node.children:
            if child.type in {"function_declaration", "method_definition"}:
                name = self._extract_identifier(child)
                if not name:
                    continue
                lineno = child.start_point[0] + 1
                doc = self._find_leading_comment(child, lines) if self.include_docstrings else None
                kind = (
                    SymbolKind.METHOD if parent and child.type == "method_definition" else SymbolKind.FUNCTION
                )
                symbols.append(
                    SymbolInfo(
                        name=name,
                        kind=kind,
                        parent=parent if kind is SymbolKind.METHOD else None,
                        path=file_path,
                        lineno=lineno,
                        docstring=doc,
                    )
                )
                if child.type == "method_definition":
                    continue
            elif child.type == "class_declaration":
                class_name = self._extract_identifier(child)
                if class_name:
                    lineno = child.start_point[0] + 1
                    doc = (
                        self._find_leading_comment(child, lines)
                        if self.include_docstrings
                        else None
                    )
                    symbols.append(
                        SymbolInfo(
                            name=class_name,
                            kind=SymbolKind.CLASS,
                            path=file_path,
                            lineno=lineno,
                            docstring=doc,
                        )
                    )
                    body = self._find_child(child, "class_body")
                    if body:
                        self._collect_from_children(body, file_path, symbols, lines, parent=class_name)
                    continue
            elif child.type == "lexical_declaration":
                self._handle_lexical_declaration(child, file_path, symbols, lines)

            self._collect_from_children(child, file_path, symbols, lines, parent)

    def _extract_identifier(self, node: Node) -> Optional[str]:
        ident = self._find_child(node, "identifier")
        if ident:
            return ident.text.decode("utf-8")
        name = node.child_by_field_name("name")
        if name and name.type == "identifier":
            return name.text.decode("utf-8")
        return None

    def _find_child(self, node: Node, type_name: str) -> Optional[Node]:
        for child in node.children:
            if child.type == type_name:
                return child
        return None

    def _handle_lexical_declaration(
        self,
        node: Node,
        file_path: Path,
        symbols: List[SymbolInfo],
        lines: List[str],
    ) -> None:
        for child in node.children:
            if child.type == "variable_declarator":
                ident = child.child_by_field_name("name")
                initializer = child.child_by_field_name("value")
                if (
                    ident
                    and initializer
                    and initializer.type in {"arrow_function", "function"}
                ):
                    name = ident.text.decode("utf-8")
                    lineno = initializer.start_point[0] + 1
                    doc = (
                        self._find_leading_comment(child, lines)
                        if self.include_docstrings
                        else None
                    )
                    symbols.append(
                        SymbolInfo(
                            name=name,
                            kind=SymbolKind.FUNCTION,
                            path=file_path,
                            lineno=lineno,
                            docstring=doc,
                        )
                    )

    def _find_leading_comment(self, node: Node, lines: List[str]) -> Optional[str]:
        start_line = node.start_point[0]
        for offset in range(1, 4):
            index = start_line - offset
            if index < 0:
                break
            text = lines[index].strip()
            if text.startswith("//"):
                return text[2:].strip()
            if text.startswith("/*"):
                comment_lines: List[str] = []
                j = index
                while j >= 0:
                    line = lines[j].strip()
                    comment_lines.insert(0, line)
                    if "/*" in line:
                        break
                    j -= 1
                cleaned = [segment.strip("/* ") for segment in comment_lines]
                return " ".join(cleaned).strip()
            if text:
                break
        return None
