# SPDX-License-Identifier: MIT
"""
Core analysis engine exports.
"""

from .models import FileSummary, SymbolInfo, SymbolKind, ProjectTreeNode
from .analyzer import FileAnalyzer
from .events import ChangeBatch, ChangeEventType
from .scheduler import ChangeScheduler
from .scanner import ProjectScanner
from .index import SymbolIndex
from .cache import SnapshotStore
from .watcher import WatcherService
from .state import AppState

try:
    from .server import create_app
except ImportError:  # pragma: no cover - dependencia opcional
    create_app = None  # type: ignore

__all__ = [
    "FileSummary",
    "SymbolInfo",
    "SymbolKind",
    "ProjectTreeNode",
    "FileAnalyzer",
    "ChangeBatch",
    "ChangeEventType",
    "ChangeScheduler",
    "ProjectScanner",
    "SymbolIndex",
    "SnapshotStore",
    "WatcherService",
    "AppState",
]

if create_app is not None:
    __all__.append("create_app")
