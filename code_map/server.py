# SPDX-License-Identifier: MIT
"""
Aplicación FastAPI principal.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .scheduler import ChangeScheduler
from .state import AppState
from .settings import load_settings, save_settings
from .api.routes import router as api_router


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def create_app(root: Optional[str | Path] = None) -> FastAPI:
    root_path = Path(
        root
        or os.environ.get("CODE_MAP_ROOT", "")
        or Path.cwd()
    ).expanduser().resolve()

    include_docstrings = _env_flag("CODE_MAP_INCLUDE_DOCSTRINGS", True)

    settings = load_settings(root_path, default_include_docstrings=include_docstrings)
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
