from fastapi.testclient import TestClient

from app.security import SESSION_COOKIE_NAME

from .support import login_user, register_user


def test_register_me_logout_and_login_flow(client: TestClient) -> None:
    register_response = register_user(client, "writer@example.com")
    assert register_response["user"]["email"] == "writer@example.com"
    assert SESSION_COOKIE_NAME in client.cookies

    me_response = client.get("/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["user"]["email"] == "writer@example.com"

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 204
    assert SESSION_COOKIE_NAME not in client.cookies

    login_response = login_user(client, "writer@example.com")
    assert login_response["user"]["email"] == "writer@example.com"

    me_after_login = client.get("/auth/me")
    assert me_after_login.status_code == 200
    assert me_after_login.json()["user"]["email"] == "writer@example.com"


def test_register_conflict_and_invalid_login(client: TestClient) -> None:
    register_user(client, "writer@example.com")

    conflict_response = client.post(
        "/auth/register",
        json={"email": "writer@example.com", "password": "supersecure123"},
    )
    assert conflict_response.status_code == 409
    assert conflict_response.json()["detail"] == "Email already registered"

    client.post("/auth/logout")
    invalid_login = client.post(
        "/auth/login",
        json={"email": "writer@example.com", "password": "wrongpass123"},
    )
    assert invalid_login.status_code == 401
    assert invalid_login.json()["detail"] == "Invalid credentials"
