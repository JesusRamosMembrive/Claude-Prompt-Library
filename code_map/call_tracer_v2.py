# SPDX-License-Identifier: MIT
"""
Call Graph Tracer - Stage 2

Análisis cross-file completo con resolución de imports.
Soporta:
- Análisis multi-archivo
- Resolución de imports (absolutos y relativos)
- Detección de métodos de clase
- Cache de resultados para performance
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import json

try:
    from tree_sitter import Parser, Node
    from tree_sitter_languages import get_language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

from .import_resolver import ImportResolver


class CrossFileCallGraphExtractor:
    """
    Extractor de call graphs con análisis cross-file.

    Características Stage 2:
    - Sigue imports entre archivos
    - Resuelve llamadas a funciones importadas
    - Cachea resultados por archivo
    - Detecta métodos de clase

    Example:
        >>> extractor = CrossFileCallGraphExtractor(project_root=Path("/project"))
        >>> graph = extractor.analyze_project(entry_point="main.py")
        >>> print(graph)
        {
            'main.py::main': ['utils.py::helper', 'process.py::run'],
            'utils.py::helper': ['config.py::load_config']
        }
    """

    def __init__(self, project_root: Path, use_cache: bool = True):
        """
        Inicializa el extractor cross-file.

        Args:
            project_root: Raíz del proyecto
            use_cache: Si True, cachea resultados por archivo
        """
        if not TREE_SITTER_AVAILABLE:
            raise ImportError(
                "tree-sitter not available. Install with: "
                "pip install tree-sitter tree-sitter-python"
            )

        self.project_root = project_root.resolve()
        self.parser = Parser()
        self.parser.set_language(get_language("python"))
        self.import_resolver = ImportResolver(project_root)
        self.use_cache = use_cache

        # Cache: {file_path: {hash: call_graph}}
        self._file_cache: Dict[Path, Tuple[str, Dict[str, List[str]]]] = {}

        # Global call graph: {qualified_name: [qualified_callees]}
        # qualified_name format: "file.py::function_name"
        self.call_graph: Dict[str, List[str]] = {}

        # Set de archivos ya analizados (para evitar ciclos)
        self.analyzed_files: Set[Path] = set()

    def _get_file_hash(self, filepath: Path) -> str:
        """Calcula hash MD5 del contenido del archivo para cache."""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _get_qualified_name(self, filepath: Path, function_name: str) -> str:
        """
        Genera nombre cualificado para una función.

        Args:
            filepath: Path del archivo
            function_name: Nombre de la función

        Returns:
            Nombre cualificado: "relative/path/file.py::function_name"
        """
        try:
            relative = filepath.relative_to(self.project_root)
        except ValueError:
            relative = filepath

        return f"{relative}::{function_name}"

    def analyze_file(
        self,
        filepath: Path,
        recursive: bool = True
    ) -> Dict[str, List[str]]:
        """
        Analiza un archivo y opcionalmente sus dependencias.

        Args:
            filepath: Archivo a analizar
            recursive: Si True, analiza también archivos importados

        Returns:
            Call graph local del archivo
        """
        filepath = filepath.resolve()

        # Verificar cache
        if self.use_cache and filepath in self._file_cache:
            cached_hash, cached_graph = self._file_cache[filepath]
            current_hash = self._get_file_hash(filepath)
            if cached_hash == current_hash:
                return cached_graph

        # Marcar como analizado para evitar ciclos
        if filepath in self.analyzed_files:
            return {}

        self.analyzed_files.add(filepath)

        # Leer archivo
        with open(filepath, 'rb') as f:
            source = f.read()

        tree = self.parser.parse(source)

        # Extraer definiciones de funciones y sus llamadas
        local_graph = {}
        self._extract_functions_and_calls(
            tree.root_node,
            source,
            filepath,
            local_graph
        )

        # Resolver imports
        import_map = self.import_resolver.build_import_map(filepath)

        # Actualizar call graph con nombres cualificados
        for func_name, callees in local_graph.items():
            qualified_func = self._get_qualified_name(filepath, func_name)

            qualified_callees = []
            for callee in callees:
                # Verificar si es un import
                if callee in import_map:
                    target_file, symbol = import_map[callee]

                    if symbol:
                        # from utils import helper → helper es la función
                        qualified_callee = self._get_qualified_name(target_file, symbol)
                    else:
                        # import utils → puede ser utils.function
                        # Por ahora, marcar como externa
                        qualified_callee = f"{target_file}::*"

                    qualified_callees.append(qualified_callee)

                    # Recursivamente analizar archivo importado
                    if recursive and target_file not in self.analyzed_files:
                        self.analyze_file(target_file, recursive=True)
                else:
                    # Llamada local (dentro del mismo archivo)
                    qualified_callee = self._get_qualified_name(filepath, callee)
                    qualified_callees.append(qualified_callee)

            self.call_graph[qualified_func] = qualified_callees

        # Cachear resultado
        if self.use_cache:
            file_hash = self._get_file_hash(filepath)
            self._file_cache[filepath] = (file_hash, local_graph)

        return local_graph

    def _extract_functions_and_calls(
        self,
        node: Node,
        source: bytes,
        filepath: Path,
        local_graph: Dict[str, List[str]],
        current_func: Optional[str] = None,
        current_class: Optional[str] = None
    ):
        """
        Extrae funciones y llamadas del AST.

        Args:
            node: Nodo actual
            source: Código fuente
            filepath: Archivo siendo analizado
            local_graph: Grafo local a llenar
            current_func: Función actual (contexto)
            current_class: Clase actual (contexto)
        """
        # Detectar clase
        if node.type == "class_definition":
            name_node = node.child_by_field_name('name')
            if name_node:
                class_name = self._get_node_text(name_node, source)
                current_class = class_name

        # Detectar función
        if node.type == "function_definition":
            name_node = node.child_by_field_name('name')
            if name_node:
                func_name = self._get_node_text(name_node, source)

                # Si está en una clase, prefixar con nombre de clase
                if current_class:
                    qualified_func_name = f"{current_class}.{func_name}"
                else:
                    qualified_func_name = func_name

                current_func = qualified_func_name

                # Inicializar en el grafo
                if qualified_func_name not in local_graph:
                    local_graph[qualified_func_name] = []

        # Detectar llamada
        if node.type == "call" and current_func:
            function_node = node.child_by_field_name('function')
            if function_node:
                callee = self._extract_callee_name(function_node, source)
                if callee and callee not in local_graph[current_func]:
                    local_graph[current_func].append(callee)

        # Recursión
        for child in node.children:
            self._extract_functions_and_calls(
                child,
                source,
                filepath,
                local_graph,
                current_func,
                current_class
            )

    def _extract_callee_name(self, node: Node, source: bytes) -> Optional[str]:
        """
        Extrae nombre de función llamada.

        Maneja:
        - foo() → "foo"
        - obj.method() → "method"
        - self.helper() → "helper"
        - module.func() → "module" (import)
        """
        if node.type == "identifier":
            return self._get_node_text(node, source)

        if node.type == "attribute":
            # obj.method() → extraer "method"
            attr_node = node.child_by_field_name('attribute')
            if attr_node:
                return self._get_node_text(attr_node, source)

            # También extraer el objeto para detectar imports
            obj_node = node.child_by_field_name('object')
            if obj_node and obj_node.type == "identifier":
                # module.func() → retornar "module"
                return self._get_node_text(obj_node, source)

        return self._get_node_text(node, source)

    def _get_node_text(self, node: Node, source: bytes) -> str:
        """Extrae texto de un nodo."""
        return source[node.start_byte:node.end_byte].decode('utf-8')

    def trace_chain_cross_file(
        self,
        start_function: str,
        max_depth: int = 10
    ) -> List[Tuple[int, str, List[str]]]:
        """
        Traza cadena de llamadas cross-file.

        Args:
            start_function: Nombre cualificado ("file.py::function")
            max_depth: Profundidad máxima

        Returns:
            Lista de (depth, qualified_name, callees)
        """
        chain: List[Tuple[int, str, List[str]]] = []
        visited: Set[str] = set()

        def dfs(func: str, depth: int = 0):
            if depth > max_depth or func in visited:
                return

            visited.add(func)
            callees = self.call_graph.get(func, [])
            chain.append((depth, func, callees.copy()))

            for callee in callees:
                dfs(callee, depth + 1)

        dfs(start_function)
        return chain

    def find_entry_points(self) -> List[str]:
        """
        Encuentra funciones que no son llamadas por nadie (entry points).

        Returns:
            Lista de nombres cualificados de entry points
        """
        all_callees = set()
        for callees in self.call_graph.values():
            all_callees.update(callees)

        entry_points = set(self.call_graph.keys()) - all_callees
        return list(entry_points)

    def export_to_dict(self) -> Dict[str, any]:
        """
        Exporta el call graph a un diccionario serializable.

        Returns:
            Dict con estructura del call graph
        """
        return {
            "call_graph": self.call_graph,
            "entry_points": self.find_entry_points(),
            "total_functions": len(self.call_graph),
            "analyzed_files": [str(f.relative_to(self.project_root)) for f in self.analyzed_files]
        }
