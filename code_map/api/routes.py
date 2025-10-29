# SPDX-License-Identifier: MIT
"""
Router compuesto que agrupa las rutas por dominio.
"""

from __future__ import annotations

from fastapi import APIRouter

from .analysis import router as analysis_router
from .preview import router as preview_router
from .settings import router as settings_router

router = APIRouter()
router.include_router(analysis_router)
router.include_router(settings_router)
router.include_router(preview_router)
