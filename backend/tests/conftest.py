from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from .support import cleanup_sqlite_database, create_database_path, create_test_client


@pytest.fixture
def db_path() -> Iterator[Path]:
    path = create_database_path()
    yield path
    cleanup_sqlite_database(path)


@pytest.fixture
def client(db_path: Path) -> Iterator[TestClient]:
    with create_test_client(db_path) as test_client:
        yield test_client


@pytest.fixture
def client_factory() -> Iterator[Callable[..., TestClient]]:
    created_paths: list[Path] = []

    def factory(**kwargs) -> TestClient:
        path = create_database_path()
        created_paths.append(path)
        return create_test_client(path, **kwargs)

    yield factory

    for path in created_paths:
        cleanup_sqlite_database(path)
