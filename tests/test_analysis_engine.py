from pathlib import Path

import pytest

from code_map import (
    ChangeBatch,
    ChangeEventType,
    ChangeScheduler,
    FileAnalyzer,
    ProjectScanner,
    SnapshotStore,
    SymbolIndex,
    SymbolKind,
)


def write_module(tmp_path: Path, relative: str, content: str) -> Path:
    target = tmp_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    return target


class FakeClock:
    def __init__(self) -> None:
        self._value = 0.0

    def advance(self, seconds: float) -> None:
        self._value += seconds

    def __call__(self) -> float:
        return self._value


def symbol_signatures(summary):
    return {
        (symbol.kind.value, symbol.name, symbol.parent or None)
        for symbol in summary.symbols
    }


def test_project_scanner_extracts_functions_classes_and_methods(tmp_path: Path) -> None:
    module_path = write_module(
        tmp_path,
        "pkg/sample.py",
        '''
def top_level():
    """Example function."""
    return 42


class Example:
    def method_one(self):
        pass

    async def method_two(self):
        pass
''',
    )

    scanner = ProjectScanner(tmp_path)
    results = scanner.scan()

    summary_by_path = {summary.path: summary for summary in results}
    summary = summary_by_path[module_path.resolve()]

    symbols = {(symbol.kind, symbol.name, symbol.parent) for symbol in summary.symbols}

    assert (SymbolKind.FUNCTION, "top_level", None) in symbols
    assert (SymbolKind.CLASS, "Example", None) in symbols
    assert (SymbolKind.METHOD, "method_one", "Example") in symbols
    assert (SymbolKind.METHOD, "method_two", "Example") in symbols


def test_file_analyzer_optionally_includes_docstrings(tmp_path: Path) -> None:
    module_path = write_module(
        tmp_path,
        "doc.py",
        '''
"""Module docstring."""


def foo():
    """Foo docstring."""
    return 0


class Bar:
    """Bar docstring."""

    def baz(self):
        """Baz docstring."""
        return 1
''',
    )

    analyzer_without_docs = FileAnalyzer(include_docstrings=False)
    summary_without_docs = analyzer_without_docs.parse(module_path)
    assert all(symbol.docstring is None for symbol in summary_without_docs.symbols)

    analyzer_with_docs = FileAnalyzer(include_docstrings=True)
    summary_with_docs = analyzer_with_docs.parse(module_path)

    docs = {symbol.name: symbol.docstring for symbol in summary_with_docs.symbols}
    assert docs["foo"] == "Foo docstring."
    assert docs["Bar"] == "Bar docstring."
    assert docs["baz"] == "Baz docstring."


def test_symbol_index_builds_tree_structure(tmp_path: Path) -> None:
    write_module(tmp_path, "a/__init__.py", "")
    file_one = write_module(tmp_path, "a/feature.py", "def run():\n    return True")
    file_two = write_module(tmp_path, "b/util.py", "class Helper:\n    def work(self):\n        return True")

    scanner = ProjectScanner(tmp_path)
    summaries = scanner.scan()

    index = SymbolIndex(tmp_path)
    index.update(summaries)

    tree = index.get_tree()
    assert tree.is_dir
    assert "a" in tree.children
    assert "b" in tree.children

    feature_node = tree.children["a"].children["feature.py"]
    util_node = tree.children["b"].children["util.py"]

    assert feature_node.file_summary.path == file_one.resolve()
    assert util_node.file_summary.path == file_two.resolve()
    assert any(symbol.name == "run" for symbol in feature_node.file_summary.symbols)
    assert any(symbol.name == "Helper" for symbol in util_node.file_summary.symbols)


def test_project_scanner_handles_js_files(tmp_path: Path) -> None:
    pytest.importorskip("esprima")
    write_module(tmp_path, "pkg/module.py", "def foo():\n    return 1")
    write_module(
        tmp_path,
        "pkg/helpers.js",
        "export function sum(a, b) { return a + b; }",
    )

    scanner = ProjectScanner(tmp_path)
    results = scanner.scan()

    filenames = {summary.path.name for summary in results}
    assert "helpers.js" in filenames

    js_summary = next(summary for summary in results if summary.path.name == "helpers.js")
    symbol_names = {symbol.name for symbol in js_summary.symbols}
    assert "sum" in symbol_names


def test_project_scanner_handles_complex_js_patterns(tmp_path: Path) -> None:
    pytest.importorskip("esprima")
    write_module(
        tmp_path,
        "pkg/math.js",
        """
/**
 * Colección de utilidades matemáticas.
 */
export class Calculator {
  add(a, b) {
    return a + b;
  }

  multiply(a, b) {
    return a * b;
  }
}

export const identity = (value) => value;

const format = function (value) {
  return String(value).trim();
};
""",
    )

    scanner = ProjectScanner(tmp_path)
    results = scanner.scan()
    js_summary = next(summary for summary in results if summary.path.name == "math.js")

    signatures = symbol_signatures(js_summary)
    expected = {
        ("class", "Calculator", None),
        ("method", "add", "Calculator"),
        ("method", "multiply", "Calculator"),
        ("function", "identity", None),
        ("function", "format", None),
    }
    assert expected <= signatures


def test_project_scanner_handles_ts_files(tmp_path: Path) -> None:
    pytest.importorskip("tree_sitter_languages")
    write_module(
        tmp_path,
        "pkg/service.ts",
        """
export class Service {
  run(): void {}
}

export const handler = (value: number): number => value * 2;
""",
    )

    scanner = ProjectScanner(tmp_path)
    results = scanner.scan()

    ts_summary = next(summary for summary in results if summary.path.name == "service.ts")
    names = {symbol.name for symbol in ts_summary.symbols}
    assert {"Service", "handler"} <= names


