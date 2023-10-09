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
            "height": 105,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
        cookies=response.cookies,
    )

    assert response.status_code == 201
    assert response.json() == {"message": "Field created successfully"}
