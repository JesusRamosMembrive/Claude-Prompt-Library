# SPDX-License-Identifier: MIT
"""
Rutas para gestionar settings y estado de la aplicación.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import asyncio

from fastapi import APIRouter, Depends, HTTPException

from ..state import AppState
from .deps import get_app_state
from .schemas import (
    BrowseDirectoryResponse,
    SettingsResponse,
    SettingsUpdateRequest,
    SettingsUpdateResponse,
    StatusResponse,
    serialize_settings,
    serialize_status,
)

router = APIRouter()


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(state: AppState = Depends(get_app_state)) -> SettingsResponse:
    """Obtiene la configuración actual de la aplicación."""
    return serialize_settings(state)


@router.put("/settings", response_model=SettingsUpdateResponse)
async def update_settings(
    payload: SettingsUpdateRequest,
    state: AppState = Depends(get_app_state),
) -> SettingsUpdateResponse:
    """Actualiza la configuración de la aplicación."""
    root_path: Optional[Path] = None
    if payload.root_path is not None:
        candidate = Path(payload.root_path).expanduser()
        if not candidate.is_absolute():
            candidate = (state.settings.root_path / candidate).resolve()
        else:
            candidate = candidate.resolve()
        root_path = candidate

    model_value: Optional[str] = None
    if payload.ollama_insights_model is not None:
        trimmed = payload.ollama_insights_model.strip()
        model_value = trimmed or None

    frequency_value = payload.ollama_insights_frequency_minutes

    try:
        updated = await state.update_settings(
            root_path=root_path,
            include_docstrings=payload.include_docstrings,
            exclude_dirs=payload.exclude_dirs,
            ollama_insights_enabled=payload.ollama_insights_enabled,
            ollama_insights_model=model_value,
            ollama_insights_frequency_minutes=frequency_value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SettingsUpdateResponse(
        updated=updated,
        settings=serialize_settings(state),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status(state: AppState = Depends(get_app_state)) -> StatusResponse:
    """Obtiene el estado actual de la aplicación."""
    return serialize_status(state)


@router.post("/settings/browse", response_model=BrowseDirectoryResponse)
async def browse_directory(state: AppState = Depends(get_app_state)) -> BrowseDirectoryResponse:
    """Abre un diálogo nativo para seleccionar un directorio."""

    def _select_directory(initial: Path) -> str:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("tkinter no está disponible en este entorno") from exc

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(initialdir=str(initial))
        root.destroy()
        if not selected:
            raise RuntimeError("Selección cancelada")
        return selected

    try:
        path = await asyncio.to_thread(_select_directory, state.settings.root_path)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BrowseDirectoryResponse(path=path)
