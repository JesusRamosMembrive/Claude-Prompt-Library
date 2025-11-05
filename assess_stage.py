#!/usr/bin/env python3
"""
Stage Assessment Tool
Analyzes an existing project and suggests the appropriate development stage.
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Literal, overload

from typing import TYPE_CHECKING

from stage_config import (
    DEFAULT_CODE_EXTENSIONS,
    STAGE_DEFINITIONS,
    StageAssessment,
    StageDiagnostics,
    StageMetrics,
    collect_metrics,
    evaluate_stage,
)

if TYPE_CHECKING:  # pragma: no cover
    from code_map.index import SymbolIndex
else:
    SymbolIndex = Any  # type: ignore


@overload
def assess_stage(  # noqa: D401 - keep compatibility
    project_path: str | Path,
    *,
    metrics: Optional[StageMetrics] = None,
    symbol_index: Optional["SymbolIndex"] = None,
    extensions: Optional[Sequence[str]] = None,
    return_dataclass: Literal[True],
) -> Optional[StageAssessment]: ...


@overload
def assess_stage(
    project_path: str | Path,
    *,
    metrics: Optional[StageMetrics] = None,
    symbol_index: Optional["SymbolIndex"] = None,
    extensions: Optional[Sequence[str]] = None,
    return_dataclass: Literal[False] = False,
) -> Optional[Dict[str, Any]]: ...


def assess_stage(
    project_path: str | Path,
    *,
    metrics: Optional[StageMetrics] = None,
    symbol_index: Optional["SymbolIndex"] = None,
    extensions: Optional[Sequence[str]] = None,
    return_dataclass: bool = False,
) -> Optional[Dict[str, Any] | StageAssessment]:
    """
    Assess project and recommend development stage.

    Compatibility wrapper returning dictionaries by default (for existing callers)
    while exposing the new dataclass via `return_dataclass=True`.
    """

    root = Path(project_path).expanduser().resolve()
    if not root.exists():
        return None

    if metrics is None:
        metrics = collect_metrics(
            root,
            symbol_index=symbol_index,
            extensions=extensions or DEFAULT_CODE_EXTENSIONS,
        )

    assessment = evaluate_stage(metrics)
    if return_dataclass:
        return assessment
    return _assessment_to_payload(assessment)


def _assessment_to_payload(assessment: StageAssessment) -> Dict[str, Any]:
    diagnostics: StageDiagnostics = assessment.diagnostics
    payload = {
        "recommended_stage": assessment.recommended_stage,
        "confidence": assessment.confidence,
        "reasons": assessment.reasons,
        "metrics": asdict(assessment.metrics),
        "diagnostics": {
            "stage_label": diagnostics.applied_stage.label,
            "description": diagnostics.applied_stage.description,
            "thresholds": asdict(diagnostics.applied_stage.thresholds),
            "warnings": list(diagnostics.warnings),
        },
    }
    return payload


def print_assessment(assessment: Optional[Dict[str, Any]]) -> None:
    """
    Pretty print assessment results to console.

    Formats and displays stage assessment results in a readable format with
    emojis, metrics, reasoning, and actionable next steps.
    """

    if not assessment:
        print("❌ Could not assess project")
        return

    stage_number = assessment["recommended_stage"]
    confidence = assessment["confidence"]
    metrics = assessment["metrics"]
    reasons = assessment["reasons"]
    diagnostics = assessment.get("diagnostics", {})

    stage_def = next((d for d in STAGE_DEFINITIONS if d.number == stage_number), None)

    conf_emoji = {
        "high": "✅",
        "medium": "⚠️",
        "low": "❓",
    }.get(confidence, "❓")

    print("\n" + "=" * 60)
    print("🎯 STAGE ASSESSMENT RESULTS")
    print("=" * 60)

    label = stage_def.label if stage_def else f"Stage {stage_number}"
    print(f"\n📊 Recommended Stage: {stage_number} - {label}")
    print(f"{conf_emoji} Confidence: {confidence.upper()}")

    print("\n📈 Project Metrics:")
    print(f"  - Code Files: {metrics['file_count']}")
    print(f"  - Lines of Code: ~{metrics['lines_of_code']}")
    print(f"  - Directories: {metrics['directory_count']}")

    if metrics.get("patterns_found"):
        print(f"  - Patterns Detected: {', '.join(metrics['patterns_found'])}")
    if metrics.get("architectural_folders"):
        arch = metrics["architectural_folders"]
        print(f"  - Architecture: {', '.join(arch[:6])}")

    print("\n💡 Reasoning:")
    for reason in reasons:
        print(f"  • {reason}")

    print("\n📚 What This Means:")
    if stage_def:
        print(f"  Stage {stage_def.number} ({stage_def.label}):")
        print(f"  - {stage_def.description}")
    else:
        print("  Stage metadata not available.")

    print("\n📖 Next Steps:")
    print(f"  1. Review .claude/02-stage{stage_number}-rules.md")
    print("  2. Update .claude/01-current-phase.md with current stage")
    print("  3. Follow stage-appropriate practices")

    warnings = diagnostics.get("warnings", [])
    if warnings:
        print("\n⚠️  Diagnostics:")
        for item in warnings:
            print(f"  - {item}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assess_stage.py <project-path>")
        print("\nExamples:")
        print("  python assess_stage.py .")
        print("  python assess_stage.py /path/to/my-project")
        print("\nNote: Automatically ignores .venv, node_modules, .git, etc.")
        sys.exit(1)

    project_path = sys.argv[1]

    print(f"🔍 Analyzing project: {project_path}")
    print("   (using shared stage configuration)")

    assessment = assess_stage(project_path)
    print_assessment(assessment)
