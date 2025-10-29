# SPDX-License-Identifier: MIT
"""
Analizador básico para documentos HTML.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:  # pragma: no cover - dependencia opcional
    BeautifulSoup = None  # type: ignore

from .analyzer import get_modified_time
from .models import FileSummary, SymbolInfo, SymbolKind


class HtmlAnalyzer:
    def parse(self, path: Path) -> FileSummary:
        abs_path = path.resolve()
        try:
            content = abs_path.read_text(encoding="utf-8")
        except OSError:
            return FileSummary(path=abs_path)

        if BeautifulSoup is None:
            return FileSummary(
                path=abs_path,
                symbols=[],
                errors=[],
                modified_at=get_modified_time(abs_path),
            )

        soup = BeautifulSoup(content, "html.parser")
        symbols: List[SymbolInfo] = []

        for element in soup.find_all(True):
            tag_name = element.name or "element"
            element_id = element.get("id")
            if element_id:
                symbols.append(
                    SymbolInfo(
                        name=element_id,
                        kind=SymbolKind.ELEMENT,
                        parent=tag_name,
                        path=abs_path,
                        lineno=0,
                        docstring=None,
                    )
                )
            elif tag_name and "-" in tag_name:  # custom elements
                symbols.append(
                    SymbolInfo(
                        name=tag_name,
                        kind=SymbolKind.ELEMENT,
                        parent=None,
                        path=abs_path,
                        lineno=0,
                        docstring=None,
                    )
                )

        return FileSummary(
            path=abs_path,
            symbols=symbols,
            errors=[],
            modified_at=get_modified_time(abs_path),
        )
