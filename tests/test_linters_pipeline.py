from pathlib import Path

from code_map.linters import run_linters_pipeline


def test_run_linters_pipeline_generates_report(tmp_path: Path) -> None:
    pkg_dir = tmp_path / "pkg"
    tests_dir = tmp_path / "tests"
    pkg_dir.mkdir()
    tests_dir.mkdir()

    (pkg_dir / "__init__.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    (tests_dir / "test_pkg.py").write_text(
        "from pkg import add\n\n\ndef test_add() -> None:\n    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    report = run_linters_pipeline(tmp_path)

    assert report.summary.total_checks == len(report.tools) + len(report.custom_rules)
    assert report.summary.overall_status.value in {"pass", "warn", "fail", "skipped"}
    assert isinstance(report.metrics, dict)
    assert report.summary.duration_ms is not None
