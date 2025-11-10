# SPDX-License-Identifier: MIT
"""
Persistencia en disco de resultados de análisis en formato JSON.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .constants import META_DIR_NAME
from .models import AnalysisError, FileSummary, SymbolInfo, SymbolKind


class SnapshotStore:
    """Gestiona snapshots en `<root>/.code-map/code-map.json`."""

    def __init__(
        self,
        root: Path,
        filename: str = "code-map.json",
        cache_dir: Optional[Path] = None,
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        # If cache_dir is specified, use it instead of root/.code-map
        if cache_dir is not None:
            self.meta_dir = Path(cache_dir).expanduser().resolve()
        else:
            self.meta_dir = self.root / META_DIR_NAME
        self.snapshot_path = self.meta_dir / filename

    def load(self) -> List[FileSummary]:
        """Carga un snapshot desde el disco."""
        if not self.snapshot_path.exists():
            return []

        data = self.snapshot_path.read_text(encoding="utf-8")
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            return []

        summaries: List[FileSummary] = []
        for entry in payload:
            summary = self._deserialize_file(entry)
            if summary is not None:
                summaries.append(summary)
        return summaries

    def save(self, summaries: Iterable[FileSummary]) -> None:
        """Guarda un snapshot en el disco."""
        serializable = [self._serialize_file(summary) for summary in summaries]
        serializable.sort(key=lambda item: item["path"])
        self.meta_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.write_text(
            json.dumps(serializable, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

    def _serialize_file(self, summary: FileSummary) -> Dict[str, Any]:
        """Serializa un objeto FileSummary a un diccionario."""
        path = summary.path.resolve()
        try:
            relative_path = path.relative_to(self.root).as_posix()
            is_relative = True
        except ValueError:
            relative_path = path.as_posix()
            is_relative = False

        return {
            "path": relative_path,
            "relative": is_relative,
            "modified_at": (
                summary.modified_at.isoformat() if summary.modified_at else None
            ),
            "symbols": [self._serialize_symbol(symbol) for symbol in summary.symbols],
            "errors": [self._serialize_error(error) for error in summary.errors],
        }

    def _serialize_symbol(self, symbol: SymbolInfo) -> Dict[str, Any]:
        """Serializa un objeto SymbolInfo a un diccionario."""
        return {
            "name": symbol.name,
            "kind": symbol.kind.value,
            "lineno": symbol.lineno,
            "parent": symbol.parent,
            "docstring": symbol.docstring,
        }

    def _serialize_error(self, error: AnalysisError) -> Dict[str, Any]:
        """Serializa un objeto AnalysisError a un diccionario."""
        return {
            "message": error.message,
            "lineno": error.lineno,
            "col_offset": error.col_offset,
        }

    def _deserialize_file(self, entry: Dict[str, Any]) -> Optional[FileSummary]:
        """Deserializa un diccionario a un objeto FileSummary."""
        raw_path = entry.get("path")
        if not raw_path:
            return None
        is_relative = entry.get("relative", True)
        if is_relative:
            file_path = (self.root / raw_path).resolve()
        else:
            file_path = Path(raw_path).expanduser().resolve()

        modified_raw = entry.get("modified_at")
        modified_at = datetime.fromisoformat(modified_raw) if modified_raw else None

        symbols = [
            self._deserialize_symbol(item, file_path)
            for item in entry.get("symbols", [])
        ]
        errors = [self._deserialize_error(item) for item in entry.get("errors", [])]

        return FileSummary(
            path=file_path,
            symbols=symbols,
            errors=errors,
            modified_at=modified_at,
        )

    def _deserialize_symbol(self, item: Dict[str, Any], path: Path) -> SymbolInfo:
        """Deserializa un diccionario a un objeto SymbolInfo."""
        kind_value = item.get("kind", SymbolKind.FUNCTION.value)
        return SymbolInfo(
            name=item.get("name", ""),
            kind=SymbolKind(kind_value),
            path=path,
            lineno=int(item.get("lineno", 0)),
            parent=item.get("parent"),
            docstring=item.get("docstring"),
        )

    def _deserialize_error(self, item: Dict[str, Any]) -> AnalysisError:
        """Deserializa un diccionario a un objeto AnalysisError."""
        return AnalysisError(
            message=item.get("message", ""),
            lineno=item.get("lineno"),
            col_offset=item.get("col_offset"),
        )
