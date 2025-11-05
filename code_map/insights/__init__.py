# SPDX-License-Identifier: MIT
"""Funciones de soporte para generar insights con Ollama."""

from __future__ import annotations

from .ollama_service import (
    OllamaInsightResult,
    run_ollama_insights,
    DEFAULT_INSIGHTS_FOCUS,
    INSIGHTS_FOCUS_PROMPTS,
    VALID_INSIGHTS_FOCUS,
    build_insights_prompt,
    OLLAMA_DEFAULT_TIMEOUT,
)
from .storage import record_insight, list_insights, clear_insights, StoredInsight

__all__ = [
    "OllamaInsightResult",
    "run_ollama_insights",
    "DEFAULT_INSIGHTS_FOCUS",
    "INSIGHTS_FOCUS_PROMPTS",
    "VALID_INSIGHTS_FOCUS",
    "build_insights_prompt",
    "OLLAMA_DEFAULT_TIMEOUT",
    "StoredInsight",
    "record_insight",
    "list_insights",
    "clear_insights",
]
