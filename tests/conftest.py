import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_headers() -> dict:
    """
    Authorization headers with the valid configured API token.
    """
    return {"Authorization": f"Bearer {settings.API_AUTH_TOKEN}"}
