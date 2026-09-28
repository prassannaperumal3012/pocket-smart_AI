try:
    from fastapi.testclient import TestClient  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover
    import pytest  # type: ignore[import-not-found]

    pytest.skip("fastapi is not installed", allow_module_level=True)

from app.main import app
from app.db import init_db

import os

os.environ["DATABASE_URL"] = (
    "sqlite:///./test_pocketsmart.db"
)

os.environ["GEMINI_API_KEY"] = ""


init_db()

client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_register_login_and_home():

    email = "test@example.com"

    response = client.post(
        "/api/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "password123",
        },
    )

    assert response.status_code in (
        201,
        409,
    )

    response = client.post(
        "/api/login",
        json={
            "email": email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    response = client.post(
        "/api/generate-home",
        json={
            "budget": 50000,

            "rooms": [
                "Living Room"
            ],

            "items": [
                {
                    "name": "sofa",
                    "category": "furniture",
                    "quantity": 1,
                    "notes": "",
                }
            ],

            "style": "modern",

            "city": "Chennai",

            "priorities": (
                "easy maintenance"
            ),
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["budget_total"] == 50000

    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) > 0
