# SPDX-License-Identifier: MIT
"""
Tipos y utilidades relacionadas con cambios en el filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


class ChangeEventType(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass(slots=True)
class FileChangeEvent:
    event_type: ChangeEventType
    src_path: Path
    dest_path: Optional[Path] = None

    def normalize(self) -> "FileChangeEvent":
        return FileChangeEvent(
            event_type=self.event_type,
            src_path=self.src_path.resolve(),
            dest_path=self.dest_path.resolve() if self.dest_path else None,
        )


@dataclass(slots=True)
class ChangeBatch:
    created: List[Path] = field(default_factory=list)
    modified: List[Path] = field(default_factory=list)
    deleted: List[Path] = field(default_factory=list)
    moved: List[Tuple[Path, Path]] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.created or self.modified or self.deleted or self.moved)

    def __bool__(self) -> bool:
        return not self.is_empty()

    @staticmethod
    def from_events(events: Iterable[FileChangeEvent]) -> "ChangeBatch":
        batch = ChangeBatch()
        for event in events:
            if event.event_type is ChangeEventType.CREATED:
                batch.created.append(event.src_path)
            elif event.event_type is ChangeEventType.MODIFIED:
                batch.modified.append(event.src_path)
            elif event.event_type is ChangeEventType.DELETED:
                batch.deleted.append(event.src_path)
            elif event.event_type is ChangeEventType.MOVED and event.dest_path:
                batch.moved.append((event.src_path, event.dest_path))
        return batch


def is_python_file(path: Path) -> bool:
    return path.suffix == ".py"
