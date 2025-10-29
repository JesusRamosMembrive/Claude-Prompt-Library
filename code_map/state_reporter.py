# SPDX-License-Identifier: MIT
"""
Servicios auxiliares para serializar settings y estado de la aplicación.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from .analyzer_registry import AnalyzerCapability
from .scanner import ProjectScanner
from .settings import AppSettings
from .index import SymbolIndex


def _serialize_capability(cap: AnalyzerCapability) -> Dict[str, Any]:
    return {
        "key": cap.key,
        "description": cap.description,
        "extensions": cap.extensions,
        "available": cap.available,
        "dependency": cap.dependency,
        "error": cap.error,
        "degraded_extensions": cap.degraded_extensions,
    }


@dataclass
class StateReporter:
    """Encapsula la construcción de payloads derivados del estado global."""

    settings: AppSettings
    scanner: ProjectScanner
    index: SymbolIndex

    def settings_payload(self, *, watcher_active: bool) -> Dict[str, Any]:
        return {
            "root_path": self.settings.root_path.as_posix(),
            "exclude_dirs": self.settings.exclude_dirs,
            "include_docstrings": self.settings.include_docstrings,
            "watcher_active": watcher_active,
            "absolute_root": str(self.settings.root_path),
        }

    def status_payload(
        self,
        *,
        watcher_active: bool,
        last_full_scan: Optional[datetime],
        last_event_batch: Optional[datetime],
        pending_events: int,
    ) -> Dict[str, Any]:
        summaries = self.index.get_all()
        total_files = len(summaries)
        total_symbols = sum(len(summary.symbols) for summary in summaries)
        capabilities = [_serialize_capability(cap) for cap in self.scanner.registry.capabilities]

        return {
            "root_path": self.settings.root_path.as_posix(),
            "absolute_root": str(self.settings.root_path),
            "watcher_active": watcher_active,
            "include_docstrings": self.settings.include_docstrings,
            "last_full_scan": last_full_scan,
            "last_event_batch": last_event_batch,
            "files_indexed": total_files,
            "symbols_indexed": total_symbols,
            "pending_events": pending_events,
            "capabilities": capabilities,
        }
