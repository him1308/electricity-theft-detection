from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import seed_default_users
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        seed_default_users(db)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def auth_headers(client: TestClient, username: str = "admin", password: str = "admin123") -> dict[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})

    assert response.status_code == 401


def test_dashboard_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/dashboard/summary")

    assert response.status_code == 401


def test_admin_can_access_admin_endpoint(client: TestClient) -> None:
    response = client.get("/api/admin/users", headers=auth_headers(client))

    assert response.status_code == 200
    assert {user["role"] for user in response.json()} == {"Admin", "Analyst"}


def test_analyst_cannot_access_admin_endpoint(client: TestClient) -> None:
    response = client.get("/api/admin/users", headers=auth_headers(client, "analyst", "analyst123"))

    assert response.status_code == 403


def test_admin_endpoint_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/admin/users")

    assert response.status_code == 401


def test_analyst_can_access_analyst_dashboard(client: TestClient) -> None:
    response = client.get("/api/dashboard/analyst", headers=auth_headers(client, "analyst", "analyst123"))

    assert response.status_code == 200
    assert "pending_investigations" in response.json()


def test_admin_can_access_analyst_dashboard(client: TestClient) -> None:
    response = client.get("/api/dashboard/analyst", headers=auth_headers(client))

    assert response.status_code == 200
    assert "recent_suspicious_consumers" in response.json()


def test_admin_can_change_user_role(client: TestClient) -> None:
    headers = auth_headers(client)
    users = client.get("/api/admin/users", headers=headers).json()
    analyst = next(user for user in users if user["username"] == "analyst")

    promote = client.patch(f"/api/admin/users/{analyst['id']}/role", json={"role": "Admin"}, headers=headers)
    assert promote.status_code == 200
    assert promote.json()["role"] == "Admin"

    demote = client.patch(f"/api/admin/users/{analyst['id']}/role", json={"role": "Analyst"}, headers=headers)
    assert demote.status_code == 200
    assert demote.json()["role"] == "Analyst"


def test_authenticated_model_status(client: TestClient) -> None:
    response = client.get("/api/model/status", headers=auth_headers(client))

    assert response.status_code == 200
    body = response.json()
    assert "is_trained" in body
    assert "model_path" in body


def test_cors_allows_vite_fallback_port(client: TestClient) -> None:
    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://127.0.0.1:5174",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5174"
