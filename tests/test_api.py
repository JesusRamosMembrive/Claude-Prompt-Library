import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient

from code_map import ChangeScheduler
from code_map.api.routes import router
from code_map.linters import (
    ChartData,
    CheckStatus,
    CoverageSnapshot,
    CustomRuleResult,
    IssueDetail,
    LintersReport,
    ReportSummary,
    Severity,
    ToolRunResult,
    record_linters_report,
    record_notification,
)
from code_map.settings import load_settings, save_settings
from code_map.state import AppState


def write_file(root: Path, relative: str, content: str) -> Path:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    return target


def create_test_app(root: Path) -> tuple[FastAPI, AppState]:
    db_path = root / "state.db"
    os.environ["CODE_MAP_DB_PATH"] = str(db_path)
    os.environ["CODE_MAP_DISABLE_LINTERS"] = "1"

    test_env = dict(os.environ)
    settings = load_settings(root_override=root, env=test_env)
    scheduler = ChangeScheduler()
    state = AppState(settings=settings, scheduler=scheduler)
    save_settings(state.settings, env=test_env)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await state.startup()
        try:
            yield
        finally:
            await state.shutdown()

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    app.state.app_state = state  # type: ignore[attr-defined]

    return app, state


def build_sample_report(root: Path) -> LintersReport:
    now = datetime.now(timezone.utc)
    summary = ReportSummary(
        overall_status=CheckStatus.WARN,
        total_checks=5,
        checks_passed=3,
        checks_warned=1,
        checks_failed=1,
        duration_ms=1200,
        files_scanned=10,
        lines_scanned=500,
        issues_total=4,
        critical_issues=1,
    )

    issues = [
        IssueDetail(
            message="Importación sin usar",
            file="pkg/module.py",
            line=12,
            code="F401",
            severity=Severity.LOW,
        )
    ]

    tools = [
        ToolRunResult(
            key="ruff",
            name="Ruff",
            status=CheckStatus.FAIL,
            issues_found=2,
            issues_sample=issues,
            version="0.0.0-test",
        )
    ]

    custom_rules = [
        CustomRuleResult(
            key="max_file_length",
            name="Longitud máxima",
            status=CheckStatus.WARN,
            description="Archivo supera el umbral",
            threshold=500,
            violations=[
                IssueDetail(
                    message="Archivo demasiado largo",
                    file="pkg/module.py",
                    line=None,
                    severity=Severity.HIGH,
                )
            ],
        )
    ]

    coverage = CoverageSnapshot(statement_coverage=82.5, branch_coverage=70.0, missing_lines=42)
    chart = ChartData(
        issues_by_tool={"ruff": 2},
        issues_by_severity={Severity.HIGH: 1, Severity.LOW: 2},
        top_offenders=["pkg/module.py"],
    )

    return LintersReport(
        root_path=str(root.resolve()),
        generated_at=now,
        summary=summary,
        tools=tools,
        custom_rules=custom_rules,
        coverage=coverage,
        metrics={"duration_ms": 1200.0},
        chart_data=chart,
        notes=["Reporte generado para pruebas"],
    )


@pytest.fixture()
def api_client(tmp_path: Path) -> TestClient:
    write_file(
        tmp_path,
        "pkg/module.py",
        """
class Demo:
    def run(self):
        return True


def helper():
    return 123
""",
    )
    app, state = create_test_app(tmp_path)
    with TestClient(app) as client:
        yield client


