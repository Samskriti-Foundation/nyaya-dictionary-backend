from fastapi.testclient import TestClient
from fastapi import Response
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models
from app.utils import encrypt


SQLALCHEMY_DATABASE_URL = settings.test_database_url

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

@pytest.fixture
def test_user():
    def _create_user(email, role, access):
        db = TestingSessionLocal()

        user = {
            "email": email,
            "first_name": "First",
            "last_name": "Last",
            "role": role,
            "access": access,
            "password": "123"
        }
        user["password"] = encrypt.hash(user["password"])
        db_user = models.DBManager(**user)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        assert db_user.email == user['email']
        assert db_user.first_name == user['first_name']
        assert db_user.last_name == user['last_name']
        assert db_user.role == user['role']
        assert db_user.access == user['access']

        return user

    return _create_user


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture()
def authorized_client(session):
    def _authorized_client(db_manager):
        def override_get_db():
            try:
                yield session
            finally:
                session.close()
        
        app.dependency_overrides[get_db] = override_get_db
        access_token = create_access_token({"email": db_manager['email']})
        headers = {"Authorization": f"Bearer {access_token}"}
        return TestClient(app, headers=headers)

    yield _authorized_client


@pytest.fixture
def test_superuser(test_user):
    return test_user("superuser@gmail.com", "SUPERUSER", "ALL")


@pytest.fixture
def test_admin(test_user):
    return test_user("admin@example.com", "ADMIN", "ALL")


@pytest.fixture
def test_editor_read_write(test_user):
    return test_user("editor_read_write@gmail.com", "EDITOR", "READ_WRITE")


@pytest.fixture
def test_editor_read_write_modify(test_user):
    return test_user("editor_read_write_modify@gmail.com", "EDITOR", "READ_WRITE_MODIFY")


@pytest.fixture
def authorized_admin(authorized_client, test_admin):
    return authorized_client(test_admin)