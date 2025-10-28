import asyncio
from pathlib import Path

import pytest
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient

from code_map import (
    AppState,
    ChangeScheduler,
    ProjectScanner,
    SnapshotStore,
    SymbolIndex,
)
from code_map.api.routes import router


def write_file(root: Path, relative: str, content: str) -> Path:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    return target


def create_test_app(root: Path) -> tuple[FastAPI, AppState]:
    scanner = ProjectScanner(root)
    index = SymbolIndex(root)
    snapshot_store = SnapshotStore(root)
    scheduler = ChangeScheduler()
    state = AppState(
        root=root,
        scanner=scanner,
        index=index,
        snapshot_store=snapshot_store,
        scheduler=scheduler,
        watcher=None,
    )

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
