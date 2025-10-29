import asyncio
from pathlib import Path

import pytest
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient

from code_map import ChangeScheduler
from code_map.api.routes import router
from code_map.settings import load_settings, save_settings
from code_map.state import AppState


def write_file(root: Path, relative: str, content: str) -> Path:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    return target


def create_test_app(root: Path) -> tuple[FastAPI, AppState]:
    settings = load_settings(root)
    scheduler = ChangeScheduler()
    state = AppState(settings=settings, scheduler=scheduler)
    save_settings(state.settings)

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
