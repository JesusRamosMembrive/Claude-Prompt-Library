# SPDX-License-Identifier: MIT
"""
Herramientas para analizar relaciones entre clases dentro del workspace.

Este módulo recorre los archivos Python del proyecto y construye un grafo con:
    - nodos: clases detectadas (nombre, módulo, archivo)
    - aristas: relaciones de herencia e instanciación entre clases

Las relaciones intentan resolverse a clases internas del proyecto. Cuando no es
posible (librerías externas, imports dinámicos, etc.) la arista se marca como
externa y mantiene el nombre original sin resolver.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Modelos de datos


@dataclass
class ClassInfo:
    """Información recolectada para una clase en un módulo."""

    name: str
    bases: List[str] = field(default_factory=list)
    instantiates: Set[str] = field(default_factory=set)
    references: Set[str] = field(default_factory=set)


@dataclass
class ModuleInfo:
    """Información recolectada para un archivo (módulo) del proyecto."""

    module: str
    file: Path
    imports: Dict[str, str] = field(default_factory=dict)
    classes: Dict[str, ClassInfo] = field(default_factory=dict)


@dataclass
class GraphNode:
    """Nodo del grafo de clases."""

    id: str
    name: str
    module: str
    file: str


@dataclass
class GraphEdge:
    """Arista del grafo de clases."""

    source: str
    target: str
    type: str  # 'inherits' | 'instantiates'
    internal: bool
    raw_target: str


# ---------------------------------------------------------------------------
# Analyse utilities


class ModuleAnalyzer(ast.NodeVisitor):
    """Analiza un módulo para extraer clases e imports relevantes."""

    def __init__(self, module: str, file_path: Path) -> None:
        self.info = ModuleInfo(module=module, file=file_path)
        self._current_class: Optional[ClassInfo] = None

    # -- Imports ------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            key = alias.asname or alias.name.split(".")[0]
            self.info.imports[key] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            key = alias.asname or alias.name
            if alias.name == "*":
                continue
            # Resolver un posible import relativo
            if node.level:
                rel_module = self._resolve_relative(module, node.level)
                full_path = f"{rel_module}.{alias.name}" if rel_module else alias.name
            else:
                full_path = f"{module}.{alias.name}" if module else alias.name
            self.info.imports[key] = full_path
        self.generic_visit(node)

    def _resolve_relative(self, module: str, level: int) -> str:
        parts = self.info.module.split(".")
        if level > len(parts):
            return module
        base = parts[: -level]
        if module:
            base.append(module)
        return ".".join(base)

    # -- Clases -------------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        klass = ClassInfo(
            name=node.name,
            bases=[self._expr_to_name(base) for base in node.bases],
        )
        self.info.classes[node.name] = klass
        previous = self._current_class
        self._current_class = klass
        self.generic_visit(node)
        self._current_class = previous

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._current_class is not None:
            visitor = InstantiationVisitor()
            visitor.visit(node)
            self._current_class.instantiates.update(visitor.instantiated_classes)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._current_class is not None:
            visitor = InstantiationVisitor()
            visitor.visit(node)
            self._current_class.instantiates.update(visitor.instantiated_classes)
            refs = _extract_references_from_assignment(node)
            self._current_class.references.update(refs)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self._current_class is not None:
            self._current_class.references.update(_extract_type_names(node.annotation))
        self.generic_visit(node)

    def _expr_to_name(self, expr: ast.expr) -> str:
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, ast.Attribute):
            return ".".join(self._collect_attribute(expr))
        if isinstance(expr, ast.Subscript):
            return self._expr_to_name(expr.value)
        if isinstance(expr, ast.Call):
            return self._expr_to_name(expr.func)
        return ast.dump(expr)

    def _collect_attribute(self, node: ast.Attribute) -> List[str]:
        parts: List[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))


class InstantiationVisitor(ast.NodeVisitor):
    """Detecta llamadas a constructores dentro de una clase."""

    def __init__(self) -> None:
        self.instantiated_classes: Set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        target = self._expr_to_name(node.func)
        if target:
            self.instantiated_classes.add(target)
        self.generic_visit(node)

    def _expr_to_name(self, expr: ast.expr) -> Optional[str]:
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, ast.Attribute):
            return ".".join(self.collect_attribute(expr))
        return None

    @staticmethod
    def collect_attribute(node: ast.Attribute) -> List[str]:
        parts: List[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))


# ---------------------------------------------------------------------------
# Helper utilities


def _extract_type_names(node: Optional[ast.AST]) -> Set[str]:
    names: Set[str] = set()
    if node is None:
        return names
    if isinstance(node, ast.Name):
        names.add(node.id)
    elif isinstance(node, ast.Attribute):
        parts: List[str] = []
        current: ast.AST = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        if parts:
            names.add(".".join(reversed(parts)))
    elif isinstance(node, ast.Subscript):
        names.update(_extract_type_names(node.value))
        if isinstance(node.slice, ast.Tuple):
            for elt in node.slice.elts:
                names.update(_extract_type_names(elt))
        else:
            names.update(_extract_type_names(node.slice))
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):  # PEP 604 unions
        names.update(_extract_type_names(node.left))
        names.update(_extract_type_names(node.right))
    elif isinstance(node, ast.Tuple):
        for elt in node.elts:
            names.update(_extract_type_names(elt))
    return names


def _extract_references_from_assignment(node: ast.Assign) -> Set[str]:
    refs: Set[str] = set()
    if not isinstance(node.value, ast.Call):
        return refs
    target = _expr_to_name_simple(node.value.func)
    if not target:
        return refs
    lower = target.lower()
    if "relationship" in lower:
        for arg in node.value.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                refs.add(arg.value)
            else:
                refs.update(_extract_type_names(arg))
        for kw in node.value.keywords:
            refs.update(_extract_type_names(kw.value))
    return refs


def _expr_to_name_simple(expr: ast.AST) -> Optional[str]:
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        parts: List[str] = []
        current: ast.AST = expr
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    return None


# ---------------------------------------------------------------------------
# Construcción del grafo


def build_class_graph(
    root: Path,
    *,
    include_external: bool = True,
    edge_types: Optional[Set[str]] = None,
    module_prefixes: Optional[Set[str]] = None,
) -> Dict[str, object]:
    """
    Construye un grafo de relaciones de clases a partir del directorio dado.

    Args:
        root: ruta al workspace que se quiere analizar.

    Returns:
        Diccionario serializable con nodos, aristas y métricas.
    """
    root = root.expanduser().resolve()
    modules = list(_analyze_modules(root))
    filtered_modules = _filter_modules(modules, module_prefixes)
    definitions = _collect_definitions(filtered_modules)

    nodes: Dict[str, GraphNode] = {}
    edges: List[GraphEdge] = []
    edge_filter = edge_types or {"inherits", "instantiates", "references"}

    for module in filtered_modules:
        for class_name, class_info in module.classes.items():
            node_id = f"{module.module}.{class_name}"
            nodes[node_id] = GraphNode(
                id=node_id,
                name=class_name,
                module=module.module,
                file=str(module.file),
            )
            for edge in _build_edges_for_class(
                node_id=node_id,
                class_info=class_info,
                module=module,
                definitions=definitions,
                include_external=include_external,
            ):
                if edge.type not in edge_filter:
                    continue
                if not include_external and not edge.internal:
                    continue
                edges.append(edge)

    return {
        "nodes": [node.__dict__ for node in nodes.values()],
        "edges": [edge.__dict__ for edge in edges],
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "edges_by_type": _count_by_type(edges),
        },
    }


def _analyze_modules(root: Path) -> Iterable[ModuleInfo]:
    """Analyze Python modules in root, excluding common directories like .venv."""
    excluded_dirs = {
        "__pycache__",
        ".git",
        ".hg",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        "venv",
        "env",
        ".code-map",
        "node_modules",
        ".next",
        "dist",
        "build",
    }

    for path in root.rglob("*.py"):
        # Skip files in excluded directories
        if any(part in excluded_dirs for part in path.relative_to(root).parts):
            continue

        try:
            module = _module_name_from_path(root, path)
            tree = ast.parse(path.read_text(encoding="utf-8"))
            analyzer = ModuleAnalyzer(module=module, file_path=path)
            analyzer.visit(tree)
            yield analyzer.info
        except (OSError, SyntaxError):
            continue


def _module_name_from_path(root: Path, file_path: Path) -> str:
    relative = file_path.relative_to(root).with_suffix("")
    return ".".join(relative.parts)


def _collect_definitions(modules: Iterable[ModuleInfo]) -> Dict[str, ModuleInfo]:
    index: Dict[str, ModuleInfo] = {}
    for module in modules:
        for class_name in module.classes:
            key = f"{module.module}.{class_name}"
            index[key] = module
    return index


def _filter_modules(
    modules: List[ModuleInfo],
    module_prefixes: Optional[Set[str]],
) -> List[ModuleInfo]:
    if not module_prefixes:
        return modules

    normalized = {prefix.strip() for prefix in module_prefixes if prefix.strip()}
    if not normalized:
        return modules

    def matches(module_name: str) -> bool:
        return any(
            module_name == prefix or module_name.startswith(f"{prefix}.")
            for prefix in normalized
        )

    filtered: List[ModuleInfo] = []
    for module in modules:
        if matches(module.module):
            filtered.append(module)
    return filtered or modules


def _build_edges_for_class(
    *,
    node_id: str,
    class_info: ClassInfo,
    module: ModuleInfo,
    definitions: Dict[str, ModuleInfo],
    include_external: bool,
) -> List[GraphEdge]:
    edges: List[GraphEdge] = []

    for base in class_info.bases:
        target, internal, display = _resolve_reference(base, module, definitions)
        if not internal and not include_external:
            continue
        edges.append(
            GraphEdge(
                source=node_id,
                target=target or display,
                type="inherits",
                internal=internal,
                raw_target=display,
            )
        )

    for target_name in sorted(class_info.instantiates):
        target, internal, display = _resolve_reference(target_name, module, definitions)
        if not internal and not include_external:
            continue
        edges.append(
            GraphEdge(
                source=node_id,
                target=target or display,
                type="instantiates",
                internal=internal,
                raw_target=display,
            )
        )

    for ref_name in sorted(class_info.references):
        target, internal, display = _resolve_reference(ref_name, module, definitions)
        if not internal and not include_external:
            continue
        edges.append(
            GraphEdge(
                source=node_id,
                target=target or display,
                type="references",
                internal=internal,
                raw_target=display,
            )
        )

    return edges


def _resolve_reference(
    raw_name: str,
    module: ModuleInfo,
    definitions: Dict[str, ModuleInfo],
) -> Tuple[Optional[str], bool, str]:
    """
    Intenta resolver el nombre recibido contra las clases internas del proyecto.

    Returns:
        (target_id, internal, display_name)
    """
    if not raw_name:
        return None, False, raw_name

    candidates = _possible_qualified_names(raw_name, module)
    for candidate in candidates:
        if candidate in definitions:
            return candidate, True, candidate
    return None, False, raw_name


def _possible_qualified_names(raw_name: str, module: ModuleInfo) -> List[str]:
    """
    Genera nombres candidatos (fully-qualified) a partir de un nombre crudo.

    Considera clases locales, alias de imports y nombres simples.
    """
    candidates: List[str] = []

    # Caso 1: coincidencia con clase local
    if raw_name in module.classes:
        candidates.append(f"{module.module}.{raw_name}")

    # Caso 2: alias importado directamente (from foo import Bar as Baz)
    if raw_name in module.imports:
        target = module.imports[raw_name]
        candidates.append(target)

    # Caso 3: nombre compuesto módulo.clase
    if "." in raw_name:
        head, tail = raw_name.split(".", 1)
        if head in module.imports:
            target = module.imports[head]
            candidates.append(f"{target}.{tail}")
        else:
            candidates.append(raw_name)
    else:
        candidates.append(f"{module.module}.{raw_name}")

    # Eliminar duplicados manteniendo orden
    seen: Set[str] = set()
    unique: List[str] = []
    for name in candidates:
        if name not in seen:
            unique.append(name)
            seen.add(name)
    return unique


def _count_by_type(edges: Iterable[GraphEdge]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for edge in edges:
        counts[edge.type] = counts.get(edge.type, 0) + 1
    return counts