def test_health_endpoint(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tree_endpoint_returns_structure(api_client: TestClient) -> None:
    response = api_client.get("/tree")
    data = response.json()
    assert response.status_code == 200
    assert data["is_dir"] is True
    assert any(child["name"] == "pkg" for child in data["children"])


def test_files_endpoint_returns_summary(api_client: TestClient) -> None:
    response = api_client.get("/files/pkg/module.py")
    assert response.status_code == 200
    payload = response.json()
    assert payload["path"] == "pkg/module.py"
    symbol_names = {symbol["name"] for symbol in payload["symbols"]}
    assert {"Demo", "helper"} <= symbol_names


def test_search_endpoint_returns_results(api_client: TestClient) -> None:
    response = api_client.get("/search", params={"q": "demo"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert any(item["name"] == "Demo" for item in results)


def test_rescan_endpoint_triggers_scan(api_client: TestClient, tmp_path: Path) -> None:
    response = api_client.post("/rescan")
    assert response.status_code == 200
    assert response.json()["files"] >= 1


def test_get_settings_endpoint(api_client: TestClient) -> None:
    response = api_client.get("/settings")
    assert response.status_code == 200
    payload = response.json()
    assert payload["root_path"]
    assert payload["absolute_root"].startswith("/")
    assert payload["include_docstrings"] is True
    assert "exclude_dirs" in payload


def test_update_settings_toggle_docstrings(api_client: TestClient) -> None:
    response = api_client.put("/settings", json={"include_docstrings": False})
    assert response.status_code == 200
    body = response.json()
    assert "include_docstrings" in body["updated"]
    assert body["settings"]["include_docstrings"] is False


def test_update_settings_updates_exclude_dirs(api_client: TestClient) -> None:
    response = api_client.put("/settings", json={"exclude_dirs": ["build", "dist"]})
    assert response.status_code == 200
    body = response.json()
    assert "exclude_dirs" in body["updated"]
    excludes = body["settings"]["exclude_dirs"]
    assert "build" in excludes
    assert "dist" in excludes


def test_update_settings_invalid_root_returns_400(api_client: TestClient) -> None:
    response = api_client.put("/settings", json={"root_path": "/path/that/does/not/exist"})
    assert response.status_code == 400


def test_status_endpoint_returns_metrics(api_client: TestClient) -> None:
    response = api_client.get("/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["files_indexed"] >= 1
    assert "symbols_indexed" in payload
    assert payload["watcher_active"] in {True, False}
    assert isinstance(payload["capabilities"], list)


def test_preview_endpoint_returns_html(tmp_path: Path) -> None:
    app, _state = create_test_app(tmp_path)
    write_file(tmp_path, "page/index.html", "<html><body>Hi</body></html>")
    with TestClient(app) as client:
        response = client.get("/preview", params={"path": "page/index.html"})
        assert response.status_code == 200
        assert response.text.strip() == "<html><body>Hi</body></html>"
        assert "text/html" in response.headers.get("content-type", "")


def test_preview_endpoint_returns_plain_text(tmp_path: Path) -> None:
    app, _state = create_test_app(tmp_path)
    write_file(tmp_path, "notes/info.txt", "Just text content")
    with TestClient(app) as client:
        response = client.get("/preview", params={"path": "notes/info.txt"})
        assert response.status_code == 200
        assert response.text.strip() == "Just text content"
        assert response.headers.get("content-type") == "text/plain; charset=utf-8"


def test_preview_endpoint_missing_file_returns_404(tmp_path: Path) -> None:
    app, _state = create_test_app(tmp_path)
    with TestClient(app) as client:
        response = client.get("/preview", params={"path": "unknown/file.md"})
        assert response.status_code == 404


def test_linters_discovery_endpoint(api_client: TestClient) -> None:
    response = api_client.get("/linters/discovery")
    assert response.status_code == 200
    payload = response.json()
    assert payload["root_path"]
    expected = {"ruff", "black", "mypy", "bandit", "pytest", "pytest_cov", "pre_commit"}
    tool_keys = {tool["key"] for tool in payload["tools"]}
    assert expected <= tool_keys
    assert all(isinstance(tool["installed"], bool) for tool in payload["tools"])
    assert any(rule["key"] == "max_file_length" for rule in payload["custom_rules"])
    assert isinstance(payload["notifications"], list)


def test_linters_reports_endpoints(api_client: TestClient, tmp_path: Path) -> None:
    report = build_sample_report(tmp_path)
    report_id = record_linters_report(report)

    list_response = api_client.get("/linters/reports")
    assert list_response.status_code == 200
    items = list_response.json()
    assert any(item["id"] == report_id for item in items)

    latest_response = api_client.get("/linters/reports/latest")
    assert latest_response.status_code == 200
    latest = latest_response.json()
    assert latest["report"]["summary"]["overall_status"] == "warn"
    assert latest["report"]["chart_data"]["issues_by_tool"]["ruff"] == 2

    detail_response = api_client.get(f"/linters/reports/{report_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == report_id
    assert detail["report"]["custom_rules"][0]["violations"][0]["severity"] == "high"

    missing_response = api_client.get("/linters/reports/9999")
    assert missing_response.status_code == 404


def test_linters_notifications_flow(api_client: TestClient, tmp_path: Path) -> None:
    notification_id = record_notification(
        channel="linters",
        severity=Severity.CRITICAL,
        title="Fallo crítico",
        message="Se detectó un fallo grave",
        root_path=tmp_path,
        payload={"report_id": 1},
    )

    list_response = api_client.get("/linters/notifications")
    assert list_response.status_code == 200
    notifications = list_response.json()
    assert any(item["id"] == notification_id for item in notifications)

    mark_response = api_client.post(f"/linters/notifications/{notification_id}/read")
    assert mark_response.status_code == 204

    after_mark = api_client.get("/linters/notifications")
    assert after_mark.status_code == 200
    assert any(item["id"] == notification_id and item["read"] is True for item in after_mark.json())

    unread_response = api_client.get("/linters/notifications", params={"unread_only": "true"})
    assert unread_response.status_code == 200
    assert unread_response.json() == []

    missing_mark = api_client.post("/linters/notifications/9999/read")
    assert missing_mark.status_code == 404
