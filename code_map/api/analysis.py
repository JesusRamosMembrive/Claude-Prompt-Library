# SPDX-License-Identifier: MIT
"""
Rutas de análisis y exploración del proyecto.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..state import AppState
from .deps import get_app_state
from .schemas import (
    ChangeNotification,
    FileSummarySchema,
    HealthResponse,
    RescanResponse,
    SearchResultsSchema,
    TreeNodeSchema,
    serialize_search_results,
    serialize_summary,
    serialize_tree,
)

router = APIRouter()

KEEPALIVE_SECONDS = 10


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Comprueba el estado de la API."""
    return HealthResponse()


@router.get("/tree", response_model=TreeNodeSchema)
async def get_tree(
    refresh: bool = Query(
        False, description="Fuerza un escaneo completo antes de responder."
    ),
    state: AppState = Depends(get_app_state),
) -> TreeNodeSchema:
    """Obtiene el árbol de archivos del proyecto."""
    if refresh:
        await state.perform_full_scan()
    tree = state.index.get_tree()
    return serialize_tree(tree, state)


@router.get("/files/{file_path:path}", response_model=FileSummarySchema)
async def get_file(
    file_path: str,
    state: AppState = Depends(get_app_state),
) -> FileSummarySchema:
    """Obtiene el resumen de un archivo específico."""
    try:
        target_path = state.resolve_path(file_path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    summary = state.index.get_file(target_path)
    if summary is None:
        raise HTTPException(
            status_code=404, detail="Archivo no encontrado en el índice."
        )
    return serialize_summary(summary, state)


@router.get("/search", response_model=SearchResultsSchema)
async def search(
    q: str = Query(
        ..., min_length=1, description="Texto a buscar en nombres de símbolos."
    ),
    state: AppState = Depends(get_app_state),
) -> SearchResultsSchema:
    """Busca símbolos en el proyecto."""
    symbols = state.index.search(q)
    return serialize_search_results(symbols, state)


async def _event_stream(state: AppState) -> AsyncIterator[bytes]:
    """Genera un flujo de eventos de cambio."""
    while True:
        try:
            payload = await asyncio.wait_for(
                state.event_queue.get(), timeout=KEEPALIVE_SECONDS
            )
            data = ChangeNotification(**payload)
            yield f"event: update\ndata: {data.json()}\n\n".encode("utf-8")
        except asyncio.TimeoutError:
            yield b": keepalive\n\n"


@router.get("/events")
async def events(state: AppState = Depends(get_app_state)) -> StreamingResponse:
    """Suscribe al flujo de eventos de cambio."""
    return StreamingResponse(_event_stream(state), media_type="text/event-stream")


@router.post("/rescan", response_model=RescanResponse)
async def rescan(state: AppState = Depends(get_app_state)) -> RescanResponse:
    """Dispara un escaneo completo del proyecto."""
    count = await state.perform_full_scan()
    return RescanResponse(files=count)
