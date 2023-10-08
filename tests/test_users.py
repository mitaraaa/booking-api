import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("client")
def test_signup(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}


@pytest.mark.usefixtures("client")
def test_signup_duplicate(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 422


@pytest.mark.usefixtures("client")
def test_login(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "testpass"}
    )

    assert response.status_code == 200
    assert response.cookies["session_id"] is not None


@pytest.mark.usefixtures("client")
def test_login_invalid(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "wrongpass"}
    )

    assert response.status_code == 401


@pytest.mark.usefixtures("client")
def test_login_already_logged_in(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "testpass"}
    )

    assert response.status_code == 200
    assert response.cookies["session_id"] is not None

    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "testpass"}
    )

    assert response.status_code == 401


@pytest.mark.usefixtures("client")
def test_logout(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "testpass"}
    )

    assert response.status_code == 200
    assert response.cookies["session_id"] is not None

    response = client.post("/users/logout")

    assert response.status_code == 200
    assert response.cookies.get("session_id") is None


@pytest.mark.usefixtures("client")
def test_logout_unauthorized(client: TestClient):
    response = client.post("/users/logout")

    assert response.status_code == 401


@pytest.mark.usefixtures("client")
def test_logout_invalid_session_id(client: TestClient):
    response = client.post("/users/logout", cookies={"session_id": "invalid"})

    assert response.status_code == 401


@pytest.mark.usefixtures("client")
def test_profile(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "testpass"}
    )

    assert response.status_code == 200
    assert response.cookies["session_id"] is not None

    response = client.get("/users/profile")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "testadmin",
        "name": "testAdmin",
    }


@pytest.mark.usefixtures("client", "admin_user")
def test_get_users(client: TestClient):
    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "testpass"}
    )

    response = client.get("/users", cookies=response.cookies)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "username": "testadmin",
            "name": "testAdmin",
        }
    ]


@pytest.mark.usefixtures("client", "admin_user")
def test_get_user(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testuser",
            "name": "testUser",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/login", json={"username": "testadmin", "password": "testpass"}
    )
    response = client.get("/users/2", cookies=response.cookies)

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "username": "testuser",
        "name": "testUser",
    }


@pytest.mark.usefixtures("client")
def test_update_user(client: TestClient):
    response = client.post(
        "/users/signup",
        json={
            "username": "testuser",
            "name": "testUser",
            "password": "testpass",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/login", json={"username": "testuser", "password": "testpass"}
    )
    response = client.put(
        "/users/profile", json={"name": "testUser2"}, cookies=response.cookies
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "User updated successfully",
        "user": {
            "id": 1,
            "username": "testuser",
            "name": "testUser2",
        },
    }
