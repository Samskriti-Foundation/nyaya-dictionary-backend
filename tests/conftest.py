from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.main import app

import os
from app.database import get_db
from app.database import Base
from alembic import command

from app.oauth2 import create_access_token
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture
def test_superuser(client):
    super_user = {
        "email": "superuser@gmail.com",
        "first_name": "Super",
        "last_name": "User",
        "password": "123"
    }
    response = client.post("/auth/register/superuser", json=super_user)

    assert response.status_code == 201

    return super_user

@pytest.fixture
def token(test_superuser):
    return create_access_token({"email": test_superuser['email']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client