# SPDX-License-Identifier: MIT
"""Generador de modelo UML a partir del código del workspace."""

from __future__ import annotations

import ast
import html
import shutil
import subprocess  # nosec B404 - se invoca Graphviz 'dot' de forma controlada
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from .ast_utils import ImportResolver


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
    instantiates: Set[str] = field(
        default_factory=set
    )  # Classes created via SomeClass()
    references: Set[str] = field(default_factory=set)  # Classes in type hints


@dataclass
class ModuleModel:
    name: str
    file: Path
    imports: Dict[str, str] = field(default_factory=dict)
    classes: Dict[str, ClassModel] = field(default_factory=dict)


@dataclass
class GraphvizStyleOptions:
    layout_engine: str = "dot"
    rankdir: str = "LR"
    splines: str = "true"
    nodesep: float = 0.6
    ranksep: float = 1.1
    pad: float = 0.3
    margin: float = 0.0
    bgcolor: str = "#0b1120"
    graph_fontname: str = "Inter"
    graph_fontsize: int = 11
    node_shape: str = "box"
    node_style: str = "rounded,filled"
    node_fillcolor: str = "#111827"
    node_color: str = "#1f2937"
    node_fontcolor: str = "#e2e8f0"
    node_fontname: str = "Inter"
    node_fontsize: int = 11
    node_width: float = 1.6
    node_height: float = 0.6
    node_margin_x: float = 0.12
    node_margin_y: float = 0.06
    edge_color: str = "#475569"
    edge_fontname: str = "Inter"
    edge_fontsize: int = 9
    edge_penwidth: float = 1.0
    inheritance_style: str = "solid"
    inheritance_color: str = "#60a5fa"
    association_color: str = "#f97316"
    instantiation_color: str = "#10b981"
    reference_color: str = "#a855f7"
    inheritance_arrowhead: str = "empty"
    association_arrowhead: str = "normal"
    instantiation_arrowhead: str = "diamond"
    reference_arrowhead: str = "vee"
    association_style: str = "dashed"
    instantiation_style: str = "dashed"
    reference_style: str = "dotted"


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
        """Resolve relative imports to absolute module paths."""
        return ImportResolver.resolve_relative_import(self.module, module, level)

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
                AttributeInfo(
                    name=node.target.id, annotation=annotation, optional=optional
                )
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
        if self._current_class is None:
            return
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
        builtin_types = {
            "List",
            "Dict",
            "Set",
            "Tuple",
            "Optional",
            "Union",
            "Any",
            "Callable",
            "Type",
            "Sequence",
            "Iterable",
        }
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
            associations = _resolve_associations(
                class_model, module, index, include_external
            )
            instantiates = _resolve_references(
                class_model.instantiates, module, index, include_external
            )
            references = _resolve_references(
                class_model.references, module, index, include_external
            )

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


def build_uml_dot(
    model: Dict[str, object],
    edge_types: Optional[Set[str]] = None,
    graphviz: Optional[GraphvizStyleOptions] = None,
) -> str:
    """Generate Graphviz DOT format from UML model.

    Args:
        model: UML model with classes and relationships
        edge_types: Set of edge types to include. Valid values:
                   "inheritance", "association", "instantiation", "reference"
                   If None, defaults to all types.
        graphviz: Styling and layout options for Graphviz.
    """
    if edge_types is None:
        edge_types = {"inheritance", "association", "instantiation", "reference"}

    options = _prepare_graphviz_options(graphviz)

    splines_attr = (
        options.splines
        if options.splines.lower() in {"true", "false"}
        else f'"{_quote_attr(options.splines)}"'
    )

    classes: List[dict] = model.get("classes", [])  # type: ignore[assignment]
    lines: List[str] = [
        "digraph UML {",
        f"  rankdir={options.rankdir};",
        '  graph [fontname="'
        + _quote_attr(options.graph_fontname)
        + f'", fontsize={options.graph_fontsize}, overlap=false, splines={splines_attr}, nodesep={_format_float(options.nodesep)}, ranksep={_format_float(options.ranksep)}, pad="{_format_float(options.pad)}", margin="{_format_float(options.margin)}", bgcolor="{_quote_attr(options.bgcolor)}"];',
        "  node [shape="
        + options.node_shape
        + ', style="'
        + _quote_attr(options.node_style)
        + '", fontname="'
        + _quote_attr(options.node_fontname)
        + f'", fontsize={options.node_fontsize}, color="{_quote_attr(options.node_color)}", fillcolor="{_quote_attr(options.node_fillcolor)}", fontcolor="{_quote_attr(options.node_fontcolor)}", width={_format_float(options.node_width)}, height={_format_float(options.node_height)}, margin="{_format_float(options.node_margin_x)},{_format_float(options.node_margin_y)}"];',
        '  edge [fontname="'
        + _quote_attr(options.edge_fontname)
        + f'", fontsize={options.edge_fontsize}, color="{_quote_attr(options.edge_color)}", penwidth={_format_float(options.edge_penwidth)}];',
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
                    "  "
                    + target
                    + " -> "
                    + source
                    + ' [style="'
                    + _quote_attr(options.inheritance_style)
                    + '", arrowhead="'
                    + _quote_attr(options.inheritance_arrowhead)
                    + '", penwidth='
                    + _format_float(options.edge_penwidth)
                    + f', color="{_quote_attr(options.inheritance_color)}"];'
                )

        # Association (orange, dashed, normal arrow)
        if "association" in edge_types:
            for assoc in cls.get("associations", []):
                target = _escape_id(assoc)
                lines.append(
                    "  "
                    + source
                    + " -> "
                    + target
                    + ' [style="'
                    + _quote_attr(options.association_style)
                    + '", penwidth='
                    + _format_float(options.edge_penwidth)
                    + f', color="{_quote_attr(options.association_color)}", arrowhead="{_quote_attr(options.association_arrowhead)}"];'
                )

        # Instantiation (green, dashed, diamond arrow)
        if "instantiation" in edge_types:
            for inst in cls.get("instantiates", []):
                target = _escape_id(inst)
                lines.append(
                    "  "
                    + source
                    + " -> "
                    + target
                    + ' [style="'
                    + _quote_attr(options.instantiation_style)
                    + '", penwidth='
                    + _format_float(options.edge_penwidth)
                    + f', color="{_quote_attr(options.instantiation_color)}", arrowhead="{_quote_attr(options.instantiation_arrowhead)}"];'
                )

        # Reference (purple, dotted, vee arrow)
        if "reference" in edge_types:
            for ref in cls.get("references", []):
                target = _escape_id(ref)
                lines.append(
                    "  "
                    + source
                    + " -> "
                    + target
                    + ' [style="'
                    + _quote_attr(options.reference_style)
                    + '", penwidth='
                    + _format_float(options.edge_penwidth)
                    + f', color="{_quote_attr(options.reference_color)}", arrowhead="{_quote_attr(options.reference_arrowhead)}"];'
                )

    lines.append("}")
    return "\n".join(lines)


