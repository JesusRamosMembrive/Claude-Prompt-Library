# SPDX-License-Identifier: MIT
"""
Planificador de eventos de cambio para reprocesar archivos con debounce.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Deque, Dict, Iterable, Iterator, Optional

from .events import ChangeBatch, ChangeEventType, FileChangeEvent

DEFAULT_DEBOUNCE_SECONDS = 0.25


@dataclass(slots=True)
class _QueuedEvent:
    """Representa un evento pendiente dentro del debounce."""
    event_type: ChangeEventType
    src_path: Path
    dest_path: Optional[Path] = None

    def to_public(self) -> FileChangeEvent:
        """Convierte el evento interno en un FileChangeEvent expuesto."""
        return FileChangeEvent(
            event_type=self.event_type,
            src_path=self.src_path,
            dest_path=self.dest_path,
        )


class ChangeScheduler:
    """
    Acumula eventos del watcher, aplica debounce y entrega lotes listos para reprocesar.
    """

    def __init__(
        self,
        *,
        debounce_seconds: float = DEFAULT_DEBOUNCE_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.debounce_seconds = debounce_seconds
        self._clock = clock
        self._queue: Deque[_QueuedEvent] = deque()
        self._lock = threading.Lock()
        self._last_dispatch = 0.0

    def enqueue(
        self,
        event_type: ChangeEventType,
        src_path: Path,
        *,
        dest_path: Optional[Path] = None,
    ) -> None:
        """Añade un evento a la cola interna aplicando normalización."""
        event = _QueuedEvent(
            event_type=event_type,
            src_path=Path(src_path).resolve(),
            dest_path=Path(dest_path).resolve() if dest_path else None,
        )
        with self._lock:
            self._queue.append(event)

    def drain(self, *, force: bool = False) -> Optional[ChangeBatch]:
        """
        Devuelve un `ChangeBatch` cuando haya pasado el debounce o si se fuerza.
        Si no hay eventos listos devuelve `None`.
        """
        with self._lock:
            if not self._queue:
                return None

            now = self._clock()
            if not force and (now - self._last_dispatch) < self.debounce_seconds:
                return None

            events = list(self._queue)
            self._queue.clear()
            self._last_dispatch = now

        collapsed = self._collapse_events(events)
        batch = ChangeBatch.from_events(collapsed)
        return batch if not batch.is_empty() else None

    def pending_count(self) -> int:
        """Devuelve la cantidad de eventos pendientes en la cola."""
        with self._lock:
            return len(self._queue)

    def clear(self) -> None:
        """Vacía la cola de eventos pendientes."""
        with self._lock:
            self._queue.clear()

    def _collapse_events(
        self, events: Iterable[_QueuedEvent]
    ) -> Iterator[FileChangeEvent]:
        """Simplifica la secuencia de eventos acumulados en su forma mínima."""
        state: Dict[Path, FileChangeEvent] = {}

        for event in events:
            if event.event_type is ChangeEventType.MOVED:
                src = event.src_path
                dest = event.dest_path
                if dest:
                    state[src] = FileChangeEvent(ChangeEventType.DELETED, src)
                    state[dest] = FileChangeEvent(ChangeEventType.CREATED, dest)
                else:
                    state[src] = FileChangeEvent(ChangeEventType.DELETED, src)
                continue

            current = state.get(event.src_path)
            incoming = event.event_type

            if incoming is ChangeEventType.CREATED:
                state[event.src_path] = FileChangeEvent(
                    ChangeEventType.CREATED, event.src_path
                )
            elif incoming is ChangeEventType.MODIFIED:
                if current and current.event_type is ChangeEventType.CREATED:
                    # mantener estado de creado (un archivo recién creado no necesita doble evento)
                    continue
                state[event.src_path] = FileChangeEvent(
                    ChangeEventType.MODIFIED, event.src_path
                )
            elif incoming is ChangeEventType.DELETED:
                state[event.src_path] = FileChangeEvent(
                    ChangeEventType.DELETED, event.src_path
                )

        return state.values()
