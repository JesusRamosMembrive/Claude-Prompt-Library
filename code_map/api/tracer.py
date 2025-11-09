# SPDX-License-Identifier: MIT
"""
Rutas para análisis de trazabilidad de llamadas (Call Tracing).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..call_tracer import CallGraphExtractor, TREE_SITTER_AVAILABLE
from ..call_tracer_v2 import CrossFileCallGraphExtractor
from ..state import AppState
from .deps import get_app_state

router = APIRouter(prefix="/tracer", tags=["tracer"])


# ==================== Request/Response Models ====================


class AnalyzeFileRequest(BaseModel):
    """Request para analizar un archivo y extraer su call graph."""

    file_path: str = Field(
        ...,
        description="Ruta relativa del archivo Python a analizar",
        examples=["code_map/server.py"],
    )


class CallChain(BaseModel):
    """Representa una cadena de llamadas."""

    depth: int = Field(..., description="Nivel de profundidad en la cadena")
    function: str = Field(..., description="Nombre de la función")
    callees: List[str] = Field(..., description="Funciones llamadas desde esta función")


class TraceChainRequest(BaseModel):
    """Request para trazar cadena desde una función específica."""

    file_path: str = Field(..., description="Ruta relativa del archivo Python")
    start_function: str = Field(
        ..., description="Nombre de la función desde donde iniciar el trace"
    )
    max_depth: int = Field(
        5, description="Profundidad máxima de la cadena", ge=1, le=20
    )


class CallGraphResponse(BaseModel):
    """Response con el call graph extraído."""

    file_path: str = Field(..., description="Archivo analizado")
    call_graph: Dict[str, List[str]] = Field(
        ...,
        description="Grafo de llamadas: {caller: [callees]}",
        examples=[{"create_app": ["configure_routes"], "configure_routes": ["include_router"]}],
    )
    total_functions: int = Field(..., description="Número total de funciones detectadas")


class TraceChainResponse(BaseModel):
    """Response con la cadena de llamadas trazada."""

    start_function: str = Field(..., description="Función de inicio")
    chain: List[CallChain] = Field(..., description="Cadena de llamadas completa")
    max_depth_reached: bool = Field(
        ..., description="Si se alcanzó el límite de profundidad"
    )


class AllChainsResponse(BaseModel):
    """Response con todas las cadenas detectadas en un archivo."""

    file_path: str = Field(..., description="Archivo analizado")
    chains: List[List[str]] = Field(
        ...,
        description="Lista de todas las cadenas de llamadas",
        examples=[[["create_app", "configure_routes", "include_router"]]],
    )
    total_chains: int = Field(..., description="Número total de cadenas detectadas")


# ==================== Endpoints ====================


@router.post("/analyze", response_model=CallGraphResponse)
async def analyze_file(
    request: AnalyzeFileRequest,
    state: AppState = Depends(get_app_state),
) -> CallGraphResponse:
    """
    Analiza un archivo Python y extrae su call graph.

    El call graph muestra qué funciones llaman a qué otras funciones
    dentro del mismo archivo.

    **Stage 1 Limitations:**
    - Solo analiza llamadas dentro del mismo archivo
    - No resuelve imports cross-file
    - No maneja decorators complejos, lambdas o closures
    """
    if not TREE_SITTER_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="tree-sitter no disponible. Instalar con: pip install tree-sitter tree-sitter-python",
        )

    # Resolver ruta completa
    try:
        target_path = state.resolve_path(request.file_path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Verificar que sea archivo Python
    if target_path.suffix != ".py":
        raise HTTPException(
            status_code=400,
            detail=f"Solo se soportan archivos Python (.py). Recibido: {target_path.suffix}",
        )

    # Analizar archivo
    try:
        extractor = CallGraphExtractor()
        call_graph = extractor.analyze_file(target_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error al analizar archivo: {exc}"
        ) from exc

    return CallGraphResponse(
        file_path=request.file_path,
        call_graph=call_graph,
        total_functions=len(call_graph),
    )


@router.post("/trace", response_model=TraceChainResponse)
async def trace_chain(
    request: TraceChainRequest,
    state: AppState = Depends(get_app_state),
) -> TraceChainResponse:
    """
    Traza la cadena completa de llamadas desde una función específica.

    Sigue todas las llamadas recursivamente desde la función de inicio
    hasta la profundidad máxima especificada.

    **Ejemplo:**
    Si tienes `api_move_motors() -> internal_move() -> kinesis_move()`,
    el trace desde `api_move_motors` retornará toda la cadena.
    """
    if not TREE_SITTER_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="tree-sitter no disponible",
        )

    # Resolver ruta
    try:
        target_path = state.resolve_path(request.file_path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Analizar y trazar
    try:
        extractor = CallGraphExtractor()
        extractor.analyze_file(target_path)

        # Verificar que la función existe
        if request.start_function not in extractor.call_graph:
            available = ", ".join(extractor.call_graph.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Función '{request.start_function}' no encontrada. "
                f"Funciones disponibles: {available}",
            )

        chain_data = extractor.trace_chain(
            request.start_function, max_depth=request.max_depth
        )

        # Convertir a modelo Pydantic
        chain = [
            CallChain(depth=depth, function=func, callees=callees)
            for depth, func, callees in chain_data
        ]

        # Detectar si se alcanzó max_depth
        max_depth_reached = any(item.depth >= request.max_depth for item in chain)

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error al trazar cadena: {exc}"
        ) from exc

    return TraceChainResponse(
        start_function=request.start_function,
        chain=chain,
        max_depth_reached=max_depth_reached,
    )


@router.post("/chains", response_model=AllChainsResponse)
async def get_all_chains(
    request: AnalyzeFileRequest,
    state: AppState = Depends(get_app_state),
) -> AllChainsResponse:
    """
    Obtiene todas las cadenas de llamadas posibles en un archivo.

    Detecta automáticamente funciones raíz (no llamadas por otras)
    y genera todas las cadenas desde esas raíces.

    **Útil para:**
    - Visualizar flujo completo de un módulo
    - Detectar endpoints y sus cadenas de ejecución
    - Identificar código no utilizado
    """
    if not TREE_SITTER_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="tree-sitter no disponible",
        )

    # Resolver ruta
    try:
        target_path = state.resolve_path(request.file_path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Analizar
    try:
        extractor = CallGraphExtractor()
        extractor.analyze_file(target_path)
        chains = extractor.get_all_chains()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Error al extraer cadenas: {exc}"
        ) from exc

    return AllChainsResponse(
        file_path=request.file_path,
        chains=chains,
        total_chains=len(chains),
    )


# ==================== Stage 2: Cross-File Analysis ====================


class AnalyzeCrossFileRequest(BaseModel):
    """Request para análisis cross-file (Stage 2)."""

    file_path: str = Field(
        ...,
        description="Archivo de inicio para análisis cross-file",
        examples=["code_map/server.py"],
    )
    recursive: bool = Field(
        True,
        description="Si True, analiza también archivos importados",
    )
    max_files: int = Field(
        50,
        description="Máximo número de archivos a analizar",
        ge=1,
        le=200,
    )


class CrossFileCallGraphResponse(BaseModel):
    """Response con call graph cross-file."""

    call_graph: Dict[str, List[str]] = Field(
        ...,
        description="Call graph con nombres cualificados (file.py::function)",
        examples=[{
            "server.py::create_app": ["settings.py::load_settings", "state.py::AppState"],
            "settings.py::load_settings": []
        }],
    )
    entry_points: List[str] = Field(
        ...,
        description="Funciones que no son llamadas por nadie",
    )
    total_functions: int = Field(
        ...,
        description="Total de funciones analizadas",
    )
    analyzed_files: List[str] = Field(
        ...,
        description="Lista de archivos analizados",
    )


class TraceCrossFileRequest(BaseModel):
    """Request para trace cross-file."""

    start_function: str = Field(
        ...,
        description="Nombre cualificado de inicio (file.py::function)",
        examples=["code_map/server.py::create_app"],
    )
    max_depth: int = Field(
        10,
        description="Profundidad máxima",
        ge=1,
        le=50,
    )


class CrossFileCallChain(BaseModel):
    """Cadena de llamadas cross-file."""

    depth: int = Field(..., description="Nivel de profundidad")
    qualified_name: str = Field(..., description="Nombre cualificado (file::function)")
    callees: List[str] = Field(..., description="Funciones llamadas (cualificadas)")
    file_path: str = Field(..., description="Archivo donde está la función")
    function_name: str = Field(..., description="Nombre de la función sin cualificación")


class TraceCrossFileResponse(BaseModel):
    """Response con trace cross-file."""

    start_function: str = Field(..., description="Función de inicio")
    chain: List[CrossFileCallChain] = Field(..., description="Cadena completa")
    max_depth_reached: bool = Field(..., description="Si alcanzó el límite")
    total_depth: int = Field(..., description="Profundidad total alcanzada")


@router.post("/analyze-cross-file", response_model=CrossFileCallGraphResponse)
async def analyze_cross_file(
    request: AnalyzeCrossFileRequest,
    state: AppState = Depends(get_app_state),
) -> CrossFileCallGraphResponse:
    """
    Analiza call graph con resolución de imports (Stage 2).

    **Características Stage 2:**
    - Sigue imports entre archivos
    - Resuelve llamadas a funciones importadas
    - Detecta entry points del proyecto
    - Cachea resultados por archivo

    **Formato de nombres:**
    - Nombres cualificados: `path/to/file.py::function_name`
    - Métodos de clase: `path/to/file.py::ClassName.method_name`

    **Ejemplo:**
    ```
    {
      "call_graph": {
        "server.py::create_app": [
          "settings.py::load_settings",
          "state.py::AppState"
        ]
      }
    }
    ```
    """
    if not TREE_SITTER_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="tree-sitter no disponible",
        )

    # Resolver ruta
    try:
        target_path = state.resolve_path(request.file_path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Verificar que sea Python
    if target_path.suffix != ".py":
        raise HTTPException(
            status_code=400,
            detail=f"Solo archivos Python (.py). Recibido: {target_path.suffix}",
        )

    # Analizar cross-file
    try:
        extractor = CrossFileCallGraphExtractor(
            project_root=state.settings.root_path,
            use_cache=True
        )

        extractor.analyze_file(target_path, recursive=request.recursive)

        # Limitar archivos analizados
        if len(extractor.analyzed_files) > request.max_files:
            raise HTTPException(
                status_code=400,
                detail=f"Demasiados archivos ({len(extractor.analyzed_files)}). "
                       f"Límite: {request.max_files}. Usa recursive=False o aumenta max_files."
            )

        result = extractor.export_to_dict()

        return CrossFileCallGraphResponse(
            call_graph=result["call_graph"],
            entry_points=result["entry_points"],
            total_functions=result["total_functions"],
            analyzed_files=result["analyzed_files"],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis cross-file: {exc}"
        ) from exc


@router.post("/trace-cross-file", response_model=TraceCrossFileResponse)
async def trace_cross_file(
    request: TraceCrossFileRequest,
    state: AppState = Depends(get_app_state),
) -> TraceCrossFileResponse:
    """
    Traza cadena de llamadas cross-file (Stage 2).

    **Características:**
    - Sigue llamadas entre archivos diferentes
    - Muestra path completo de ejecución
    - Detecta ciclos

    **Input:**
    - `start_function`: Nombre cualificado `"path/file.py::function"`
    - `max_depth`: Profundidad máxima a trazar

    **Ejemplo:**
    ```
    POST /tracer/trace-cross-file
    {
      "start_function": "code_map/server.py::create_app",
      "max_depth": 10
    }
    ```
    """
    if not TREE_SITTER_AVAILABLE:
        raise HTTPException(status_code=500, detail="tree-sitter no disponible")

    try:
        # Parsear el nombre cualificado
        if "::" not in request.start_function:
            raise HTTPException(
                status_code=400,
                detail=f"Formato inválido. Use 'file.py::function'. Recibido: {request.start_function}"
            )

        file_part, func_part = request.start_function.rsplit("::", 1)
        target_path = state.settings.root_path / file_part

        if not target_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Archivo no encontrado: {file_part}"
            )

        # Analizar proyecto desde ese archivo
        extractor = CrossFileCallGraphExtractor(
            project_root=state.settings.root_path,
            use_cache=True
        )

        extractor.analyze_file(target_path, recursive=True)

        # Verificar que la función existe
        if request.start_function not in extractor.call_graph:
            available = ", ".join(list(extractor.call_graph.keys())[:10])
            raise HTTPException(
                status_code=404,
                detail=f"Función '{request.start_function}' no encontrada. "
                       f"Disponibles: {available}..."
            )

        # Trazar cadena
        chain_data = extractor.trace_chain_cross_file(
            request.start_function,
            max_depth=request.max_depth
        )

        # Convertir a modelo Pydantic
        chain = []
        for depth, qualified_name, callees in chain_data:
            # Parsear nombre cualificado
            if "::" in qualified_name:
                file_str, func_str = qualified_name.rsplit("::", 1)
            else:
                file_str, func_str = "unknown", qualified_name

            chain.append(
                CrossFileCallChain(
                    depth=depth,
                    qualified_name=qualified_name,
                    callees=callees,
                    file_path=file_str,
                    function_name=func_str,
                )
            )

        max_depth_reached = any(item.depth >= request.max_depth for item in chain)
        total_depth = max(item.depth for item in chain) if chain else 0

        return TraceCrossFileResponse(
            start_function=request.start_function,
            chain=chain,
            max_depth_reached=max_depth_reached,
            total_depth=total_depth,
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error al trazar cross-file: {exc}"
        ) from exc
