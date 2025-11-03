# SPDX-License-Identifier: MIT
"""
Estado compartido de la aplicación FastAPI.
"""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from .cache import SnapshotStore
from .index import SymbolIndex
from .scanner import ProjectScanner
from .scheduler import ChangeScheduler
from .watcher import WatcherService
from .settings import AppSettings, save_settings, ENV_DISABLE_LINTERS
from .linters import (
    CheckStatus,
    Severity,
    record_linters_report,
    record_notification,
    run_linters_pipeline,
    LinterRunOptions,
)
from .state_reporter import StateReporter

logger = logging.getLogger(__name__)


def _parse_enabled_tools_env(raw: Optional[str]) -> Optional[Set[str]]:
    if not raw:
        return None
    tokens = {token.strip().lower() for token in raw.split(",") if token.strip()}
    return tokens or None


def _parse_int_env(raw: Optional[str]) -> Optional[int]:
    if raw is None:
        return None
    try:
        value = int(raw.strip())
    except ValueError:
        return None
    return value if value >= 0 else None


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
        self._linters_task: Optional[asyncio.Task[None]] = None
        self._linters_pending = False
        self._linters_disabled = os.environ.get(ENV_DISABLE_LINTERS, "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        tools_env = os.environ.get("CODE_MAP_LINTERS_TOOLS")
        enabled_tools = _parse_enabled_tools_env(tools_env)
        max_files_env = os.environ.get("CODE_MAP_LINTERS_MAX_PROJECT_FILES")
        max_size_env = os.environ.get("CODE_MAP_LINTERS_MAX_PROJECT_SIZE_MB")
        min_interval_env = os.environ.get("CODE_MAP_LINTERS_MIN_INTERVAL_SECONDS")

        max_project_files = _parse_int_env(max_files_env)
        max_project_size_mb = _parse_int_env(max_size_env)
        max_project_bytes = max_project_size_mb * 1024 * 1024 if max_project_size_mb else None

        min_interval = _parse_int_env(min_interval_env)
        self._linters_min_interval = max(0, min_interval or 180)

        self._linters_options = LinterRunOptions(
            enabled_tools=enabled_tools,
            max_project_files=max_project_files,
            max_project_bytes=max_project_bytes,
        )
        self._linters_last_run: Optional[datetime] = None
        self._linters_timer: Optional[asyncio.Task[None]] = None
        self.last_linters_report_id: Optional[int] = None
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
        self._schedule_linters_pipeline()
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def shutdown(self) -> None:
        """Detiene el estado de la aplicación."""
        logger.info("Deteniendo estado de la app")
        self._stop_event.set()
        self._linters_pending = False
        if self._linters_timer:
            self._linters_timer.cancel()
            with suppress(asyncio.CancelledError):
                await self._linters_timer
            self._linters_timer = None
        if self._linters_task:
            await self._linters_task
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
                    self._schedule_linters_pipeline()
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
        self._schedule_linters_pipeline()
        return len(summaries)

    def _schedule_linters_pipeline(self, *, force: bool = False) -> None:
        """Programa la ejecución del pipeline de linters."""
        if self._linters_disabled:
            return
        if self._linters_task and not self._linters_task.done():
            self._linters_pending = True
            return
        if not force:
            if self.scheduler.pending_count() > 0:
                self._linters_pending = True
                return

            if self._linters_min_interval and self._linters_last_run is not None:
                elapsed = (datetime.now(timezone.utc) - self._linters_last_run).total_seconds()
                remaining = self._linters_min_interval - elapsed
                if remaining > 0:
                    self._linters_pending = True
                    if self._linters_timer is None or self._linters_timer.done():
                        self._linters_timer = asyncio.create_task(self._schedule_linters_pipeline_later(remaining))
                    return

        self._linters_pending = False
        self._linters_task = asyncio.create_task(self._run_linters_pipeline())

    async def _run_linters_pipeline(self) -> None:
        """Ejecuta el pipeline de linters y persiste el resultado."""
        try:
            report = await asyncio.to_thread(
                run_linters_pipeline,
                self.settings.root_path,
                options=self._linters_options,
            )
            report_id = record_linters_report(report)
            self.last_linters_report_id = report_id
            summary = report.summary
            status = summary.overall_status
            self._linters_last_run = datetime.now(timezone.utc)

            if status in {CheckStatus.FAIL, CheckStatus.WARN, CheckStatus.SKIPPED}:
                if status == CheckStatus.FAIL:
                    severity = Severity.CRITICAL if summary.critical_issues else Severity.HIGH
                    message = (
                        f"{summary.issues_total} incidencias detectadas (críticas: {summary.critical_issues})."
                        if summary.issues_total
                        else "El pipeline falló. Revisa la salida de las herramientas."
                    )
                elif status == CheckStatus.WARN:
                    severity = Severity.MEDIUM
                    message = (
                        f"{summary.issues_total} advertencias encontradas."
                        if summary.issues_total
                        else "El pipeline reportó advertencias."
                    )
                else:
                    severity = Severity.LOW
                    message = "No se pudieron ejecutar las herramientas configuradas."

                record_notification(
                    channel="linters",
                    severity=severity,
                    title=f"Pipeline de linters: {status.value.upper()}",
                    message=message,
                    root_path=self.settings.root_path,
                    payload={
                        "report_id": report_id,
                        "status": status.value,
                        "issues_total": summary.issues_total,
                        "critical_issues": summary.critical_issues,
                    },
                )
        except Exception:  # pragma: no cover - logging del pipeline
            logger.exception("Error al ejecutar el pipeline de linters")
        finally:
            self._linters_task = None
            if self._linters_timer and self._linters_timer.done():
                self._linters_timer = None
            if self._linters_pending:
                self._linters_pending = False
                self._schedule_linters_pipeline()

    async def _schedule_linters_pipeline_later(self, delay: float) -> None:
        try:
            await asyncio.sleep(max(delay, 0))
            if self._stop_event.is_set():
                return
            self._linters_timer = None
            self._schedule_linters_pipeline(force=True)
        except asyncio.CancelledError:
            self._linters_timer = None
            raise

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
        ollama_insights_enabled: Optional[bool] = None,
        ollama_insights_model: Optional[str] = None,
        ollama_insights_frequency_minutes: Optional[int] = None,
    ) -> List[str]:
        """Actualiza la configuración de la aplicación."""
        if ollama_insights_frequency_minutes is not None:
            if ollama_insights_frequency_minutes <= 0:
                raise ValueError("La frecuencia de insights debe ser un entero positivo.")
            if ollama_insights_frequency_minutes > 24 * 60:
                raise ValueError("La frecuencia de insights no puede superar 1440 minutos.")

        new_settings = self.settings.with_updates(
            root_path=root_path,
            include_docstrings=include_docstrings,
            exclude_dirs=exclude_dirs,
            ollama_insights_enabled=ollama_insights_enabled,
            ollama_insights_model=ollama_insights_model,
            ollama_insights_frequency_minutes=ollama_insights_frequency_minutes,
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
        if new_settings.ollama_insights_enabled != self.settings.ollama_insights_enabled:
            updated_fields.append("ollama_insights_enabled")
        if new_settings.ollama_insights_model != self.settings.ollama_insights_model:
            updated_fields.append("ollama_insights_model")
        if (
            new_settings.ollama_insights_frequency_minutes
            != self.settings.ollama_insights_frequency_minutes
        ):
            updated_fields.append("ollama_insights_frequency_minutes")

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
