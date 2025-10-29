# SPDX-License-Identifier: MIT
"""
Rutas para gestionar settings y estado de la aplicación.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..state import AppState
from .deps import get_app_state
from .schemas import (
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
    return serialize_settings(state)


@router.put("/settings", response_model=SettingsUpdateResponse)
async def update_settings(
    payload: SettingsUpdateRequest,
    state: AppState = Depends(get_app_state),
) -> SettingsUpdateResponse:
    root_path: Optional[Path] = None
    if payload.root_path is not None:
        candidate = Path(payload.root_path).expanduser()
        if not candidate.is_absolute():
            candidate = (state.settings.root_path / candidate).resolve()
        else:
            candidate = candidate.resolve()
        root_path = candidate

    try:
        updated = await state.update_settings(
            root_path=root_path,
            include_docstrings=payload.include_docstrings,
            exclude_dirs=payload.exclude_dirs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SettingsUpdateResponse(
        updated=updated,
        settings=serialize_settings(state),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status(state: AppState = Depends(get_app_state)) -> StatusResponse:
    return serialize_status(state)