def test_project_scanner_handles_ts_methods_and_exports(tmp_path: Path) -> None:
    pytest.importorskip("tree_sitter_languages")
    write_module(
        tmp_path,
        "pkg/toolkit.ts",
        """
export class Toolbox {
  constructor(private readonly prefix: string) {}

  format(value: string): string {
    return `${this.prefix}:${value}`;
  }

  static version(): string {
    return "1.0.0";
  }
}

export const mapValues = <T, R>(items: T[], fn: (item: T) => R): R[] => {
  return items.map(fn);
};

function helper(input: number): number {
  return input * 10;
}
""",
    )

    scanner = ProjectScanner(tmp_path)
    results = scanner.scan()

    ts_summary = next(summary for summary in results if summary.path.name == "toolkit.ts")
    signatures = symbol_signatures(ts_summary)
    expected = {
        ("class", "Toolbox", None),
        ("method", "format", "Toolbox"),
        ("method", "version", "Toolbox"),
        ("function", "mapValues", None),
        ("function", "helper", None),
    }
    assert expected <= signatures


def test_project_scanner_handles_html_files(tmp_path: Path) -> None:
    pytest.importorskip("bs4")
    write_module(
        tmp_path,
        "page/index.html",
        """
<!DOCTYPE html>
<html>
  <body>
    <div id="app">Hello</div>
    <custom-element></custom-element>
  </body>
</html>
""",
    )

    scanner = ProjectScanner(tmp_path)
    summaries = scanner.scan()

    html_summary = next(summary for summary in summaries if summary.path.name == "index.html")
    names = {symbol.name for symbol in html_summary.symbols}
    assert "app" in names
    assert "custom-element" in names


def test_snapshot_store_persists_and_restores_summaries(tmp_path: Path) -> None:
    module_path = write_module(tmp_path, "pkg/sample.py", "def foo():\n    return 1")
    scanner = ProjectScanner(tmp_path)
    summaries = scanner.scan()

    store = SnapshotStore(tmp_path)
    store.save(summaries)

    snapshot_file = tmp_path / ".code-map" / "code-map.json"
    assert snapshot_file.exists()

    index = SymbolIndex(tmp_path)
    loaded = index.load_snapshot(store)

    assert len(loaded) == 1
    restored = index.get_file(module_path.resolve())
    assert restored is not None
    assert any(symbol.name == "foo" for symbol in restored.symbols)


def test_scanner_can_hydrate_index_from_snapshot(tmp_path: Path) -> None:
    module_path = write_module(tmp_path, "pkg/example.py", "class A:\n    def run(self):\n        return True")

    scanner = ProjectScanner(tmp_path)
    index = SymbolIndex(tmp_path)
    scanner.scan_and_update_index(index, persist=True)

    # Emulate nuevo arranque con índice vacío
    fresh_index = SymbolIndex(tmp_path)
    summaries = scanner.hydrate_index_from_snapshot(fresh_index)

    assert summaries
    restored = fresh_index.get_file(module_path.resolve())
    assert restored is not None
    assert any(symbol.kind is SymbolKind.CLASS for symbol in restored.symbols)


def test_change_scheduler_debounce_and_collapse(tmp_path: Path) -> None:
    clock = FakeClock()
    scheduler = ChangeScheduler(debounce_seconds=0.1, clock=clock)
    module_path = tmp_path / "sample.py"

    scheduler.enqueue(ChangeEventType.CREATED, module_path)
    assert scheduler.drain() is None  # aún dentro del debounce

    clock.advance(0.11)
    batch = scheduler.drain()
    assert batch is not None
    assert module_path.resolve() in batch.created
    assert module_path.resolve() not in batch.modified

    scheduler.enqueue(ChangeEventType.CREATED, module_path)
    scheduler.enqueue(ChangeEventType.MODIFIED, module_path)
    clock.advance(0.11)
    batch = scheduler.drain()
    assert batch is not None
    assert module_path.resolve() in batch.created
    assert module_path.resolve() not in batch.modified

    dest_path = tmp_path / "renamed.py"
    scheduler.enqueue(ChangeEventType.MOVED, module_path, dest_path=dest_path)
    clock.advance(0.11)
    batch = scheduler.drain()
    assert batch is not None
    assert module_path.resolve() in batch.deleted
    assert dest_path.resolve() in batch.created


def test_scanner_apply_change_batch_updates_index(tmp_path: Path) -> None:
    module_path = write_module(tmp_path, "pkg/module.py", "def foo():\n    return 1")

    scanner = ProjectScanner(tmp_path)
    index = SymbolIndex(tmp_path)
    scanner.scan_and_update_index(index)

    # modificar archivo existente
    module_path.write_text("def foo():\n    return 2\n", encoding="utf-8")
    batch = ChangeBatch(modified=[module_path])

    result = scanner.apply_change_batch(batch, index)
    assert module_path.resolve() in result["updated"]

    summary = index.get_file(module_path.resolve())
    assert summary is not None
    assert any(symbol.name == "foo" for symbol in summary.symbols)


def test_scanner_apply_change_batch_handles_deletions(tmp_path: Path) -> None:
    module_path = write_module(tmp_path, "pkg/remove.py", "def bar():\n    return 3")

    scanner = ProjectScanner(tmp_path)
    index = SymbolIndex(tmp_path)
    scanner.scan_and_update_index(index)

    module_path.unlink()
    batch = ChangeBatch(deleted=[module_path])

    result = scanner.apply_change_batch(batch, index)
    assert module_path.resolve() in result["deleted"]
    assert index.get_file(module_path.resolve()) is None
