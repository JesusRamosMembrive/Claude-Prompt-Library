# SPDX-License-Identifier: MIT
"""
Aplicación FastAPI principal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .scheduler import ChangeScheduler
from .state import AppState
from .settings import load_settings, save_settings
from .api.routes import router as api_router


def create_app(root: Optional[str | Path] = None) -> FastAPI:
    settings = load_settings(root_override=root)
    scheduler = ChangeScheduler()

    state = AppState(
        settings=settings,
        scheduler=scheduler,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await state.startup()
        try:
            yield
        finally:
            await state.shutdown()

    # Guardar settings al arranque por si se generaron con valores por defecto.
    save_settings(state.settings)

    app = FastAPI(title="Code Map API", lifespan=lifespan)
    app.include_router(api_router)
    app.state.app_state = state  # type: ignore[attr-defined]

    return app


app = create_app()
