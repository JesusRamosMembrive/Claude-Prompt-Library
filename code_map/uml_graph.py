# SPDX-License-Identifier: MIT
"""Generador de modelo UML a partir del código del workspace."""

from __future__ import annotations

import ast
import html
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set


@dataclass
class AttributeInfo:
    name: str
    annotation: Optional[str] = None
    optional: bool = False


@dataclass
class MethodInfo:
    name: str
    parameters: List[str] = field(default_factory=list)
    returns: Optional[str] = None


@dataclass
class ClassModel:
    name: str
    module: str
    file: Path
    bases: List[str] = field(default_factory=list)
    attributes: List[AttributeInfo] = field(default_factory=list)
    methods: List[MethodInfo] = field(default_factory=list)
    associations: Set[str] = field(default_factory=set)
    instantiates: Set[str] = field(default_factory=set)  # Classes created via SomeClass()
    references: Set[str] = field(default_factory=set)  # Classes in type hints


@dataclass
class ModuleModel:
    name: str
    file: Path
    imports: Dict[str, str] = field(default_factory=dict)
    classes: Dict[str, ClassModel] = field(default_factory=dict)


class UMLModuleAnalyzer(ast.NodeVisitor):
    def __init__(self, module: str, file_path: Path) -> None:
        self.module = module
        self.file_path = file_path
        self.model = ModuleModel(name=module, file=file_path)
        self._current_class: Optional[ClassModel] = None

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            key = alias.asname or alias.name.split(".")[0]
            self.model.imports[key] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            if alias.name == "*":
                continue
            key = alias.asname or alias.name
            base = self._resolve_relative(module, node.level)
            full = f"{base}.{alias.name}" if base else alias.name
            self.model.imports[key] = full
        self.generic_visit(node)

    def _resolve_relative(self, module: str, level: int) -> str:
        if not level:
            return module
        parts = self.module.split(".")
        if level > len(parts):
            return module
        base = parts[:-level]
        if module:
            base.append(module)
        return ".".join(base)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        model = ClassModel(
            name=node.name,
            module=self.module,
            file=self.file_path,
            bases=[
                name
                for base in node.bases
                for name in [self._expr_to_name(base)]
                if name
            ],
        )
        self.model.classes[node.name] = model
        previous = self._current_class
        self._current_class = model
        self.generic_visit(node)
        self._current_class = previous

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._current_class is None:
            return
        params = [arg.arg for arg in node.args.args]
        if params and params[0] == "self":
            params = params[1:]
        returns = self._expr_to_name(node.returns) if node.returns else None
        self._current_class.methods.append(
            MethodInfo(name=node.name, parameters=params, returns=returns)
        )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect class instantiation: instance = SomeClass()"""
        if self._current_class is None:
            self.generic_visit(node)
            return
        target = self._expr_to_name(node.func)
        if target and target[0].isupper():  # Likely a class (PascalCase)
            self._current_class.instantiates.add(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self._current_class is None:
            return
        if isinstance(node.target, ast.Name):
            annotation = self._expr_to_name(node.annotation)
            optional = _is_optional(node.annotation)
            self._current_class.attributes.append(
                AttributeInfo(name=node.target.id, annotation=annotation, optional=optional)
            )
            if annotation:
                self._track_association(annotation)
            # Track type hints as references
            type_names = self._extract_type_names(node.annotation)
            self._current_class.references.update(type_names)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._current_class is None:
            return
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._current_class.attributes.append(AttributeInfo(name=target.id))
        if isinstance(node.value, ast.Call):
            func_name = self._expr_to_name(node.value.func)
            if func_name:
                lower = func_name.lower()
                if "relationship" in lower and node.value.args:
                    arg = node.value.args[0]
                    ref = None
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        ref = arg.value
                    else:
                        ref = self._expr_to_name(arg)
                    if ref:
                        self._track_association(ref)
        self.generic_visit(node)

    def _track_association(self, raw: str) -> None:
        name = raw.split("[")[0]
        if name:
            self._current_class.associations.add(name)

    def _expr_to_name(self, expr: Optional[ast.AST]) -> Optional[str]:
        if expr is None:
            return None
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, ast.Attribute):
            return ".".join(self._collect_attribute(expr))
        if isinstance(expr, ast.Subscript):
            return self._expr_to_name(expr.value)
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            return expr.value
        return None

    def _collect_attribute(self, node: ast.Attribute) -> List[str]:
        parts: List[str] = []
        current: ast.AST = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))

    def _extract_type_names(self, node: Optional[ast.AST]) -> Set[str]:
        """Extract all class names from type annotation (handles Union, List, Optional, etc.)"""
        names: Set[str] = set()
        if node is None:
            return names

        # Simple name: foo: Bar
        if isinstance(node, ast.Name):
            if node.id[0].isupper():  # Likely a class (PascalCase)
                names.add(node.id)

        # Subscript: List[User], Optional[Product]
        elif isinstance(node, ast.Subscript):
            # Recurse into base and slice
            names.update(self._extract_type_names(node.value))
            names.update(self._extract_type_names(node.slice))

        # Tuple of types: Union[A, B] or tuple annotation
        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                names.update(self._extract_type_names(elt))

        # Binary or: A | B (Python 3.10+)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            names.update(self._extract_type_names(node.left))
            names.update(self._extract_type_names(node.right))

        # Attribute: module.ClassName
        elif isinstance(node, ast.Attribute):
            attr_name = self._expr_to_name(node)
            if attr_name and attr_name[0].isupper():
                names.add(attr_name)

        # String literal (forward reference)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value and node.value[0].isupper():
                names.add(node.value)

        # Filter out built-in types
        builtin_types = {"List", "Dict", "Set", "Tuple", "Optional", "Union",
                        "Any", "Callable", "Type", "Sequence", "Iterable"}
        return {name for name in names if name not in builtin_types}


def _is_optional(expr: Optional[ast.AST]) -> bool:
    if expr is None:
        return False
    if isinstance(expr, ast.Subscript):
        base = expr.value
        if isinstance(base, ast.Name) and base.id in {"Optional", "Union"}:
            return True
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.BitOr):
        return True
    return False


def build_uml_model(
    root: Path,
    *,
    module_prefixes: Optional[Set[str]] = None,
    include_external: bool = False,
) -> Dict[str, object]:
    root = root.expanduser().resolve()
    modules = list(_analyze(root))
    modules = _filter_modules(modules, module_prefixes)
    index = _collect_definitions(modules)

    classes = []
    inheritance_edges = 0
    association_edges = 0
    instantiation_edges = 0
    reference_edges = 0

    for module in modules:
        for class_model in module.classes.values():
            bases = _resolve_bases(class_model, module, index, include_external)
            associations = _resolve_associations(class_model, module, index, include_external)
            instantiates = _resolve_references(class_model.instantiates, module, index, include_external)
            references = _resolve_references(class_model.references, module, index, include_external)

            inheritance_edges += len(bases)
            association_edges += len(associations)
            instantiation_edges += len(instantiates)
            reference_edges += len(references)

            classes.append(
                {
                    "id": f"{class_model.module}.{class_model.name}",
                    "name": class_model.name,
                    "module": class_model.module,
                    "file": str(class_model.file),
                    "bases": bases,
                    "attributes": [
                        {
                            "name": attr.name,
                            "type": attr.annotation,
                            "optional": attr.optional,
                        }
                        for attr in class_model.attributes
                    ],
                    "methods": [
                        {
                            "name": method.name,
                            "parameters": method.parameters,
                            "returns": method.returns,
                        }
                        for method in class_model.methods
                    ],
                    "associations": list(associations),
                    "instantiates": list(instantiates),
                    "references": list(references),
                }
            )

    stats = {
        "classes": len(classes),
        "inheritance_edges": inheritance_edges,
        "association_edges": association_edges,
        "instantiation_edges": instantiation_edges,
        "reference_edges": reference_edges,
    }

    return {"classes": classes, "stats": stats}


def build_uml_dot(model: Dict[str, object], edge_types: Optional[Set[str]] = None) -> str:
    """Generate Graphviz DOT format from UML model.

    Args:
        model: UML model with classes and relationships
        edge_types: Set of edge types to include. Valid values:
                   "inheritance", "association", "instantiation", "reference"
                   If None, defaults to all types.
    """
    if edge_types is None:
        edge_types = {"inheritance", "association", "instantiation", "reference"}

    classes: List[dict] = model.get("classes", [])  # type: ignore[assignment]
    lines: List[str] = [
        "digraph UML {",
        "  rankdir=LR;",
        '  graph [fontname="Inter", fontsize=11, overlap=false, splines=true, nodesep=0.6, ranksep=1.1, pad="0.3", margin=0];',
        '  node [shape=box, style="rounded,filled", fontname="Inter", fontsize=11, color="#1f2937", fillcolor="#111827", fontcolor="#e2e8f0", width=1.6, height=0.6, margin="0.12,0.06"];',
        '  edge [fontname="Inter", fontsize=9, color="#475569"];',
    ]

    # Add nodes
    for cls in classes:
        node_id = _escape_id(cls["id"])
        label = _build_node_label(cls)
        lines.append(f"  {node_id} [label={label}];")

    # Add edges based on requested types
    for cls in classes:
        source = _escape_id(cls["id"])

        # Inheritance (blue, solid, empty arrow)
        if "inheritance" in edge_types:
            for base in cls.get("bases", []):
                target = _escape_id(base)
                lines.append(
                    f'  {target} -> {source} [arrowhead=empty, penwidth=1.6, color="#60a5fa"];'
                )

        # Association (orange, dashed, normal arrow)
        if "association" in edge_types:
            for assoc in cls.get("associations", []):
                target = _escape_id(assoc)
                lines.append(
                    f'  {source} -> {target} [style=dashed, color="#f97316", arrowhead=normal];'
                )

        # Instantiation (green, dashed, diamond arrow)
        if "instantiation" in edge_types:
            for inst in cls.get("instantiates", []):
                target = _escape_id(inst)
                lines.append(
                    f'  {source} -> {target} [style=dashed, color="#10b981", arrowhead=diamond];'
                )

        # Reference (purple, dotted, vee arrow)
        if "reference" in edge_types:
            for ref in cls.get("references", []):
                target = _escape_id(ref)
                lines.append(
                    f'  {source} -> {target} [style=dotted, color="#a855f7", arrowhead=vee];'
                )

    lines.append("}")
    return "\n".join(lines)


def render_uml_svg(model: Dict[str, object], edge_types: Optional[Set[str]] = None) -> str:
    """Render UML model to SVG using Graphviz.

    Args:
        model: UML model with classes and relationships
        edge_types: Set of edge types to include in diagram
    """
    dot = build_uml_dot(model, edge_types)
    try:
        result = subprocess.run(
            ["dot", "-Tsvg"],
            input=dot.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except FileNotFoundError as exc:  # pragma: no cover
        raise RuntimeError("Graphviz 'dot' command no encontrado") from exc
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        raise RuntimeError(exc.stderr.decode("utf-8", errors="ignore")) from exc

    return result.stdout.decode("utf-8")


def _analyze(root: Path) -> Iterable[ModuleModel]:
    for path in root.rglob("*.py"):
        try:
            module = ".".join(path.relative_to(root).with_suffix("").parts)
            tree = ast.parse(path.read_text(encoding="utf-8"))
            analyzer = UMLModuleAnalyzer(module, path)
            analyzer.visit(tree)
            yield analyzer.model
        except (SyntaxError, OSError):  # pragma: no cover
            continue


def _filter_modules(modules: List[ModuleModel], prefixes: Optional[Set[str]]) -> List[ModuleModel]:
    if not prefixes:
        return modules
    normalized = {prefix.strip() for prefix in prefixes if prefix.strip()}
    if not normalized:
        return modules

    def matches(name: str) -> bool:
        return any(name == prefix or name.startswith(f"{prefix}.") for prefix in normalized)

    filtered = [module for module in modules if matches(module.name)]
    return filtered or modules


def _collect_definitions(modules: Iterable[ModuleModel]) -> Dict[str, ClassModel]:
    index: Dict[str, ClassModel] = {}
    for module in modules:
        for class_model in module.classes.values():
            key = f"{module.name}.{class_model.name}"
            index[key] = class_model
    return index


def _resolve_bases(
    class_model: ClassModel,
    module: ModuleModel,
    definitions: Dict[str, ClassModel],
    include_external: bool,
) -> List[str]:
    bases: List[str] = []
    for base in class_model.bases:
        if not base:
            continue
        target = _resolve_reference(base, module, definitions)
        if target or include_external:
            bases.append(target or base)
    return bases


def _resolve_associations(
    class_model: ClassModel,
    module: ModuleModel,
    definitions: Dict[str, ClassModel],
    include_external: bool,
) -> Set[str]:
    associations: Set[str] = set()
    for raw in class_model.associations:
        if not raw:
            continue
        target = _resolve_reference(raw, module, definitions)
        if target:
            associations.add(target)
        elif include_external:
            associations.add(raw)
    return associations


def _resolve_references(
    raw_refs: Set[str],
    module: ModuleModel,
    definitions: Dict[str, ClassModel],
    include_external: bool,
) -> Set[str]:
    """Resolve a set of raw class names to fully qualified names."""
    resolved: Set[str] = set()
    for raw in raw_refs:
        if not raw:
            continue
        target = _resolve_reference(raw, module, definitions)
        if target:
            resolved.add(target)
        elif include_external:
            resolved.add(raw)
    return resolved


def _resolve_reference(raw: str, module: ModuleModel, definitions: Dict[str, ClassModel]) -> Optional[str]:
    for candidate in _possible_names(raw, module):
        if candidate in definitions:
            return candidate
    return None


def _possible_names(raw: str, module: ModuleModel) -> List[str]:
    if raw is None:
        return []
    if not isinstance(raw, str):
        raw = str(raw)
    if not raw:
        return []
    candidates: List[str] = []
    if raw in module.classes:
        candidates.append(f"{module.name}.{raw}")
    if raw in module.imports:
        candidates.append(module.imports[raw])
    if "." in raw:
        head, tail = raw.split(".", 1)
        target = module.imports.get(head, head)
        candidates.append(f"{target}.{tail}")
    else:
        candidates.append(f"{module.name}.{raw}")
    seen: Set[str] = set()
    unique: List[str] = []
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return unique


def _escape_id(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def _build_node_label(cls: dict) -> str:
    name = html.escape(cls.get("name", ""))
    module = html.escape(cls.get("module", ""))
    if module:
        return f'<<b>{name}</b><br/><font point-size="9">{module}</font>>'
    return f'<<b>{name}</b>>'
