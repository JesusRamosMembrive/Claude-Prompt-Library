# SPDX-License-Identifier: MIT
"""
Analizador básico para documentos HTML.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from .analyzer import get_modified_time
from .dependencies import optional_dependencies
from .models import FileSummary, SymbolInfo, SymbolKind


class HtmlAnalyzer:
    """Analiza documentos HTML para extraer elementos identificables."""

    def __init__(self) -> None:
        """Inicializa BeautifulSoup si la dependencia opcional está disponible."""
        module = optional_dependencies.require("beautifulsoup4", module="bs4")
        self._beautiful_soup = getattr(module, "BeautifulSoup", None) if module else None
        status = optional_dependencies.status("beautifulsoup4")[0]
        self.available = bool(status.available and self._beautiful_soup)

    def parse(self, path: Path) -> FileSummary:
        """
        Analiza un archivo HTML y devuelve los elementos relevantes.

        Args:
            path: Ruta del archivo HTML a procesar.

        Returns:
            Un resumen con los elementos detectados (ids y custom elements).
        """
        abs_path = path.resolve()
        try:
            content = abs_path.read_text(encoding="utf-8")
        except OSError:
            return FileSummary(path=abs_path)

        if not self._beautiful_soup:
            return FileSummary(
                path=abs_path,
                symbols=[],
                errors=[],
                modified_at=get_modified_time(abs_path),
            )

        soup = self._beautiful_soup(content, "html.parser")
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
