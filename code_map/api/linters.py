# SPDX-License-Identifier: MIT
"""
Rutas para exponer el estado de linters y reglas de calidad.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..linters import linters_discovery_payload
from ..state import AppState
from .deps import get_app_state
from .schemas import LintersDiscoveryResponse

router = APIRouter(prefix="/linters", tags=["linters"])


@router.get("/discovery", response_model=LintersDiscoveryResponse)
async def get_linters_discovery(state: AppState = Depends(get_app_state)) -> LintersDiscoveryResponse:
    """Devuelve el resultado del proceso de discovery de herramientas de calidad."""
    payload = await linters_discovery_payload(state.settings.root_path)
    return LintersDiscoveryResponse(**payload)
