# SPDX-License-Identifier: MIT
"""
Utilidades para inicializar y verificar los archivos Stage-Aware
que consumen Claude Code y Codex CLI.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Optional, Sequence, Tuple, TYPE_CHECKING

from stage_config import StageMetrics, collect_metrics

if TYPE_CHECKING:  # pragma: no cover
    from .index import SymbolIndex

AgentSelection = Literal["claude", "codex", "both"]

CLAUDE_REQUIRED: Tuple[str, ...] = (
    ".claude/00-project-brief.md",
    ".claude/01-current-phase.md",
    ".claude/02-stage1-rules.md",
    ".claude/02-stage2-rules.md",
    ".claude/02-stage3-rules.md",
    ".claude/agents/architect-generic.md",
    ".claude/agents/code-reviewer-optimized.md",
    ".claude/agents/implementer.md",
    ".claude/agents/stage-keeper-architecture.md",
)

CLAUDE_OPTIONAL: Tuple[str, ...] = (
    "CLAUDE.md",
    ".claude/settings.local.json",
)

CODEX_REQUIRED: Tuple[str, ...] = (
    ".codex/AGENTS.md",
    ".codex/stage1-rules.md",
    ".codex/stage2-rules.md",
    ".codex/stage3-rules.md",
)

DOCS_REQUIRED: Tuple[str, ...] = (
    "docs/QUICK_START.md",
    "docs/STAGES_COMPARISON.md",
    "docs/STAGE_CRITERIA.md",
    "docs/GUIDE.md",
    "docs/CLAUDE_CODE_REFERENCE.md",
    "docs/CODEX_CLI_REFERENCE.md",
)


@dataclass
class FileStatus:
    """Representa el estado de un conjunto de archivos esperados."""

    expected: Tuple[str, ...]
    present: List[str]
    missing: List[str]

    @property
    def complete(self) -> bool:
        return not self.missing


def _collect_file_status(root: Path, required: Sequence[str]) -> FileStatus:
    present: List[str] = []
    missing: List[str] = []
    for relative in required:
        path = (root / relative).resolve()
        if path.exists():
            present.append(relative)
        else:
            missing.append(relative)
    return FileStatus(expected=tuple(required), present=present, missing=missing)


def _build_agent_payload(
    root: Path, required: Tuple[str, ...], optional: Tuple[str, ...] = ()
) -> Dict[str, object]:
    mandatory = _collect_file_status(root, required)
    optional_status = (
        _collect_file_status(root, optional)
        if optional
        else FileStatus(optional, [], [])
    )
    return {
        "expected": list(mandatory.expected),
        "present": mandatory.present,
        "missing": mandatory.missing,
        "optional": {
            "expected": list(optional_status.expected),
            "present": optional_status.present,
            "missing": optional_status.missing,
        },
        "installed": mandatory.complete,
    }


def _detect_stage(
    root: Path, *, metrics: Optional[StageMetrics] = None
) -> Dict[str, object]:
    try:
        import assess_stage  # noqa: WPS433 (import at runtime)
    except Exception as exc:  # pragma: no cover - fallback path
        return {
            "available": False,
            "error": f"assess_stage no disponible: {exc}",
            "recommended_stage": None,
            "confidence": None,
            "reasons": [],
            "metrics": None,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    try:
        assessment = assess_stage.assess_stage(root, metrics=metrics)
    except Exception as exc:  # pragma: no cover - runtime errors
        return {
            "available": False,
            "error": f"Error al evaluar la etapa: {exc}",
            "recommended_stage": None,
            "confidence": None,
            "reasons": [],
            "metrics": None,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    if not assessment:
        return {
            "available": False,
            "error": "No se pudo determinar la etapa del proyecto.",
            "recommended_stage": None,
            "confidence": None,
            "reasons": [],
            "metrics": None,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "available": True,
        "error": None,
        "recommended_stage": assessment.get("recommended_stage"),
        "confidence": assessment.get("confidence"),
        "reasons": assessment.get("reasons", [])[:5],
        "metrics": assessment.get("metrics"),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def _compute_status(
    root: Path, metrics: Optional[StageMetrics] = None
) -> Dict[str, object]:
    resolved_root = root.expanduser().resolve()
    claude_payload = _build_agent_payload(
        resolved_root, CLAUDE_REQUIRED, CLAUDE_OPTIONAL
    )
    codex_payload = _build_agent_payload(resolved_root, CODEX_REQUIRED)
    docs_status = _collect_file_status(resolved_root, DOCS_REQUIRED)

    return {
        "root_path": str(resolved_root),
        "claude": claude_payload,
        "codex": codex_payload,
        "docs": {
            "expected": list(docs_status.expected),
            "present": docs_status.present,
            "missing": docs_status.missing,
            "complete": docs_status.complete,
        },
        "detection": _detect_stage(resolved_root, metrics=metrics),
    }


async def stage_status(
    root: Path, *, index: Optional["SymbolIndex"] = None
) -> Dict[str, object]:
    """Obtiene el estado actual de los archivos stage-aware para un root dado."""
    metrics: Optional[StageMetrics] = None
    if index is not None:
        metrics = await asyncio.to_thread(collect_metrics, root, symbol_index=index)
    return await asyncio.to_thread(_compute_status, root, metrics)


async def run_initializer(root: Path, agents: AgentSelection) -> Dict[str, object]:
    """
    Ejecuta init_project.py contra el root indicado para instalar instrucciones.
    """
    from asyncio.subprocess import PIPE  # noqa: WPS433

    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "init_project.py"
    target = root.expanduser().resolve()

    command = [sys.executable, str(script_path), str(target), "--existing"]
    if agents in {"claude", "codex"}:
        command.extend(["--agent", agents])
    else:
        # explicitar para mantener coherencia aunque el default sea ambos
        command.extend(["--agent", "both"])
    command.append("--skip-claude-init")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=PIPE,
        stderr=PIPE,
        cwd=str(repo_root),
    )
    stdout_bytes, stderr_bytes = await process.communicate()

    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")

    status_payload = await stage_status(target)

    return {
        "success": process.returncode == 0,
        "exit_code": process.returncode,
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
        "status": status_payload,
    }
