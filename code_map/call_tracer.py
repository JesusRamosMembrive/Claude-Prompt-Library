# SPDX-License-Identifier: MIT
"""
Call Graph Tracer - Stage 1 MVP

Extrae call graphs básicos usando tree-sitter para análisis de trazabilidad.
Este módulo permite rastrear cadenas de llamadas de funciones en código Python.

Stage 1 limitations:
- Solo llamadas directas: foo(), obj.method()
- Solo funciones en el mismo archivo (sin cross-file analysis)
- No maneja imports, decorators complejos, lambdas
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from tree_sitter import Parser, Node
    from tree_sitter_languages import get_language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


class CallGraphExtractor:
    """
    Extractor básico de call graphs usando tree-sitter.

    Analiza archivos Python para detectar llamadas entre funciones
    y construir un grafo de dependencias.

    Example:
        >>> extractor = CallGraphExtractor()
        >>> graph = extractor.analyze_file("my_module.py")
        >>> print(graph)
        {'foo': ['bar', 'baz'], 'bar': ['qux']}
    """

    def __init__(self):
        """Inicializa el parser de tree-sitter para Python."""
        if not TREE_SITTER_AVAILABLE:
            raise ImportError(
                "tree-sitter not available. Install with: "
                "pip install tree-sitter tree-sitter-python"
            )

        self.parser = Parser()
        self.parser.set_language(get_language("python"))
        self.call_graph: Dict[str, List[str]] = {}
        self.current_function: Optional[str] = None

    def analyze_file(self, filepath: str | Path) -> Dict[str, List[str]]:
        """
        Analiza un archivo Python y extrae el call graph.

        Args:
            filepath: Ruta al archivo Python a analizar

        Returns:
            Diccionario con el call graph: {caller: [callees]}

        Example:
            >>> extractor.analyze_file("server.py")
            {'create_app': ['configure_routes'], 'configure_routes': ['include_router']}
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, 'rb') as f:
            source = f.read()

        tree = self.parser.parse(source)
        self.call_graph = {}
        self.current_function = None

        self._extract_calls(tree.root_node, source)

        return self.call_graph

    def _extract_calls(self, node: Node, source: bytes, current_func: Optional[str] = None):
        """
        Recorre recursivamente el AST extrayendo llamadas a funciones.

        Args:
            node: Nodo actual del árbol sintáctico
            source: Código fuente como bytes
            current_func: Nombre de la función actual (contexto)
        """
        # Detectar definición de función
        if node.type == "function_definition":
            name_node = node.child_by_field_name('name')
            if name_node:
                func_name = self._get_node_text(name_node, source)
                current_func = func_name
                # Inicializar entrada en el grafo
                if func_name not in self.call_graph:
                    self.call_graph[func_name] = []

        # Detectar llamada a función
        if node.type == "call" and current_func:
            function_node = node.child_by_field_name('function')
            if function_node:
                callee = self._extract_callee_name(function_node, source)
                if callee and callee not in self.call_graph[current_func]:
                    self.call_graph[current_func].append(callee)

        # Recursión sobre hijos
        for child in node.children:
            self._extract_calls(child, source, current_func)

    def _extract_callee_name(self, node: Node, source: bytes) -> Optional[str]:
        """
        Extrae el nombre de la función llamada desde un nodo 'call'.

        Maneja:
        - Llamadas simples: foo()
        - Llamadas a métodos: obj.method()
        - Llamadas a atributos: self.helper()

        Args:
            node: Nodo que representa la función a llamar
            source: Código fuente como bytes

        Returns:
            Nombre de la función/método, o None si no se puede extraer
        """
        # Caso 1: Llamada simple - identifier
        if node.type == "identifier":
            return self._get_node_text(node, source)

        # Caso 2: Llamada a atributo - obj.method()
        if node.type == "attribute":
            attr_node = node.child_by_field_name('attribute')
            if attr_node:
                return self._get_node_text(attr_node, source)

        # Caso 3: Fallback - retornar texto completo
        return self._get_node_text(node, source)

    def _get_node_text(self, node: Node, source: bytes) -> str:
        """
        Extrae el texto de un nodo del AST.

        Args:
            node: Nodo del árbol sintáctico
            source: Código fuente como bytes

        Returns:
            Texto del nodo como string
        """
        return source[node.start_byte:node.end_byte].decode('utf-8')

    def trace_chain(
        self,
        start_function: str,
        max_depth: int = 5
    ) -> List[Tuple[int, str, List[str]]]:
        """
        Traza la cadena completa de llamadas desde una función inicial.

        Args:
            start_function: Nombre de la función de inicio
            max_depth: Profundidad máxima de recursión (default: 5)

        Returns:
            Lista de tuplas (depth, function, callees) representando la cadena

        Example:
            >>> extractor.trace_chain("create_app")
            [(0, 'create_app', ['configure_routes']),
             (1, 'configure_routes', ['include_router'])]
        """
        chain: List[Tuple[int, str, List[str]]] = []
        visited: Set[str] = set()

        def dfs(func: str, depth: int = 0):
            """DFS para rastrear la cadena de llamadas."""
            if depth > max_depth or func in visited:
                return

            visited.add(func)
            callees = self.call_graph.get(func, [])
            chain.append((depth, func, callees.copy()))

            for callee in callees:
                dfs(callee, depth + 1)

        dfs(start_function)
        return chain

    def get_all_chains(self) -> List[List[str]]:
        """
        Genera todas las cadenas de llamadas posibles en el grafo.

        Returns:
            Lista de cadenas, donde cada cadena es una lista de nombres de funciones

        Example:
            >>> extractor.get_all_chains()
            [['create_app', 'configure_routes', 'include_router'],
             ['process_data', 'validate', 'check_schema']]
        """
        chains: List[List[str]] = []
        visited_global: Set[str] = set()

        def build_chain(func: str, current_chain: List[str], visited_local: Set[str]):
            """Construye una cadena de llamadas recursivamente."""
            if func in visited_local:
                # Ciclo detectado, guardar cadena actual
                if len(current_chain) > 1:
                    chains.append(current_chain.copy())
                return

            visited_local.add(func)
            current_chain.append(func)

            callees = self.call_graph.get(func, [])

            if not callees:
                # Hoja del grafo, guardar cadena
                if len(current_chain) > 1:
                    chains.append(current_chain.copy())
            else:
                for callee in callees:
                    build_chain(callee, current_chain, visited_local.copy())

            current_chain.pop()

        # Encontrar funciones raíz (no llamadas por nadie)
        all_callees = set()
        for callees in self.call_graph.values():
            all_callees.update(callees)

        root_functions = set(self.call_graph.keys()) - all_callees

        # Si no hay raíces, usar todas las funciones
        if not root_functions:
            root_functions = set(self.call_graph.keys())

        for root in root_functions:
            if root not in visited_global:
                build_chain(root, [], set())
                visited_global.add(root)

        return chains


def analyze_file(filepath: str | Path) -> Dict[str, List[str]]:
    """
    Función helper para analizar un archivo rápidamente.

    Args:
        filepath: Ruta al archivo Python

    Returns:
        Call graph como diccionario

    Example:
        >>> from code_map.call_tracer import analyze_file
        >>> graph = analyze_file("my_module.py")
    """
    extractor = CallGraphExtractor()
    return extractor.analyze_file(filepath)
