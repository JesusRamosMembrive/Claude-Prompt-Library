# SPDX-License-Identifier: MIT
"""
Endpoints relacionados con visualizaciones de grafos.
"""

from __future__ import annotations

from typing import List, Optional, Set

from fastapi import APIRouter, Depends, Query

from ..class_graph import build_class_graph
from ..state import AppState
from .deps import get_app_state
from .schemas import ClassGraphResponse

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/classes", response_model=ClassGraphResponse)
async def get_class_graph(
    include_external: bool = Query(
        True,
        description="Incluir relaciones externas (clases fuera del workspace).",
    ),
    edge_types: Optional[List[str]] = Query(
        None,
        description="Filtra un conjunto concreto de relaciones (inherits, instantiates).",
    ),
    state: AppState = Depends(get_app_state),
) -> ClassGraphResponse:
    """
    Genera el grafo de clases detectado en el workspace actual.
    """
    valid_types: Set[str] = {"inherits", "instantiates"}
    requested: Optional[Set[str]] = None
    if edge_types:
        requested = {edge for edge in edge_types if edge in valid_types}
        if not requested:
            requested = valid_types
    graph = build_class_graph(
        state.settings.root_path,
        include_external=include_external,
        edge_types=requested,
    )
    return ClassGraphResponse(**graph)
