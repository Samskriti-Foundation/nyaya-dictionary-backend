import pytest
from fastapi import Response
from pprint import pprint


@pytest.fixture
def superuser_data():
    return {
        "email": "superusertest@gmail.com",
        "first_name": "Super",
        "last_name": "User",
        "role": "SUPERUSER",
        "access": "ALL",
        "password": "123"
    }

@pytest.fixture
def admin_data():
    return {
        "email": "admintest@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "ADMIN",
        "access": "ALL",
        "password": "123"
    }


@pytest.fixture
def editor_data(access = "READ_ONLY"):
    return {
        "email": "editortest@gmail.com",
        "first_name": "Editor",
        "last_name": "User",
        "role": "EDITOR",
        "access": access,
        "password": "123"
    }


def test_create_superuser_by_superuser(authorized_superuser, superuser_data):
    response: Response = authorized_superuser.post("/auth/register", json = superuser_data)
    assert response.status_code == 201


def test_create_superuser_by_admin(authorized_admin, superuser_data):
    pprint(authorized_admin.__dict__)
    response: Response = authorized_admin.post("/auth/register", json = superuser_data)
    assert response.status_code == 403


def test_create_superuser_by_editor(authorized_editor, superuser_data):
    response: Response = authorized_editor.post("/auth/register", json = superuser_data)
    assert response.status_code == 403


def test_create_admin_by_superuser(authorized_superuser, admin_data):
    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201


def test_create_admin_by_admin(authorized_admin, admin_data):
    response: Response = authorized_admin.post("/auth/register", json = admin_data)
    assert response.status_code == 403


def test_create_admin_by_editor(authorized_editor, admin_data):
    response: Response = authorized_editor.post("/auth/register", json = admin_data)
    assert response.status_code == 403


def test_create_editor_by_superuser(authorized_superuser, editor_data):
    response: Response = authorized_superuser.post("/auth/register", json = editor_data)
    assert response.status_code == 201


def test_create_editor_by_admin(authorized_admin, editor_data):
    response: Response = authorized_admin.post("/auth/register", json = editor_data)
    assert response.status_code == 201


def test_create_editor_by_editor(authorized_editor, editor_data):
    response: Response = authorized_editor.post("/auth/register", json = editor_data)
    assert response.status_code == 403