import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("client", "dummy_admin")
def test_signup(client: TestClient):
    response = client.post(
        "/users/login",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    response = client.post(
        "/owners/",
        json={
            "username": "testowner",
            "name": "testOwner",
            "password": "testpass",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201
    assert response.json() == {"message": "Owner created successfully"}


@pytest.mark.usefixtures("client", "dummy_admin", "dummy_owner")
def test_signup_duplicate(client: TestClient):
    response = client.post(
        "/users/login",
        json={
            "username": "testadmin",
            "name": "testAdmin",
            "password": "testpass",
        },
    )

    response = client.post(
        "/owners/",
        json={
            "username": "testowner",
            "name": "testOwner",
            "password": "testpass",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 422


@pytest.mark.usefixtures("client", "dummy_owner")
def test_login(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    assert response.status_code == 200


@pytest.mark.usefixtures("client", "dummy_owner")
def test_profile(client: TestClient):
    response = client.post(
        "/owners/login", json={"username": "testowner", "password": "testpass"}
    )
    response = client.get("/owners/profile", cookies=response.cookies)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "testowner",
        "name": "testOwner",
        "contacts": {"email": None, "phone_number": None, "instagram": None},
    }
