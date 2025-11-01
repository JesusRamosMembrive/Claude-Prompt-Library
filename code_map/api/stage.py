# SPDX-License-Identifier: MIT
"""
Rutas para gestionar la inicialización y verificación Stage-Aware.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends

from ..stage_toolkit import AgentSelection, run_initializer, stage_status
from ..state import AppState
from .deps import get_app_state
from .schemas import StageInitRequest, StageInitResponse, StageStatusResponse

router = APIRouter(prefix="/stage", tags=["stage"])


@router.get("/status", response_model=StageStatusResponse)
async def get_stage_status(state: AppState = Depends(get_app_state)) -> StageStatusResponse:
    """Devuelve el estado actual de los archivos Stage-Aware del proyecto."""
    payload = await stage_status(state.settings.root_path, index=state.index)
    return StageStatusResponse(**payload)


@router.post("/init", response_model=StageInitResponse)
async def initialize_stage_assets(
    request: StageInitRequest,
    state: AppState = Depends(get_app_state),
) -> StageInitResponse:
    """Ejecuta init_project.py sobre el root actual para instalar instrucciones."""
    agents: AgentSelection = request.agents  # type: ignore[assignment]
    result = await run_initializer(state.settings.root_path, agents)
    return StageInitResponse(**result)
