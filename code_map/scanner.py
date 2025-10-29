# SPDX-License-Identifier: MIT
"""
Escaneo de proyectos para obtener resúmenes de archivos Python.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Set

from .analyzer import FileAnalyzer
from .analyzer_registry import AnalyzerRegistry
from .events import ChangeBatch
from .models import FileSummary

if TYPE_CHECKING:
    from .cache import SnapshotStore
    from .index import SymbolIndex


DEFAULT_EXCLUDED_DIRS: Set[str] = {
    "__pycache__",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "env",
    "node_modules",
    "venv",
}

DEFAULT_EXTENSIONS: Set[str] = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
}

class ProjectScanner:
    """Coordina los escaneos completos de una ruta raíz."""

    def __init__(
        self,
        root: Path,
        *,
        analyzer: Optional[FileAnalyzer] = None,
        analyzers: Optional[Mapping[str, Any]] = None,
        exclude_dirs: Optional[Sequence[str]] = None,
        include_docstrings: bool = False,
        extensions: Optional[Sequence[str]] = None,
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        if not self.root.exists():
            raise ValueError(f"La ruta raíz no existe: {self.root}")
        if not self.root.is_dir():
            raise ValueError(f"La ruta raíz debe ser un directorio: {self.root}")

        self.exclude_dirs = set(DEFAULT_EXCLUDED_DIRS)
        if exclude_dirs:
            self.exclude_dirs.update(exclude_dirs)

        base_extensions = DEFAULT_EXTENSIONS.copy()
        if extensions:
            base_extensions.update(
                ext if ext.startswith(".") else f".{ext}"
                for ext in extensions
            )
        self.extensions: Set[str] = {ext.lower() for ext in base_extensions}

        overrides: Dict[str, Any] = {}
        if analyzers:
            for ext, custom_analyzer in analyzers.items():
                key = ext if ext.startswith(".") else f".{ext}"
                overrides[key.lower()] = custom_analyzer

        if analyzer:
            overrides[".py"] = analyzer

        self.registry = AnalyzerRegistry(
            include_docstrings=include_docstrings,
            extensions=self.extensions,
            overrides=overrides or None,
        )
        self.analyzers = self.registry.analyzers

    def scan(self) -> List[FileSummary]:
        """Ejecuta un recorrido completo del árbol y devuelve resúmenes por archivo."""
        summaries: List[FileSummary] = []
        for path in self._iter_supported_files():
            analyzer = self.analyzers.get(path.suffix.lower())
            if not analyzer:
                continue
            summaries.append(analyzer.parse(path))
        return summaries

    def scan_and_update_index(
        self,
        index: "SymbolIndex",
        *,
        persist: bool = False,
        store: Optional["SnapshotStore"] = None,
    ) -> List[FileSummary]:
        """
        Ejecuta un escaneo, actualiza el índice y opcionalmente persiste un snapshot.
        """

        summaries = self.scan()
        index.update(summaries)
        if persist:
            snapshot_store = store or self._default_store()
            index.save_snapshot(snapshot_store)
        return summaries

    def hydrate_index_from_snapshot(
        self,
        index: "SymbolIndex",
        *,
        store: Optional["SnapshotStore"] = None,
    ) -> List[FileSummary]:
        """
        Carga un snapshot (si existe) y lo aplica al índice antes de escanear.
        """

        snapshot_store = store or self._default_store()
        return index.load_snapshot(snapshot_store)

    def apply_change_batch(
        self,
        batch: ChangeBatch,
        index: "SymbolIndex",
        *,
        persist: bool = False,
        store: Optional["SnapshotStore"] = None,
    ) -> dict:
        """
        Reprocesa los archivos afectados por un lote de cambios y actualiza el índice.
        """

        if not batch:
            return {"updated": [], "deleted": []}

        updated: List[Path] = []
        deleted: List[Path] = []

        refresh_candidates = list(batch.created) + list(batch.modified)
        to_refresh = self._dedupe_paths(refresh_candidates)
        to_delete = self._dedupe_paths(batch.deleted)

        for path in to_refresh:
            if not path.exists():
                continue
            if path.suffix.lower() not in self.extensions:
                continue
            analyzer = self.analyzers.get(path.suffix.lower())
            if not analyzer:
                continue
            summary = analyzer.parse(path)
            index.update_file(summary)
            updated.append(path)

        for path in to_delete:
            index.remove(path)
            deleted.append(path)

        if persist:
            snapshot_store = store or self._default_store()
            index.save_snapshot(snapshot_store)

        return {"updated": updated, "deleted": deleted}

    def _iter_supported_files(self) -> Iterator[Path]:
        """Genera rutas absolutas a cada archivo con extensión soportada."""
        for dirpath, dirnames, filenames in os.walk(self.root, followlinks=False):
            dirnames[:] = [
                d for d in dirnames if not self._should_exclude(Path(dirpath) / d)
            ]
            for filename in filenames:
                suffix = Path(filename).suffix.lower()
                if suffix not in self.extensions:
                    continue
                full_path = Path(dirpath, filename)
                if full_path.is_file():
                    yield full_path.resolve()

    def _should_exclude(self, path: Path) -> bool:
        name = path.name
        if name in self.exclude_dirs:
            return True
        # Excluir directorios ocultos comunes excepto el propio root.
        if name.startswith(".") and path != self.root:
            return True
        return False

    def _default_store(self) -> "SnapshotStore":
        from .cache import SnapshotStore

        return SnapshotStore(self.root)

    def _within_root(self, path: Path) -> bool:
        try:
            Path(path).resolve().relative_to(self.root)
            return True
        except ValueError:
            return False

    def _dedupe_paths(self, paths: Iterable[Path]) -> List[Path]:
        ordered: List[Path] = []
        seen: Set[Path] = set()
        for path in paths:
            resolved = Path(path).resolve()
            if not self._within_root(resolved):
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            ordered.append(resolved)
        return ordered
