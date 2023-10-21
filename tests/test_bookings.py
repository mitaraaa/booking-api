from datetime import datetime

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_create_booking(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201
    assert response.json() == {
        "booked_until": "2023-10-21T10:00:00",
        "booking_date": "2023-10-21T09:00:00",
        "field_id": 1,
        "id": 1,
        "status": "pending",
        "user_id": 1,
    }


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_create_invalid_booking(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.post(
        "/bookings/",
        json={
            "field_id": 2,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Field not found"}

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Bookng overlaps with another booking"
    }

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 8, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Bookng overlaps with another booking"
    }

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 11, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Bookng overlaps with another booking"
    }


@pytest.mark.usefixtures("client", "dummy_admin", "dummy_owner", "dummy_field")
def test_get_bookings(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testadmin", "password": "testpass"},
    )

    response = client.get(
        "/bookings/",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.get(
        "/bookings/",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "booked_until": "2023-10-21T10:00:00",
            "booking_date": "2023-10-21T09:00:00",
            "field_id": 1,
            "id": 1,
            "status": "pending",
            "user_id": 1,
        }
    ]


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_get_user_bookings(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.get(
        "/bookings/user",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.get(
        "/bookings/user",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "booked_until": "2023-10-21T10:00:00",
            "booking_date": "2023-10-21T09:00:00",
            "field_id": 1,
            "id": 1,
            "status": "pending",
            "user_id": 1,
        }
    ]


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_get_field_bookings(client: TestClient):
    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.get(
        "/bookings/field/1",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/owners/logout",
        cookies=response.cookies,
    )

    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.get(
        "/bookings/field/1",
        cookies=response.cookies,
    )

    assert response.status_code == 403

    response = client.post(
        "users/logout",
        cookies=response.cookies,
    )

    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.get(
        "/bookings/field/1",
        cookies=response.cookies,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "booked_until": "2023-10-21T10:00:00",
            "booking_date": "2023-10-21T09:00:00",
            "field_id": 1,
            "id": 1,
            "status": "pending",
            "user_id": 1,
        }
    ]

    response = client.get(
        "/bookings/field/0",
        cookies=response.cookies,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Field not found"}


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_get_field_availability(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.get(
        "/bookings/field/1/availability/2023-10-21",
    )

    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.get(
        "/bookings/field/1/availability/2023-10-21",
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "from": "09:00:00",
            "to": "10:00:00",
        }
    ]

    response = client.get(
        "/bookings/field/0/availability/2023-10-22",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Field not found"}


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_get_booking(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.get(
        "/bookings/1",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2023, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2023, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.get(
        "/bookings/1",
    )

    assert response.status_code == 200
    assert response.json() == {
        "booked_until": "2023-10-21T10:00:00",
        "booking_date": "2023-10-21T09:00:00",
        "field_id": 1,
        "id": 1,
        "status": "pending",
        "user_id": 1,
    }


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_delete_booking(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.delete(
        "/bookings/1",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2022, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2022, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2022, 10, 21, 11, 0, 0).isoformat(),
            "booked_until": datetime(2022, 10, 21, 12, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.delete(
        "/bookings/1",
    )

    assert response.status_code == 200

    response = client.post(
        "/users/logout",
        cookies=response.cookies,
    )

    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.delete(
        "/bookings/2",
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Booking deleted successfully"}

    response = client.delete(
        "/bookings/1",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


@pytest.mark.usefixtures("client", "dummy_user", "dummy_owner", "dummy_field")
def test_set_booking_status(client: TestClient):
    response = client.post(
        "/users/login",
        json={"username": "testuser", "password": "testpass"},
    )

    response = client.put(
        "/bookings/1",
        json={"status": "accepted"},
    )

    assert response.status_code == 403

    response = client.post(
        "/bookings/",
        json={
            "field_id": 1,
            "booking_date": datetime(2022, 10, 21, 9, 0, 0).isoformat(),
            "booked_until": datetime(2022, 10, 21, 10, 0, 0).isoformat(),
        },
        cookies=response.cookies,
    )

    response = client.post(
        "/users/logout",
        cookies=response.cookies,
    )

    response = client.post(
        "/owners/login",
        json={"username": "testowner", "password": "testpass"},
    )

    response = client.put(
        "/bookings/1",
        json={"status": "confirmed"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "booked_until": "2022-10-21T10:00:00",
        "booking_date": "2022-10-21T09:00:00",
        "field_id": 1,
        "id": 1,
        "status": "confirmed",
        "user_id": 1,
    }

    response = client.put(
        "/bookings/1",
        json={"status": "undefined"},
    )

    assert response.status_code == 422
