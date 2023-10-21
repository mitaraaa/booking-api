from datetime import time

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("client", "dummy_owner")
def test_create_field(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    start_time = time(10, 0, 0)
    end_time = time(22, 0, 0)

    response = client.post(
        "/fields/",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201
    assert response.json() == {"message": "Field created successfully"}


@pytest.mark.usefixtures("client", "dummy_owner")
def test_add_unprocessable_field(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    start_time = time(10, 0, 0)
    end_time = time(22, 0, 0)

    response = client.post(
        "/fields/",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": "err",
            "length": 105,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 422


@pytest.mark.usefixtures("client", "dummy_owner")
def test_get_fields(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.post(
        "/fields/",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201

    response = client.get(
        "/fields/",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "owner_id": 1,
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        }
    ]


@pytest.mark.usefixtures("client", "dummy_owner")
def test_get_owner_fields(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.post(
        "/fields/",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201

    response = client.get(
        "/fields/owner",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "owner_id": 1,
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        }
    ]


@pytest.mark.usefixtures("client", "dummy_owner")
def test_update_field(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.post(
        "/fields/",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201

    response = client.put(
        "/fields/1",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Field updated successfully"}

    response = client.put(
        "/fields/2",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 404


@pytest.mark.usefixtures("client", "dummy_owner")
def test_delete_field(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.post(
        "/fields/",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201

    response = client.delete(
        "/fields/1",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Field deleted successfully"}

    response = client.delete(
        "/fields/2",
        cookies=response.cookies,
    )

    assert response.status_code == 404


@pytest.mark.usefixtures("client", "dummy_owner")
def test_get_field(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.post(
        "/fields/",
        json={
            "name": "testField",
            "location": "Astana",
            "surface_type": "grass",
            "width": 68,
            "length": 105,
            "start_time": "10:00:00",
            "end_time": "22:00:00",
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201

    response = client.get(
        "/fields/1",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "owner_id": 1,
        "name": "testField",
        "location": "Astana",
        "surface_type": "grass",
        "width": 68,
        "length": 105,
        "start_time": "10:00:00",
        "end_time": "22:00:00",
    }

    response = client.get(
        "/fields/2",
        cookies=response.cookies,
    )

    assert response.status_code == 404
