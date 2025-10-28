# SPDX-License-Identifier: MIT
"""
Estado compartido de la aplicación FastAPI.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .cache import SnapshotStore
from .index import SymbolIndex
from .scanner import ProjectScanner
from .scheduler import ChangeScheduler
from .watcher import WatcherService

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    root: Path
    scanner: ProjectScanner
    index: SymbolIndex
    snapshot_store: SnapshotStore
    scheduler: ChangeScheduler
    watcher: Optional[WatcherService]
    include_docstrings: bool = False

    def __post_init__(self) -> None:
        self.root = self.root.expanduser().resolve()
        self.event_queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self._scheduler_task: Optional[asyncio.Task[None]] = None

    async def startup(self) -> None:
        logger.info("Inicializando estado de la app para %s", self.root)
        await asyncio.to_thread(
            self.scanner.hydrate_index_from_snapshot,
            self.index,
            store=self.snapshot_store,
        )
        await asyncio.to_thread(
            self.scanner.scan_and_update_index,
            self.index,
            persist=True,
            store=self.snapshot_store,
        )
        if self.watcher:
            started = await asyncio.to_thread(self.watcher.start)
            if not started:
                logger.warning("Watcher no iniciado (watchdog ausente o error).")
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def shutdown(self) -> None:
        logger.info("Deteniendo estado de la app")
        self._stop_event.set()
        if self._scheduler_task:
            await self._scheduler_task
        if self.watcher:
            await asyncio.to_thread(self.watcher.stop)

    async def _scheduler_loop(self) -> None:
        while not self._stop_event.is_set():
            batch = await asyncio.to_thread(self.scheduler.drain, force=True)
            if batch:
                changes = await asyncio.to_thread(
                    self.scanner.apply_change_batch,
                    batch,
                    self.index,
                    persist=True,
                    store=self.snapshot_store,
                )
                payload = self._serialize_changes(changes)
                if payload["updated"] or payload["deleted"]:
                    await self.event_queue.put(payload)
            await asyncio.sleep(self.scheduler.debounce_seconds)

    def _serialize_changes(self, changes: Dict[str, Iterable[Path]]) -> Dict[str, List[str]]:
        updated = [self.to_relative(path) for path in changes.get("updated", [])]
        deleted = [self.to_relative(path) for path in changes.get("deleted", [])]
        return {"updated": updated, "deleted": deleted}

    async def perform_full_scan(self) -> int:
        summaries = await asyncio.to_thread(
            self.scanner.scan_and_update_index,
            self.index,
            persist=True,
            store=self.snapshot_store,
        )
        payload = {
            "updated": [self.to_relative(summary.path) for summary in summaries],
            "deleted": [],
        }
        if payload["updated"]:
            await self.event_queue.put(payload)
        return len(summaries)

    def to_relative(self, path: Path) -> str:
        try:
            rel = path.resolve().relative_to(self.root)
            return rel.as_posix()
        except ValueError:
            return path.resolve().as_posix()

    def resolve_path(self, relative: str) -> Path:
        candidate = (self.root / relative).resolve()
        if not self._within_root(candidate):
            raise ValueError(f"Ruta fuera del root configurado: {relative}")
        return candidate

    def _within_root(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.root)
            return True
        except ValueError:
            return False
