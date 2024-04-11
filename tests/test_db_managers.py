import pytest
from fastapi import Response


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


def test_create_superuser_by_superuser(authorized_client, test_superuser, superuser_data):
    authorized_superuser = authorized_client(test_superuser)
    response: Response = authorized_superuser.post("/auth/register", json = superuser_data)
    assert response.status_code == 201


def test_create_superuser_by_admin(authorized_client, test_admin, superuser_data):
    authorized_admin = authorized_client(test_admin)
    response: Response = authorized_admin.post("/auth/register", json = superuser_data)
    assert response.status_code == 403


def test_create_superuser_by_editor(authorized_client, test_editor_read_write, superuser_data):
    authorized_editor = authorized_client(test_editor_read_write)
    response: Response = authorized_editor.post("/auth/register", json = superuser_data)
    assert response.status_code == 403


def test_create_admin_by_superuser(authorized_client, test_superuser, admin_data):
    authorized_superuser = authorized_client(test_superuser)
    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201


def test_create_admin_by_admin(authorized_client, test_admin, admin_data):
    authorized_admin = authorized_client(test_admin)
    response: Response = authorized_admin.post("/auth/register", json = admin_data)
    assert response.status_code == 403


def test_create_admin_by_editor(authorized_client, test_editor_read_write, admin_data):
    authorized_editor = authorized_client(test_editor_read_write)
    response: Response = authorized_editor.post("/auth/register", json = admin_data)
    assert response.status_code == 403


def test_create_editor_by_superuser(authorized_client, test_superuser, editor_data):
    authorized_superuser = authorized_client(test_superuser)
    response: Response = authorized_superuser.post("/auth/register", json = editor_data)
    assert response.status_code == 201


def test_create_editor_by_admin(authorized_client, test_admin, editor_data):
    authorized_admin = authorized_client(test_admin)
    response: Response = authorized_admin.post("/auth/register", json = editor_data)
    assert response.status_code == 201


def test_create_editor_by_editor(authorized_client, test_editor_read_write, editor_data):
    authorized_editor = authorized_client(test_editor_read_write)
    response: Response = authorized_editor.post("/auth/register", json = editor_data)
    assert response.status_code == 403


def test_create_db_manager_duplicate(authorized_client, test_superuser, admin_data):
    authorized_superuser = authorized_client(test_superuser)
    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 409


def test_create_db_manager_invalid_email(authorized_client, test_superuser, admin_data):
    authorized_superuser = authorized_client(test_superuser)
    
    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201

    invalid_data = admin_data.update({"email": "invalidemail"})

    response: Response = authorized_superuser.post("/auth/register", json = invalid_data)
    assert response.status_code == 422

def test_get_db_managers_by_superuser(authorized_client, test_superuser, admin_data, editor_data, superuser_data):
    authorized_superuser = authorized_client(test_superuser)
    
    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = editor_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = superuser_data)
    assert response.status_code == 201

    response: Response = authorized_superuser.get("/db-managers")
    assert response.status_code == 200

    for manager in response.json():
        assert manager['role'] in ['ADMIN', 'EDITOR', 'SUPERUSER']
    

def test_get_db_managers_by_admin(authorized_client, test_superuser, test_admin, admin_data, editor_data, superuser_data):
    authorized_superuser = authorized_client(test_superuser)
    authorized_admin = authorized_client(test_admin)

    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = editor_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = superuser_data)
    assert response.status_code == 201

    response: Response = authorized_admin.get("/db-managers")
    
    assert response.status_code == 200

    for manager in response.json():
        assert manager['role'] == 'EDITOR'
    

def test_get_db_managers_by_editor(authorized_client, test_superuser, test_editor_read_write, admin_data, editor_data, superuser_data):
    authorized_superuser = authorized_client(test_superuser)
    authorized_editor = authorized_client(test_editor_read_write)

    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = editor_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = superuser_data)
    assert response.status_code == 201

    response: Response = authorized_editor.get("/db-managers")
    assert response.status_code == 403


def test_get_db_managers_query_by_superuser(authorized_client, test_superuser, admin_data, editor_data, superuser_data):
    authorized_superuser = authorized_client(test_superuser)
    
    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = editor_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = superuser_data)
    assert response.status_code == 201

    
    for role in ['ADMIN', 'EDITOR', 'SUPERUSER']:
        response: Response = authorized_superuser.get(f"/db-managers?role={role}")
        assert response.status_code == 200

        for manager in response.json():
            assert manager['role'] == role


def test_get_db_managers_query_by_admin(authorized_client, test_superuser, test_admin, admin_data, editor_data, superuser_data):
    authorized_superuser = authorized_client(test_superuser)
    authorized_admin = authorized_client(test_admin)

    response: Response = authorized_superuser.post("/auth/register", json = admin_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = editor_data)
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = superuser_data)
    assert response.status_code == 201

    
    for role in ['ADMIN', 'EDITOR', 'SUPERUSER']:
        response: Response = authorized_admin.get(f"/db-managers?role={role}")
        
        if role == 'SUPERUSER' or role == 'ADMIN':
            assert response.status_code == 403
            return

        assert response.status_code == 200

        for manager in response.json():
            assert manager['role'] == 'EDITOR'