# SPDX-License-Identifier: MIT
"""
Dependencias compartidas para las rutas del API.
"""

from __future__ import annotations

from fastapi import Request

from ..state import AppState


def get_app_state(request: Request) -> AppState:
    """Obtiene el estado de la aplicación desde la solicitud."""
    return request.app.state.app_state  # type: ignore[attr-defined]
