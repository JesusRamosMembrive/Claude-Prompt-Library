# SPDX-License-Identifier: MIT
"""
Estado compartido de la aplicación FastAPI.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .cache import SnapshotStore
from .index import SymbolIndex
from .scanner import ProjectScanner
from .scheduler import ChangeScheduler
from .watcher import WatcherService
from .settings import AppSettings, save_settings
from .state_reporter import StateReporter

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    """Estado compartido de la aplicación FastAPI."""
    settings: AppSettings
    scheduler: ChangeScheduler
    scanner: ProjectScanner = field(init=False)
    index: SymbolIndex = field(init=False)
    snapshot_store: SnapshotStore = field(init=False)
    watcher: Optional[WatcherService] = field(init=False, default=None)
    last_full_scan: Optional[datetime] = field(init=False, default=None)
    last_event_batch: Optional[datetime] = field(init=False, default=None)
    reporter: StateReporter = field(init=False)

    def __post_init__(self) -> None:
        self.event_queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self._scheduler_task: Optional[asyncio.Task[None]] = None
        self._build_components()

    async def startup(self) -> None:
        """Inicializa el estado de la aplicación."""
        logger.info("Inicializando estado de la app para %s", self.settings.root_path)
        await asyncio.to_thread(
            self.scanner.hydrate_index_from_snapshot,
            self.index,
            store=self.snapshot_store,
        )
        summaries = await asyncio.to_thread(
            self.scanner.scan_and_update_index,
            self.index,
            persist=True,
            store=self.snapshot_store,
        )
        if summaries:
            self.last_full_scan = datetime.now(timezone.utc)
        if self.watcher:
            started = await asyncio.to_thread(self.watcher.start)
            if not started:
                logger.warning("Watcher no iniciado (watchdog ausente o error).")
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def shutdown(self) -> None:
        """Detiene el estado de la aplicación."""
        logger.info("Deteniendo estado de la app")
        self._stop_event.set()
        if self._scheduler_task:
            await self._scheduler_task
        if self.watcher:
            await asyncio.to_thread(self.watcher.stop)

    async def _scheduler_loop(self) -> None:
        """Bucle principal del programador de cambios."""
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
                    self.last_event_batch = datetime.now(timezone.utc)
                    await self.event_queue.put(payload)
            await asyncio.sleep(self.scheduler.debounce_seconds)

    def _serialize_changes(self, changes: Dict[str, Iterable[Path]]) -> Dict[str, List[str]]:
        """Serializa los cambios para la notificación de eventos."""
        updated = [self.to_relative(path) for path in changes.get("updated", [])]
        deleted = [self.to_relative(path) for path in changes.get("deleted", [])]
        return {"updated": updated, "deleted": deleted}

    async def perform_full_scan(self) -> int:
        """Realiza un escaneo completo del proyecto."""
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
            self.last_event_batch = datetime.now(timezone.utc)
            await self.event_queue.put(payload)
        self.last_full_scan = datetime.now(timezone.utc)
        return len(summaries)

    def to_relative(self, path: Path) -> str:
        """Convierte una ruta absoluta en una ruta relativa al root del proyecto."""
        try:
            rel = path.resolve().relative_to(self.settings.root_path)
            return rel.as_posix()
        except ValueError:
            return path.resolve().as_posix()

    def resolve_path(self, relative: str) -> Path:
        """Resuelve una ruta relativa en una ruta absoluta dentro del root del proyecto."""
        candidate = (self.settings.root_path / relative).resolve()
        if not self._within_root(candidate):
            raise ValueError(f"Ruta fuera del root configurado: {relative}")
        return candidate

    def _within_root(self, path: Path) -> bool:
        """Comprueba si una ruta está dentro del root del proyecto."""
        try:
            path.resolve().relative_to(self.settings.root_path)
            return True
        except ValueError:
            return False

    def is_watcher_running(self) -> bool:
        """Comprueba si el observador de archivos está en ejecución."""
        return bool(self.watcher and self.watcher.is_running)

    def get_settings_payload(self) -> Dict[str, Any]:
        """Obtiene el payload de configuración para la API."""
        return self.reporter.settings_payload(watcher_active=self.is_watcher_running())

    def get_status_payload(self) -> Dict[str, Any]:
        """Obtiene el payload de estado para la API."""
        return self.reporter.status_payload(
            watcher_active=self.is_watcher_running(),
            last_full_scan=self.last_full_scan,
            last_event_batch=self.last_event_batch,
            pending_events=self.event_queue.qsize(),
        )

    async def update_settings(
        self,
        *,
        root_path: Optional[Path] = None,
        include_docstrings: Optional[bool] = None,
        exclude_dirs: Optional[Iterable[str]] = None,
    ) -> List[str]:
        """Actualiza la configuración de la aplicación."""
        new_settings = self.settings.with_updates(
            root_path=root_path,
            include_docstrings=include_docstrings,
            exclude_dirs=exclude_dirs,
        )
        updated_fields: List[str] = []
        if new_settings.root_path != self.settings.root_path:
            if not new_settings.root_path.exists() or not new_settings.root_path.is_dir():
                raise ValueError("La nueva ruta raíz no es válida o no existe.")
            updated_fields.append("root_path")
        if new_settings.include_docstrings != self.settings.include_docstrings:
            updated_fields.append("include_docstrings")
        if new_settings.exclude_dirs != self.settings.exclude_dirs:
            updated_fields.append("exclude_dirs")

        if not updated_fields:
            return []

        await self._apply_settings(new_settings)
        save_settings(self.settings)
        return updated_fields

    def _build_components(self) -> None:
        """(Re)construye los componentes de la aplicación a partir de la configuración."""
        self.scanner = ProjectScanner(
            self.settings.root_path,
            include_docstrings=self.settings.include_docstrings,
            exclude_dirs=self.settings.exclude_dirs,
        )
        self.index = SymbolIndex(self.settings.root_path)
        self.snapshot_store = SnapshotStore(self.settings.root_path)
        self.reporter = StateReporter(
            settings=self.settings,
            scanner=self.scanner,
            index=self.index,
        )
        self.watcher = WatcherService(
            self.settings.root_path,
            self.scheduler,
            exclude_dirs=self.settings.exclude_dirs,
            extensions=self.scanner.extensions,
        )

    async def _apply_settings(self, new_settings: AppSettings) -> None:
        """Aplica la nueva configuración a la aplicación."""
        if self.watcher and self.watcher.is_running:
            await asyncio.to_thread(self.watcher.stop)

        self.scheduler.clear()

        self.settings = new_settings
        self._build_components()

        # Vaciar cola de eventos para evitar notificaciones obsoletas
        try:
            while True:
                self.event_queue.get_nowait()
        except asyncio.QueueEmpty:
            pass

        await asyncio.to_thread(
            self.scanner.hydrate_index_from_snapshot,
            self.index,
            store=self.snapshot_store,
        )
        summaries = await asyncio.to_thread(
            self.scanner.scan_and_update_index,
            self.index,
            persist=True,
            store=self.snapshot_store,
        )

        self.last_full_scan = datetime.now(timezone.utc)

        if summaries:
            payload = {
                "updated": [self.to_relative(summary.path) for summary in summaries],
                "deleted": [],
            }
            self.last_event_batch = datetime.now(timezone.utc)
            await self.event_queue.put(payload)

        if self.watcher:
            started = await asyncio.to_thread(self.watcher.start)
            if not started:
                logger.warning(
                    "Watcher no iniciado tras actualizar settings para %s",
                    self.settings.root_path,
                )
