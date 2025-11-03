# SPDX-License-Identifier: MIT
"""Ejecución de análisis automáticos asistidos por Ollama."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..integrations import OllamaChatError, OllamaChatMessage, chat_with_ollama, OllamaChatResponse
from ..settings import AppSettings

logger = logging.getLogger(__name__)


INSIGHTS_SYSTEM_PROMPT = (
    "Eres un asistente que revisa periódicamente un repositorio para detectar mejoras. "
    "Responde en español con un resumen breve de acciones útiles (máximo 5 viñetas)."
)

INSIGHTS_USER_PROMPT = (
    "Analiza el estado actual del repositorio en {root}. Sugiere refactors, soluciones "
    "para problemas de linters y patrones de diseño relevantes. Si no tienes contexto, "
    "propón pasos generales."
)


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
) -> OllamaInsightResult:
    """Ejecuta un pequeño prompt en Ollama y devuelve la respuesta normalizada."""

    prompt = INSIGHTS_USER_PROMPT.format(root=root_path.as_posix())
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
