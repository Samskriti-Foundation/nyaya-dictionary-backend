from fastapi.testclient import TestClient
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
    def _authorized_client(user):
        def override_get_db():
            try:
                yield session
            finally:
                session.close()
        
        app.dependency_overrides[get_db] = override_get_db
        access_token = create_access_token({"email": user['email'], "role": user['role'], "access": user['access']})
        headers = {"Authorization": f"Bearer {access_token}"}
        return TestClient(app, headers=headers)

    yield _authorized_client


@pytest.fixture
def test_users(test_user):
    return {
        "superuser": test_user("superuser@example.com", "SUPERUSER", "ALL"),
        "admin": test_user("admin@example.com", "ADMIN", "ALL"),
        "editor_read_only": test_user("editor.read.only@example.com", "EDITOR", "READ_ONLY"),
        "editor_read_write": test_user("editor.read.write@example.com", "EDITOR", "READ_WRITE"),
        "editor_read_write_modify": test_user("editor.read.write.modify@example.com", "EDITOR", "READ_WRITE_MODIFY"),
        "editor_all": test_user("editor.all@example.com", "EDITOR", "ALL"),
    }


@pytest.fixture
def sample_word_input():
    return {
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarga",
    }


@pytest.fixture
def sample_word_output():
    return {
        "id": 1,
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarga",
    }


@pytest.fixture
def sample_meaning_input():
    return {
        "meaning": "test"
    }


@pytest.fixture
def sample_meaning_output():
    return {
        "id": 1,
        "sanskrit_word_id": 1,
        "meaning": "test"
    }