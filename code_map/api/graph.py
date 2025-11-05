# SPDX-License-Identifier: MIT
"""
Endpoints relacionados con visualizaciones de grafos.
"""

from __future__ import annotations

from typing import List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from ..class_graph import build_class_graph
from ..uml_graph import build_uml_model, render_uml_svg
from ..state import AppState
from .deps import get_app_state
from .schemas import ClassGraphResponse, UMLDiagramResponse

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/classes", response_model=ClassGraphResponse)
async def get_class_graph(
    include_external: bool = Query(
        False,
        description="Incluir relaciones externas (clases fuera del workspace).",
    ),
    edge_types: Optional[List[str]] = Query(
        None,
        description="Filtra un conjunto concreto de relaciones (inherits, instantiates).",
    ),
    module_prefix: Optional[List[str]] = Query(
        None,
        description="Limita el grafo a módulos que comiencen por alguno de estos prefijos.",
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
        module_prefixes={prefix for prefix in module_prefix or [] if prefix},
    )
    return ClassGraphResponse.model_validate(graph)


@router.get("/uml", response_model=UMLDiagramResponse)
async def get_uml_diagram(
    include_external: bool = Query(
        False,
        description="Incluir relaciones con clases externas.",
    ),
    module_prefix: Optional[List[str]] = Query(
        None,
        description="Prefijos de módulo a incluir en el diagrama.",
    ),
    edge_types: Optional[List[str]] = Query(
        None,
        description="Tipos de relaciones a mostrar: inheritance, association, instantiation, reference. Default: inheritance, association.",
    ),
    state: AppState = Depends(get_app_state),
) -> UMLDiagramResponse:
    prefixes = {prefix for prefix in module_prefix or [] if prefix}

    # Parse edge types - default to inheritance + association for backwards compatibility
    valid_types = {"inheritance", "association", "instantiation", "reference"}
    if edge_types:
        requested_types = {edge for edge in edge_types if edge in valid_types}
        if not requested_types:
            requested_types = {"inheritance", "association"}
    else:
        requested_types = {"inheritance", "association"}

    uml = build_uml_model(
        state.settings.root_path,
        module_prefixes=prefixes,
        include_external=include_external,
    )
    return UMLDiagramResponse.model_validate(uml)


@router.get("/uml/svg", response_class=Response)
async def get_uml_svg(
    include_external: bool = Query(
        False,
        description="Incluir relaciones con clases externas.",
    ),
    module_prefix: Optional[List[str]] = Query(
        None,
        description="Prefijos de módulo a incluir en el diagrama.",
    ),
    edge_types: Optional[List[str]] = Query(
        None,
        description="Tipos de relaciones a mostrar: inheritance, association, instantiation, reference. Default: inheritance, association.",
    ),
    state: AppState = Depends(get_app_state),
) -> Response:
    prefixes = {prefix for prefix in module_prefix or [] if prefix}

    # Parse edge types - default to inheritance + association for backwards compatibility
    valid_types = {"inheritance", "association", "instantiation", "reference"}
    if edge_types:
        requested_types = {edge for edge in edge_types if edge in valid_types}
        if not requested_types:
            requested_types = {"inheritance", "association"}
    else:
        requested_types = {"inheritance", "association"}

    model = build_uml_model(
        state.settings.root_path,
        module_prefixes=prefixes,
        include_external=include_external,
    )
    try:
        svg = render_uml_svg(model, requested_types)
    except RuntimeError as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return Response(content=svg, media_type="image/svg+xml")
