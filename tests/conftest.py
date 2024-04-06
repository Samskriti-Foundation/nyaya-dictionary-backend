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
def test_superuser():
    db = TestingSessionLocal()

    superuser = {
        "email": "superuser@gmail.com",
        "first_name": "Super",
        "last_name": "User",
        "role": "SUPERUSER",
        "access": "ALL",
        "password": "123"
    }

    superuser["password"] = encrypt.hash(superuser["password"])
    db_superuser = models.DBManager(**superuser)

    db.add(db_superuser)
    db.commit()
    db.refresh(db_superuser)

    assert db_superuser.email == superuser['email']
    assert db_superuser.first_name == superuser['first_name']
    assert db_superuser.last_name == superuser['last_name']
    assert db_superuser.role == superuser['role']
    assert db_superuser.access == superuser['access']

    return superuser



@pytest.fixture
def test_admin():
    db = TestingSessionLocal()
    
    admin = {
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "ADMIN",
        "access": "ALL",
        "password": "123"
    }

    admin["password"] = encrypt.hash(admin["password"])
    db_admin = models.DBManager(**admin)

    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    assert db_admin.email == admin['email']
    assert db_admin.first_name == admin['first_name']
    assert db_admin.last_name == admin['last_name']
    assert db_admin.role == admin['role']
    assert db_admin.access == admin['access']

    return admin




@pytest.fixture
def test_editor():
    db = TestingSessionLocal()
    
    editor = {
        "email": "editor@gmail.com",
        "first_name": "Editor",
        "last_name": "User",
        "role": "EDITOR",
        "access": "READ_WRITE_MODIFY",
        "password": "123"
    }

    editor["password"] = encrypt.hash(editor["password"])
    db_editor = models.DBManager(**editor)

    db.add(db_editor)
    db.commit()
    db.refresh(db_editor)

    assert db_editor.email == editor['email']
    assert db_editor.first_name == editor['first_name']
    assert db_editor.last_name == editor['last_name']
    assert db_editor.role == editor['role']
    assert db_editor.access == editor['access']

    return editor


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