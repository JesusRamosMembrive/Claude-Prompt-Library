# SPDX-License-Identifier: MIT
"""Funciones de soporte para generar insights con Ollama."""

from __future__ import annotations

from .ollama_service import OllamaInsightResult, run_ollama_insights
from .storage import record_insight, list_insights, clear_insights, StoredInsight

__all__ = [
    "OllamaInsightResult",
    "run_ollama_insights",
    "StoredInsight",
    "record_insight",
    "list_insights",
    "clear_insights",
]
