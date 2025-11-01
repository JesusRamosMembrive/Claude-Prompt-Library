import logging
from pathlib import Path

import pytest

from stage_init.initializer import InitializationConfig, ProjectInitializer


@pytest.fixture(autouse=True)
def _silence_logs():
    logging.basicConfig(level=logging.CRITICAL)
    yield


def test_initializer_dry_run_does_not_create_files(tmp_path: Path) -> None:
    project_path = tmp_path / "demo-project"
    config = InitializationConfig(
        project_path=project_path,
        existing_project=False,
        agent_selection="both",
        dry_run=True,
    )

    initializer = ProjectInitializer(config)
    result = initializer.run()

    assert not project_path.exists()
    assert "claude" in result.template_summaries
    claude_summary = result.template_summaries["claude"]
    assert claude_summary.copied  # would copy files
    assert not result.claude_md_created


def test_initializer_creates_files(tmp_path: Path) -> None:
    project_path = tmp_path / "real-project"
    config = InitializationConfig(
        project_path=project_path,
        existing_project=False,
        agent_selection="claude",
        dry_run=False,
        run_claude_init=False,  # avoid calling external CLI during tests
    )

    initializer = ProjectInitializer(config)
    result = initializer.run()

    assert project_path.exists()
    assert (project_path / ".claude").exists()
    assert (project_path / "docs").exists()
    assert result.template_summaries["claude"].copied
    assert result.stage_update is not None
