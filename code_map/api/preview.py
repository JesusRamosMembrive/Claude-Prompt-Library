# SPDX-License-Identifier: MIT
"""
Rutas relacionadas con la previsualización de archivos.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from ..state import AppState
from .deps import get_app_state

router = APIRouter()


@router.get("/preview")
async def preview_file(
    path: str = Query(..., description="Ruta relativa al root configurado."),
    state: AppState = Depends(get_app_state),
) -> PlainTextResponse:
    """Obtiene el contenido de un archivo para previsualización."""
    try:
        target_path = state.resolve_path(path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")

    try:
        content = target_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    content_type = (
        "text/html; charset=utf-8"
        if target_path.suffix.lower() in {".html", ".htm"}
        else "text/plain; charset=utf-8"
    )

    return PlainTextResponse(content, media_type=content_type)
