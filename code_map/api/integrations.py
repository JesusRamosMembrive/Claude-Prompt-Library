# SPDX-License-Identifier: MIT
"""
Rutas relacionadas con la integración con Ollama.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import List

from fastapi import APIRouter, HTTPException

from ..integrations import (
    OllamaChatError,
    OllamaChatMessage,
    OllamaStartError,
    chat_with_ollama,
    discover_ollama,
    start_ollama_server,
)
from .schemas import (
    OllamaStartRequest,
    OllamaStartResponse,
    OllamaStatusResponse,
    OllamaTestRequest,
    OllamaTestResponse,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/ollama/status", response_model=OllamaStatusResponse)
async def get_ollama_status() -> OllamaStatusResponse:
    """Devuelve el estado actual de Ollama (instalación, servicio y modelos)."""
    discovery = await asyncio.to_thread(discover_ollama)
    return OllamaStatusResponse(status=asdict(discovery.status), checked_at=discovery.checked_at)


@router.post("/ollama/start", response_model=OllamaStartResponse)
async def start_ollama(payload: OllamaStartRequest) -> OllamaStartResponse:
    """Intenta iniciar el servidor Ollama y devuelve el estado actualizado."""
    timeout = payload.timeout_seconds if payload.timeout_seconds is not None else 5.0
    try:
        result = await asyncio.to_thread(start_ollama_server, timeout=timeout)
    except OllamaStartError as exc:
        detail = {
            "message": str(exc),
            "endpoint": exc.endpoint,
            "original_error": exc.original_error,
        }
        raise HTTPException(status_code=502, detail=detail) from exc

    return OllamaStartResponse(
        started=result.started,
        already_running=result.already_running,
        endpoint=result.endpoint,
        process_id=result.process_id,
        status=asdict(result.status),
        checked_at=result.checked_at,
    )


@router.post("/ollama/test", response_model=OllamaTestResponse)
async def test_ollama_chat(payload: OllamaTestRequest) -> OllamaTestResponse:
    """
    Ejecuta un chat breve contra el modelo indicado para verificar conectividad con Ollama.
    """
    messages: List[OllamaChatMessage] = []
    if payload.system_prompt:
        messages.append(OllamaChatMessage(role="system", content=payload.system_prompt))
    messages.append(OllamaChatMessage(role="user", content=payload.prompt))

    timeout = payload.timeout_seconds if payload.timeout_seconds is not None else 180.0

    try:
        result = await asyncio.to_thread(
            chat_with_ollama,
            model=payload.model,
            messages=messages,
            endpoint=payload.endpoint,
            timeout=timeout,
        )
    except OllamaChatError as exc:
        detail = {
            "message": str(exc),
            "endpoint": exc.endpoint,
            "original_error": exc.original_error,
            "status_code": exc.status_code,
        }
        if exc.reason_code is not None:
            detail["reason_code"] = exc.reason_code
        if exc.retry_after_seconds is not None:
            detail["retry_after_seconds"] = exc.retry_after_seconds
        if exc.loading_since is not None:
            detail["loading"] = True
            detail["loading_since"] = exc.loading_since.isoformat()
        raise HTTPException(status_code=502, detail=detail) from exc

    return OllamaTestResponse(
        success=True,
        model=result.model,
        endpoint=result.endpoint,
        latency_ms=result.latency_ms,
        message=result.message,
        raw=result.raw,
    )
