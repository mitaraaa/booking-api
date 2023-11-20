from datetime import time

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from db import FootballField, Owner, User, engine, session
from main import app


@pytest.fixture()
def client() -> TestClient:
    """
    This fixture is used to create a test client that will be used to make
    requests to the API. The client is created once per test function.
    """
    client = TestClient(app)

    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)

    return client


@pytest.fixture()
def dummy_admin():
    with session:
        admin_user = User(
            username="testadmin",
            name="testAdmin",
            password=User.hash_password("testpass"),
        )

        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)


@pytest.fixture()
def dummy_owner():
    with session:
        owner_user = Owner(
            username="testowner",
            name="testOwner",
            password=User.hash_password("testpass"),
        )

        session.add(owner_user)
        session.commit()
        session.refresh(owner_user)


@pytest.fixture()
def dummy_user():
    with session:
        user = User(
            username="testuser",
            name="testUser",
            password=User.hash_password("testpass"),
        )

        session.add(user)
        session.commit()
        session.refresh(user)


@pytest.fixture()
def dummy_field():
    with session:
        field = FootballField(
            name="testField",
            owner_id=1,
            location="Astana",
            surface_type="grass",
            price=2600,
            width=68,
            length=105,
            start_time=time(10, 0, 0),
            end_time=time(22, 0, 0),
        )

        session.add(field)
        session.commit()
        session.refresh(field)