def render_uml_svg(
    model: Dict[str, object],
    edge_types: Optional[Set[str]] = None,
    graphviz: Optional[GraphvizStyleOptions] = None,
) -> str:
    """Render UML model to SVG using Graphviz.

    Args:
        model: UML model with classes and relationships
        edge_types: Set of edge types to include in diagram
        graphviz: Styling/layout options forwarded to Graphviz.
    """
    options = _prepare_graphviz_options(graphviz)
    dot = build_uml_dot(model, edge_types, options)
    engine = options.layout_engine or "dot"
    dot_binary = shutil.which(engine)
    if not dot_binary:
        dot_binary = shutil.which("dot")
    if not dot_binary:
        raise RuntimeError("Graphviz command not found (looked for dot/neato family)")
    try:
        result = subprocess.run(  # nosec B603 - se ejecuta binario validado de Graphviz
            [dot_binary, "-Tsvg"],
            input=dot.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        raise RuntimeError(exc.stderr.decode("utf-8", errors="ignore")) from exc

    return result.stdout.decode("utf-8")


def _prepare_graphviz_options(
    graphviz: Optional[GraphvizStyleOptions],
) -> GraphvizStyleOptions:
    source = graphviz or GraphvizStyleOptions()
    return GraphvizStyleOptions(
        layout_engine=_normalize_layout_engine(source.layout_engine),
        rankdir=_normalize_rankdir(source.rankdir),
        splines=_normalize_splines(source.splines),
        nodesep=_clamp_float(source.nodesep, default=0.6, minimum=0.1),
        ranksep=_clamp_float(source.ranksep, default=1.1, minimum=0.4),
        pad=_clamp_float(source.pad, default=0.3, minimum=0.0),
        margin=_clamp_float(source.margin, default=0.0, minimum=0.0),
        bgcolor=_sanitize_string(source.bgcolor, "#0b1120"),
        graph_fontname=_sanitize_string(source.graph_fontname, "Inter"),
        graph_fontsize=_clamp_int(source.graph_fontsize, default=11, minimum=6),
        node_shape=_normalize_node_shape(source.node_shape),
        node_style=_sanitize_string(source.node_style, "rounded,filled"),
        node_fillcolor=_sanitize_string(source.node_fillcolor, "#111827"),
        node_color=_sanitize_string(source.node_color, "#1f2937"),
        node_fontcolor=_sanitize_string(source.node_fontcolor, "#e2e8f0"),
        node_fontname=_sanitize_string(source.node_fontname, "Inter"),
        node_fontsize=_clamp_int(source.node_fontsize, default=11, minimum=6),
        node_width=_clamp_float(source.node_width, default=1.6, minimum=0.2),
        node_height=_clamp_float(source.node_height, default=0.6, minimum=0.2),
        node_margin_x=_clamp_float(source.node_margin_x, default=0.12, minimum=0.02),
        node_margin_y=_clamp_float(source.node_margin_y, default=0.06, minimum=0.02),
        edge_color=_sanitize_string(source.edge_color, "#475569"),
        edge_fontname=_sanitize_string(source.edge_fontname, "Inter"),
        edge_fontsize=_clamp_int(source.edge_fontsize, default=9, minimum=6),
        edge_penwidth=_clamp_float(source.edge_penwidth, default=1.0, minimum=0.5),
        inheritance_style=_sanitize_string(source.inheritance_style, "solid"),
        inheritance_color=_sanitize_string(source.inheritance_color, "#60a5fa"),
        association_color=_sanitize_string(source.association_color, "#f97316"),
        instantiation_color=_sanitize_string(source.instantiation_color, "#10b981"),
        reference_color=_sanitize_string(source.reference_color, "#a855f7"),
        inheritance_arrowhead=_sanitize_string(source.inheritance_arrowhead, "empty"),
        association_arrowhead=_sanitize_string(source.association_arrowhead, "normal"),
        instantiation_arrowhead=_sanitize_string(
            source.instantiation_arrowhead, "diamond"
        ),
        reference_arrowhead=_sanitize_string(source.reference_arrowhead, "vee"),
        association_style=_sanitize_string(source.association_style, "dashed"),
        instantiation_style=_sanitize_string(source.instantiation_style, "dashed"),
        reference_style=_sanitize_string(source.reference_style, "dotted"),
    )


def _normalize_layout_engine(value: Optional[str]) -> str:
    allowed = {"dot", "neato", "fdp", "sfdp", "circo", "twopi"}
    candidate = (value or "dot").lower()
    return candidate if candidate in allowed else "dot"


def _normalize_rankdir(value: Optional[str]) -> str:
    allowed = {"TB", "BT", "LR", "RL"}
    candidate = (value or "LR").upper()
    return candidate if candidate in allowed else "LR"


def _normalize_splines(value: Optional[str]) -> str:
    if value is None:
        return "true"
    candidate = value.strip().lower()
    if candidate in {"true", "false"}:
        return candidate
    allowed = {"line", "polyline", "spline", "curved", "ortho"}
    return candidate if candidate in allowed else "true"


def _normalize_node_shape(value: Optional[str]) -> str:
    allowed = {
        "box",
        "rect",
        "ellipse",
        "plaintext",
        "record",
        "component",
        "cylinder",
        "tab",
    }
    candidate = (value or "box").lower()
    return candidate if candidate in allowed else "box"


def _clamp_float(
    value: Optional[float],
    *,
    default: float,
    minimum: float,
    maximum: Optional[float] = None,
) -> float:
    try:
        numeric = float(value) if value is not None else default
    except (TypeError, ValueError):
        numeric = default
    if maximum is not None:
        numeric = min(numeric, maximum)
    if numeric < minimum:
        numeric = minimum
    return numeric


def _clamp_int(
    value: Optional[int],
    *,
    default: int,
    minimum: int,
    maximum: Optional[int] = None,
) -> int:
    try:
        numeric = int(value) if value is not None else default
    except (TypeError, ValueError):
        numeric = default
    if maximum is not None:
        numeric = min(numeric, maximum)
    if numeric < minimum:
        numeric = minimum
    return numeric


def _sanitize_string(value: Optional[str], fallback: str) -> str:
    candidate = (value or "").strip()
    return candidate or fallback


def _format_float(value: float) -> str:
    formatted = f"{value:.3f}"
    return formatted.rstrip("0").rstrip(".") or "0"


def _quote_attr(value: str) -> str:
    return value.replace('"', '\\"')


def _analyze(
    root: Path, excluded_dirs: Optional[Set[str]] = None
) -> Iterable[ModuleModel]:
    """Analyze Python files in the root directory, excluding certain directories.

    Args:
        root: Root directory to scan
        excluded_dirs: Set of directory names to exclude (e.g., .venv, __pycache__)
    """
    if excluded_dirs is None:
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
        # Check if any part of the path is in excluded_dirs
        if any(part in excluded_dirs for part in path.relative_to(root).parts):
            continue

        try:
            module = ".".join(path.relative_to(root).with_suffix("").parts)
            tree = ast.parse(path.read_text(encoding="utf-8"))
            analyzer = UMLModuleAnalyzer(module, path)
            analyzer.visit(tree)
            yield analyzer.model
        except (SyntaxError, OSError):  # pragma: no cover
            continue


def _filter_modules(
    modules: List[ModuleModel], prefixes: Optional[Set[str]]
) -> List[ModuleModel]:
    if not prefixes:
        return modules
    normalized = {prefix.strip() for prefix in prefixes if prefix.strip()}
    if not normalized:
        return modules

    def matches(name: str) -> bool:
        return any(
            name == prefix or name.startswith(f"{prefix}.") for prefix in normalized
        )

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


def _resolve_reference(
    raw: str, module: ModuleModel, definitions: Dict[str, ClassModel]
) -> Optional[str]:
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
    return f"<<b>{name}</b>>"
