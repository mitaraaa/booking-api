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


@pytest.mark.usefixtures("client", "dummy_owner", "dummy_admin")
def test_get_owners(client: TestClient):
    response = client.post(
        "/users/login",
        json={
            "username": "testadmin",
            "password": "testpass",
        },
    )

    response = client.get("/owners/", cookies=response.cookies)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "username": "testowner",
            "name": "testOwner",
            "contacts": {
                "email": None,
                "phone_number": None,
                "instagram": None,
            },
        }
    ]


@pytest.mark.usefixtures("client", "dummy_owner", "dummy_admin")
def test_get_owner(client: TestClient):
    response = client.post(
        "/users/login",
        json={
            "username": "testadmin",
            "password": "testpass",
        },
    )

    response = client.get("/owners/1", cookies=response.cookies)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "testowner",
        "name": "testOwner",
        "contacts": {
            "email": None,
            "phone_number": None,
            "instagram": None,
        },
    }


@pytest.mark.usefixtures("client", "dummy_owner", "dummy_admin")
def test_delete_owner(client: TestClient):
    response = client.post(
        "/users/login",
        json={
            "username": "testadmin",
            "password": "testpass",
        },
    )

    response = client.delete("/owners/1", cookies=response.cookies)

    assert response.status_code == 200
    assert response.json() == {"message": "Owner deleted successfully"}


@pytest.mark.usefixtures("client", "dummy_owner")
def test_prevent_logging_twice(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    assert response.status_code == 401


@pytest.mark.usefixtures("client", "dummy_owner")
def test_update_profile(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.put(
        "/owners/profile",
        json={
            "name": "testOwner",
            "email": "test@mail.com",
            "phone_number": "+77777777777",
            "instagram": "@test",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Profile updated successfully",
        "user": {
            "id": 1,
            "username": "testowner",
            "name": "testOwner",
            "contacts": {
                "email": "test@mail.com",
                "phone_number": "+77777777777",
                "instagram": "@test",
            },
        },
    }
