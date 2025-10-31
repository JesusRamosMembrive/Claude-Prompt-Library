# SPDX-License-Identifier: MIT
"""
Gestión centralizada de dependencias opcionales usadas por los analizadores.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from types import ModuleType
from typing import Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DependencySpec:
    """Describe una dependencia opcional y los módulos que deben importarse."""

    key: str
    modules: Tuple[str, ...]
    description: str


@dataclass
class DependencyStatus:
    """Estado de disponibilidad para una dependencia opcional."""

    key: str
    modules: Tuple[str, ...]
    description: str
    available: bool
    error: Optional[str] = None


class OptionalDependencyRegistry:
    """Carga perezosa de dependencias opcionales con memoización de su estado."""

    def __init__(self, specs: Iterable[DependencySpec]) -> None:
        self._specs: Dict[str, DependencySpec] = {spec.key: spec for spec in specs}
        self._statuses: Dict[str, DependencyStatus] = {}
        self._modules: Dict[str, Dict[str, ModuleType]] = {}
        self._logger = logging.getLogger(f"{__name__}.OptionalDependencyRegistry")

    def require(self, key: str, module: str | None = None) -> Optional[ModuleType]:
        """
        Devuelve el módulo solicitado si la dependencia está disponible.

        Si la dependencia agrupa múltiples módulos y no se especifica `module`,
        se devuelve el primer módulo listado en la especificación.
        """

        modules = self.load(key)
        if not modules:
            return None

        if module is None:
            spec = self._specs[key]
            module = spec.modules[0]
        return modules.get(module)

    def load(self, key: str) -> Optional[Dict[str, ModuleType]]:
        """Carga todos los módulos de una dependencia y devuelve el mapeo import_name -> módulo."""

        self._ensure_loaded(key)
        return self._modules.get(key)

    def status(self, key: str | None = None) -> List[DependencyStatus]:
        """Devuelve el estado de todas las dependencias o de una en particular."""

        if key is not None:
            self._ensure_loaded(key)
            return [self._statuses[key]]

        for spec_key in self._specs:
            self._ensure_loaded(spec_key)
        return list(self._statuses.values())

    def _ensure_loaded(self, key: str) -> None:
        if key in self._statuses:
            return

        spec = self._specs.get(key)
        if spec is None:
            raise KeyError(f"Dependencia opcional desconocida: {key}")

        modules: Dict[str, ModuleType] = {}
        for module_name in spec.modules:
            try:
                modules[module_name] = importlib.import_module(module_name)
            except Exception as exc:  # pragma: no cover - dependiente del entorno
                self._statuses[key] = DependencyStatus(
                    key=spec.key,
                    modules=spec.modules,
                    description=spec.description,
                    available=False,
                    error=str(exc),
                )
                self._modules.pop(key, None)
                self._logger.warning(
                    "Dependencia opcional '%s' no disponible (%s).",
                    spec.description,
                    exc,
                )
                return

        self._modules[key] = modules
        self._statuses[key] = DependencyStatus(
            key=spec.key,
            modules=spec.modules,
            description=spec.description,
            available=True,
        )


OPTIONAL_DEPENDENCIES: Tuple[DependencySpec, ...] = (
    DependencySpec(
        key="esprima",
        modules=("esprima",),
        description="Análisis de símbolos JavaScript/JSX",
    ),
    DependencySpec(
        key="tree_sitter_languages",
        modules=("tree_sitter", "tree_sitter_languages"),
        description="Análisis de símbolos TypeScript/TSX",
    ),
    DependencySpec(
        key="beautifulsoup4",
        modules=("bs4",),
        description="Extracción de elementos HTML",
    ),
)

optional_dependencies = OptionalDependencyRegistry(OPTIONAL_DEPENDENCIES)
