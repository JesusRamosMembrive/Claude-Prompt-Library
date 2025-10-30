# SPDX-License-Identifier: MIT
"""
Almacén en memoria y utilidades de consulta sobre los resultados del análisis.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterable, Iterator, List, Optional

from .models import FileSummary, ProjectTreeNode, SymbolInfo

if TYPE_CHECKING:
    from .cache import SnapshotStore


class SymbolIndex:
    """Mantiene un índice en memoria de los resúmenes de archivos analizados."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self._files: Dict[Path, FileSummary] = {}

    def update(self, summaries: Iterable[FileSummary]) -> None:
        """Actualiza múltiples archivos en el índice."""
        for summary in summaries:
            self._files[summary.path] = summary

    def update_file(self, summary: FileSummary) -> None:
        """Actualiza o inserta un único resumen en el índice."""
        self._files[summary.path] = summary

    def remove(self, path: Path) -> None:
        """Elimina un archivo del índice si existe."""
        self._files.pop(Path(path).resolve(), None)

    def get_file(self, path: Path) -> Optional[FileSummary]:
        """Recupera el resumen asociado a una ruta concreta."""
        return self._files.get(Path(path).resolve())

    def get_all(self) -> List[FileSummary]:
        """Devuelve la lista completa de resúmenes almacenados."""
        return list(self._files.values())

    def iter_symbols(self) -> Iterator[SymbolInfo]:
        """Itera sobre todos los símbolos indexados."""
        for summary in self._files.values():
            yield from summary.symbols

    def search(self, term: str) -> List[SymbolInfo]:
        """Busca símbolos cuyo nombre contenga el término proporcionado."""
        if not term:
            return []
        lowered = term.lower()
        return [
            symbol
            for symbol in self.iter_symbols()
            if lowered in symbol.name.lower()
        ]

    def get_tree(self) -> ProjectTreeNode:
        """Construye el árbol jerárquico carpeta → archivo → símbolos."""
        root_node = ProjectTreeNode(
            name=self.root.name or str(self.root),
            path=self.root,
            is_dir=True,
        )

        files_sorted = sorted(self._files.items(), key=lambda item: str(item[0]))
        for file_path, summary in files_sorted:
            try:
                relative_parts = file_path.relative_to(self.root).parts
            except ValueError:
                relative_parts = ()

            node = root_node
            accumulated_path = self.root
            for part in relative_parts[:-1]:
                accumulated_path = accumulated_path / part
                node = node.ensure_child(part, accumulated_path, is_dir=True)

            file_part = relative_parts[-1] if relative_parts else file_path.name
            file_path_final = (
                accumulated_path / file_part if relative_parts else file_path
            )
            file_node = node.ensure_child(
                file_part,
                file_path_final,
                is_dir=False,
            )
            file_node.file_summary = summary

        return root_node

    def load_snapshot(self, store: "SnapshotStore") -> List[FileSummary]:
        """Carga un snapshot y actualiza el índice con su contenido."""
        summaries = store.load()
        self.update(summaries)
        return summaries

    def save_snapshot(self, store: "SnapshotStore") -> None:
        """Persiste el estado actual del índice en un snapshot."""
        store.save(self._files.values())
