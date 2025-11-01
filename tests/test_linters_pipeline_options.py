from pathlib import Path

from code_map.linters import LinterRunOptions, run_linters_pipeline, CheckStatus


def write_file(root: Path, name: str, content: str = "print('ok')\n") -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_pipeline_skips_when_no_tools_enabled(tmp_path: Path) -> None:
    write_file(tmp_path, "module.py")
    options = LinterRunOptions(enabled_tools=set())

    report = run_linters_pipeline(tmp_path, options=options)

    assert report.summary.overall_status == CheckStatus.SKIPPED
    assert report.notes and "No hay herramientas" in report.notes[0]


def test_pipeline_skips_when_project_exceeds_limit(tmp_path: Path) -> None:
    for index in range(3):
        write_file(tmp_path, f"pkg/file_{index}.py")

    options = LinterRunOptions(max_project_files=1)
    report = run_linters_pipeline(tmp_path, options=options)

    assert report.summary.overall_status == CheckStatus.SKIPPED
    assert "limite" in report.notes[0].lower()
