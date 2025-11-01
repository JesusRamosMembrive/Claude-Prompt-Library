"""
Shared configuration, thresholds, and helpers for stage detection logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from code_map.index import SymbolIndex
    from code_map.models import FileSummary

# ---------------------------------------------------------------------------
# Stage metadata


@dataclass(frozen=True)
class StageThresholds:
    """Thresholds that describe boundaries for a project stage."""

    max_files: Optional[int]
    max_loc: Optional[int]
    max_patterns: Optional[int]
    max_arch_layers: Optional[int]


@dataclass(frozen=True)
class StageDefinition:
    """Declarative metadata for a stage."""

    number: int
    label: str
    description: str
    thresholds: StageThresholds


STAGE_DEFINITIONS: Tuple[StageDefinition, ...] = (
    StageDefinition(
        number=1,
        label="Prototyping",
        description="Mantén todo simple. Una sola pieza de código para validar la idea.",
        thresholds=StageThresholds(
            max_files=3,
            max_loc=500,
            max_patterns=0,
            max_arch_layers=0,
        ),
    ),
    StageDefinition(
        number=2,
        label="Structuring",
        description="Divide el código cuando duela. Añade estructura ligera y máximo 1–2 patrones.",
        thresholds=StageThresholds(
            max_files=20,
            max_loc=3000,
            max_patterns=3,
            max_arch_layers=3,
        ),
    ),
    StageDefinition(
        number=3,
        label="Scaling",
        description="Patrones y arquitectura completa son válidos si resuelven dolores reales.",
        thresholds=StageThresholds(
            max_files=None,
            max_loc=None,
            max_patterns=None,
            max_arch_layers=None,
        ),
    ),
)

# ---------------------------------------------------------------------------
# Pattern and structure heuristics

PATTERN_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "Factory Pattern": ("factory", "Factory", "create_"),
    "Singleton": ("singleton", "Singleton", "getInstance"),
    "Observer": ("observer", "Observer", "subscribe", "emit"),
    "Strategy": ("strategy", "Strategy"),
    "Repository": ("repository", "Repository", "repo"),
    "Service Layer": ("service", "Service", "services/"),
    "Adapter": ("adapter", "Adapter", "adapters/"),
    "Middleware": ("middleware", "Middleware"),
}

ARCHITECTURE_FOLDERS: Tuple[str, ...] = (
    "models",
    "views",
    "controllers",
    "services",
    "repositories",
    "middleware",
    "adapters",
    "interfaces",
    "handlers",
    "routers",
    "api",
    "core",
    "domain",
    "infrastructure",
    "application",
    "presentation",
)

IGNORE_DIRS: Set[str] = {
    ".venv",
    "venv",
    "env",
    "ENV",
    "node_modules",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "build",
    "dist",
    ".eggs",
    "*.egg-info",
    ".tox",
    ".nox",
    "htmlcov",
    ".coverage",
    ".idea",
    ".vscode",
    "target",
    "bin",
    "obj",
    "CMakeFiles",
    "cmake-build-debug",
    "cmake-build-release",
    ".qmake.stash",
}

DEFAULT_CODE_EXTENSIONS: Tuple[str, ...] = (
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".h",
    ".hpp",
    ".hxx",
)

# ---------------------------------------------------------------------------
# Metrics and diagnostics


@dataclass(frozen=True)
class StageMetrics:
    """Aggregated metrics used to evaluate which stage fits best."""

    file_count: int
    lines_of_code: int
    directory_count: int
    patterns_found: List[str]
    architectural_folders: List[str]


@dataclass(frozen=True)
class StageDiagnostics:
    """Additional data explaining how a stage recommendation was produced."""

    applied_stage: StageDefinition
    warnings: Tuple[str, ...]


@dataclass(frozen=True)
class StageAssessment:
    """Final evaluation result with metrics and justification."""

    recommended_stage: int
    confidence: str
    reasons: List[str]
    metrics: StageMetrics
    diagnostics: StageDiagnostics


# ---------------------------------------------------------------------------
# Public helpers


def should_ignore(path: Path) -> bool:
    """Return True when any segment of the path is an ignored folder."""

    return any(part.startswith(".") or part in IGNORE_DIRS for part in path.parts)


def collect_metrics(
    root: Path,
    *,
    symbol_index: Optional["SymbolIndex"] = None,
    extensions: Sequence[str] = DEFAULT_CODE_EXTENSIONS,
) -> StageMetrics:
    """
    Collect project metrics needed for stage evaluation.

    If `symbol_index` is provided, it will be used as the primary source for files.
    """

    root = root.expanduser().resolve()
    extension_set = {ext if ext.startswith(".") else f".{ext}" for ext in extensions}

    files: List[Path] = []
    if symbol_index:
        summaries = _filter_summaries(symbol_index.get_all(), root, extension_set)
        files = [summary.path for summary in summaries]

    if not files:
        files = list(_iter_code_files(root, extension_set))

    unique_files = sorted(set(files))
    file_count = len(unique_files)
    loc = sum(_count_file_lines(path) for path in unique_files)

    directories: Set[Path] = set()
    for path in unique_files:
        try:
            path.relative_to(root)
        except ValueError:
            continue
        directories.add(path.parent)
    directory_count = len(directories)

    patterns = detect_patterns(unique_files, root)
    architecture = detect_architectural_folders(root, directories)

    return StageMetrics(
        file_count=file_count,
        lines_of_code=loc,
        directory_count=directory_count,
        patterns_found=patterns,
        architectural_folders=architecture,
    )


def evaluate_stage(metrics: StageMetrics) -> StageAssessment:
    """Evaluate the provided metrics and return a stage recommendation."""

    reasons: List[str] = []
    warnings: List[str] = []

    definition = _select_stage_definition(metrics, reasons)
    confidence = _determine_confidence(metrics, definition, warnings, reasons)

    _append_substage_hint(metrics, definition, reasons)

    diagnostics = StageDiagnostics(applied_stage=definition, warnings=tuple(warnings))
    return StageAssessment(
        recommended_stage=definition.number,
        confidence=confidence,
        reasons=reasons,
        metrics=metrics,
        diagnostics=diagnostics,
    )


def detect_patterns(files: Iterable[Path], root: Path) -> List[str]:
    """Detect design patterns using simple filename heuristics."""

    root = root.expanduser().resolve()
    matches: Set[str] = set()

    for pattern, keywords in PATTERN_KEYWORDS.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if any(keyword_lower in segment.lower() for path in files for segment in path.parts):
                matches.add(pattern)
                break

    return sorted(matches)


def detect_architectural_folders(root: Path, directories: Iterable[Path]) -> List[str]:
    """Detect architectural folder names inside the project."""

    found: Set[str] = set()
    for directory in directories:
        try:
            relative = directory.relative_to(root)
        except ValueError:
            relative = directory
        if should_ignore(relative):
            continue
        dirname = directory.name.lower()
        for marker in ARCHITECTURE_FOLDERS:
            if marker in dirname:
                found.add(marker)
                break
    return sorted(found)


# ---------------------------------------------------------------------------
# Internal helpers


def _filter_summaries(
    summaries: Iterable["FileSummary"],
    root: Path,
    extensions: Set[str],
) -> List["FileSummary"]:
    filtered: List["FileSummary"] = []
    for summary in summaries:
        path = summary.path.resolve()
        if not path.suffix or path.suffix.lower() not in extensions:
            continue
        try:
            relative = path.relative_to(root)
        except ValueError:
            # File is outside root; ignore it for stage heuristics
            continue
        if should_ignore(relative):
            continue
        filtered.append(summary)
    return filtered


def _iter_code_files(root: Path, extensions: Set[str]) -> Iterator[Path]:
    for ext in extensions:
        yield from (
            path
            for path in root.rglob(f"*{ext}")
            if _path_within_root(path, root)
            and not should_ignore(path.relative_to(root))
        )


def _count_file_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def _path_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _select_stage_definition(metrics: StageMetrics, reasons: List[str]) -> StageDefinition:
    files = metrics.file_count
    loc = metrics.lines_of_code
    patterns = len(metrics.patterns_found)
    layers = len(metrics.architectural_folders)

    stage = STAGE_DEFINITIONS[-1]

    for definition in STAGE_DEFINITIONS:
        thresholds = definition.thresholds

        files_ok = thresholds.max_files is None or files <= thresholds.max_files
        loc_ok = thresholds.max_loc is None or loc < thresholds.max_loc
        patterns_ok = thresholds.max_patterns is None or patterns <= thresholds.max_patterns
        layers_ok = thresholds.max_arch_layers is None or layers <= thresholds.max_arch_layers

        if files_ok and loc_ok and patterns_ok and layers_ok:
            stage = definition
            break

    if stage.number == 1:
        reasons.append(f"Very small codebase ({files} files, ~{loc} LOC)")
        reasons.append("Appropriate for prototyping stage")
    elif stage.number == 2:
        reasons.append(f"Medium codebase ({files} files, ~{loc} LOC)")
        if metrics.architectural_folders:
            arch_count = len(metrics.architectural_folders)
            reasons.append(f"Basic architecture present: {arch_count} layer(s)")
            if arch_count > 3:
                reasons.append("⚠️  Consider if architecture is justified")
            else:
                reasons.append("Structure is appropriate for Stage 2")
        else:
            reasons.append("No clear architecture yet - good for Stage 2")

        if metrics.patterns_found:
            joined = ", ".join(metrics.patterns_found[:2])
            reasons.append(f"Some patterns in use: {joined}")
            if len(metrics.patterns_found) > 2:
                reasons.append("⚠️  Multiple patterns - ensure they're justified")
        else:
            reasons.append("No design patterns detected yet")
    else:
        reasons.append(f"Large or complex codebase ({files} files, ~{loc} LOC)")
        if metrics.patterns_found:
            reasons.append(f"Multiple patterns detected: {', '.join(metrics.patterns_found[:4])}")
        if len(metrics.architectural_folders) > 4:
            reasons.append(f"Complex architecture: {len(metrics.architectural_folders)} layers")

    return stage


def _determine_confidence(
    metrics: StageMetrics,
    definition: StageDefinition,
    warnings: List[str],
    reasons: List[str],
) -> str:
    confidence = "high"

    if metrics.file_count <= 5 and metrics.lines_of_code > 1500:
        confidence = "medium"
        warnings.append("Few files but high LOC - consider refactoring into smaller modules")
        reasons.append("⚠️  Few files but high LOC - consider refactoring")

    if metrics.file_count > 30 and not metrics.patterns_found:
        confidence = "medium"
        warnings.append("Many files without clear patterns - structure might be missing")
        reasons.append("⚠️  Many files but no patterns - may need structure")

    return confidence


def _append_substage_hint(metrics: StageMetrics, definition: StageDefinition, reasons: List[str]) -> None:
    if definition.number != 2:
        return

    files = metrics.file_count
    loc = metrics.lines_of_code

    if files <= 8 and loc < 1000:
        reasons.append("📍 Early Stage 2 - just starting to structure")
    elif files <= 15 and loc < 2000:
        reasons.append("📍 Mid Stage 2 - structure emerging")
    else:
        reasons.append("📍 Late Stage 2 - consider Stage 3 transition")
