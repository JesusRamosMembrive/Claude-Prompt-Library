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

from .cache import SnapshotStore
from .scheduler import ChangeScheduler
from .scanner import ProjectScanner
from .index import SymbolIndex
from .state import AppState
from .watcher import WatcherService
from .api.routes import router as api_router


def create_app(root: Optional[str | Path] = None) -> FastAPI:
    root_path = Path(
        root
        or os.environ.get("CODE_MAP_ROOT", "")
        or Path.cwd()
    ).expanduser().resolve()

    scanner = ProjectScanner(root_path)
    index = SymbolIndex(root_path)
    snapshot_store = SnapshotStore(root_path)
    scheduler = ChangeScheduler()
    watcher = WatcherService(root_path, scheduler)

    state = AppState(
        root=root_path,
        scanner=scanner,
        index=index,
        snapshot_store=snapshot_store,
        scheduler=scheduler,
        watcher=watcher,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await state.startup()
        try:
            yield
        finally:
            await state.shutdown()

    app = FastAPI(title="Code Map API", lifespan=lifespan)
    app.include_router(api_router)
    app.state.app_state = state  # type: ignore[attr-defined]

    return app


app = create_app()
