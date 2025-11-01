"""
Utilities for working with template files used during project initialization.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

logger = logging.getLogger(__name__)


@dataclass
class TemplateSummary:
    """Tracks copied and skipped template files."""

    copied: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)
    updated: List[Path] = field(default_factory=list)

    def record_copied(self, path: Path) -> None:
        self.copied.append(path)

    def record_skipped(self, path: Path) -> None:
        self.skipped.append(path)

    def record_updated(self, path: Path) -> None:
        self.updated.append(path)

    def merge(self, other: "TemplateSummary") -> "TemplateSummary":
        self.copied.extend(other.copied)
        self.skipped.extend(other.skipped)
        self.updated.extend(other.updated)
        return self


def copy_templates(
    sources: Mapping[str, Path],
    destinations: Mapping[str, Path],
    *,
    placeholders: Optional[MutableMapping[str, str]] = None,
    dry_run: bool = False,
    logger_override: Optional[logging.Logger] = None,
) -> Dict[str, TemplateSummary]:
    """
    Copy template files category by category.

    Args:
        sources: Mapping from category name to template directory.
        destinations: Mapping from category name to destination directory.
        placeholders: Placeholder substitutions to apply (only for newly copied files).
        dry_run: If True, no filesystem changes will be made.
    """

    log = logger_override or logger
    outcomes: Dict[str, TemplateSummary] = {}

    for category, source_dir in sources.items():
        dest_dir = destinations.get(category)
        if dest_dir is None:
            raise ValueError(f"No destination configured for category '{category}'")
        summary = TemplateSummary()
        outcomes[category] = summary

        if not source_dir.exists():
            log.warning("Template directory missing for %s: %s", category, source_dir)
            continue

        _ensure_directory(dest_dir, dry_run=dry_run, log=log)

        for template_file in source_dir.iterdir():
            if template_file.is_dir():
                summary.merge(
                    _copy_directory(
                        template_file,
                        dest_dir / template_file.name,
                        placeholders=placeholders,
                        dry_run=dry_run,
                        log=log,
                    )
                )
            else:
                _copy_file(
                    template_file,
                    dest_dir / template_file.name,
                    summary,
                    placeholders=placeholders,
                    dry_run=dry_run,
                    log=log,
                )

    return outcomes


def _copy_directory(
    source_dir: Path,
    dest_dir: Path,
    *,
    placeholders: Optional[MutableMapping[str, str]],
    dry_run: bool,
    log: logging.Logger,
) -> TemplateSummary:
    summary = TemplateSummary()
    if not source_dir.exists():
        log.warning("Directory not found: %s", source_dir)
        return summary

    _ensure_directory(dest_dir, dry_run=dry_run, log=log)

    for item in source_dir.iterdir():
        destination = dest_dir / item.name
        if item.is_dir():
            summary.merge(
                _copy_directory(
                    item,
                    destination,
                    placeholders=placeholders,
                    dry_run=dry_run,
                    log=log,
                )
            )
        else:
            _copy_file(
                item,
                destination,
                summary,
                placeholders=placeholders,
                dry_run=dry_run,
                log=log,
            )
    return summary


def _copy_file(
    source: Path,
    destination: Path,
    summary: TemplateSummary,
    *,
    placeholders: Optional[MutableMapping[str, str]],
    dry_run: bool,
    log: logging.Logger,
) -> None:
    if destination.exists():
        log.debug("Skipping existing file: %s", destination)
        summary.record_skipped(destination)
        return

    if dry_run:
        log.info("[dry-run] Would copy %s -> %s", source, destination)
        summary.record_copied(destination)
        return

    log.info("Copying %s -> %s", source, destination)
    _ensure_directory(destination.parent, dry_run=False, log=log)
    shutil.copy2(source, destination)

    if placeholders:
        _apply_placeholders(destination, placeholders, log=log)

    summary.record_copied(destination)


def _apply_placeholders(
    target: Path,
    placeholders: Mapping[str, str],
    *,
    log: logging.Logger,
) -> None:
    try:
        content = target.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        log.debug("Skipping placeholder replacement for %s (%s)", target, exc)
        return

    for key, value in placeholders.items():
        content = content.replace(key, value)

    try:
        target.write_text(content, encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        log.warning("Unable to write %s after placeholder replacement: %s", target, exc)


def _ensure_directory(path: Path, *, dry_run: bool, log: logging.Logger) -> None:
    if path.exists():
        return
    if dry_run:
        log.info("[dry-run] Would create directory: %s", path)
        return
    path.mkdir(parents=True, exist_ok=True)
