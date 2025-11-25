import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def docs_path(project_root: Path) -> Path:
    return project_root / "documents.txt"


@pytest.fixture(scope="session")
def entities_schema_path(project_root: Path) -> Path:
    return project_root / "entities.json"


@pytest.fixture(scope="session")
def relations_schema_path(project_root: Path) -> Path:
    return project_root / "relations.json"
