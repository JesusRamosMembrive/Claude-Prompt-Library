# SPDX-License-Identifier: MIT
"""Ejecución de análisis automáticos asistidos por Ollama."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..integrations import OllamaChatError, OllamaChatMessage, chat_with_ollama, OllamaChatResponse

logger = logging.getLogger(__name__)


INSIGHTS_SYSTEM_PROMPT = (
    "Eres un asistente que revisa periódicamente un repositorio para detectar mejoras. "
    "Responde en español con un resumen breve de acciones útiles (máximo 5 viñetas)."
)

DEFAULT_INSIGHTS_FOCUS = "general"

INSIGHTS_FOCUS_PROMPTS = {
    "general": (
        "Analiza el estado actual del repositorio en {root}. Sugiere refactors, soluciones "
        "para problemas de linters y patrones de diseño relevantes. Si no tienes contexto, "
        "propón pasos generales."
    ),
    "refactors": (
        "Analiza el repositorio en {root} y prioriza la detección de oportunidades de refactor. "
        "Propón simplificaciones, extracción de módulos y mejoras de legibilidad. "
        "Incluye recomendaciones concretas sobre archivos o componentes a ajustar."
    ),
    "issues": (
        "Revisa el repositorio en {root} buscando señales de fallos potenciales, manejo deficiente "
        "de errores, dependencias frágiles o comportamientos inconsistentes. "
        "Sugiere verificaciones adicionales y mitigaciones."
    ),
    "duplication": (
        "Inspecciona {root} en busca de duplicación de lógica, funciones con responsabilidades "
        "superpuestas o módulos que deberían consolidarse. Propón estrategias para redistribuir "
        "responsabilidades y reducir redundancias."
    ),
    "testing": (
        "Evalúa {root} con foco en cobertura y estrategia de pruebas. Identifica áreas sin tests, "
        "escenarios críticos sin validar y oportunidades para fortalecer suites automatizadas."
    ),
}

VALID_INSIGHTS_FOCUS = tuple(INSIGHTS_FOCUS_PROMPTS.keys())


def _resolve_focus(focus: Optional[str]) -> str:
    if not focus:
        return DEFAULT_INSIGHTS_FOCUS
    normalized = focus.strip().lower()
    if normalized in INSIGHTS_FOCUS_PROMPTS:
        return normalized
    return DEFAULT_INSIGHTS_FOCUS


def build_insights_prompt(root_path: Path, focus: Optional[str]) -> str:
    """Construye el prompt de usuario según el foco seleccionado."""
    focus_key = _resolve_focus(focus)
    template = INSIGHTS_FOCUS_PROMPTS.get(focus_key, INSIGHTS_FOCUS_PROMPTS[DEFAULT_INSIGHTS_FOCUS])
    return template.format(root=root_path.as_posix())


@dataclass(frozen=True)
class OllamaInsightResult:
    """Resultado simplificado devuelto por una ejecución de insights."""

    model: str
    generated_at: datetime
    message: str
    raw: OllamaChatResponse


def run_ollama_insights(
    *,
    model: str,
    root_path: Path,
    endpoint: Optional[str] = None,
    timeout: float = 180.0,
    context: Optional[str] = None,
    focus: Optional[str] = None,
) -> OllamaInsightResult:
    """Ejecuta un pequeño prompt en Ollama y devuelve la respuesta normalizada."""

    prompt = build_insights_prompt(root_path, focus)
    if context:
        prompt = f"{prompt}\n\nContexto reciente:\n{context.strip()}"
    messages = [
        OllamaChatMessage(role="system", content=INSIGHTS_SYSTEM_PROMPT),
        OllamaChatMessage(role="user", content=prompt),
    ]

    logger.debug(
        "Ejecutando insights con Ollama (model=%s, endpoint=%s, timeout=%s)",
        model,
        endpoint,
        timeout,
    )

    try:
        response = chat_with_ollama(
            model=model,
            messages=messages,
            endpoint=endpoint,
            timeout=timeout,
        )
    except OllamaChatError as exc:
        logger.warning(
            "No se pudieron generar insights con Ollama (modelo=%s, endpoint=%s): %s",
            model,
            endpoint,
            exc,
        )
        raise

    logger.info(
        "Insights generados con %s en %.2fms",
        model,
        response.latency_ms,
    )

    return OllamaInsightResult(
        model=response.model,
        generated_at=datetime.now(timezone.utc),
        message=response.message,
        raw=response,
    )
