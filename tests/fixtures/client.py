import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from db import User, engine, session
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
def admin_user():
    with session:
        admin_user = User(
            username="testadmin",
            name="testAdmin",
            password=User.hash_password("testpass"),
        )

        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
