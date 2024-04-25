import pytest
from fastapi import Response


@pytest.fixture
def user_data():
    def _user_data(email: str, role: str, access: str):
        return {
            "email": email,
            "first_name": "Super",
            "last_name": "User",
            "role": role,
            "access": access,
            "password": "123"
        }
    return _user_data


@pytest.mark.parametrize("user_role, expected_status_code_superuser, expected_status_code_admin, expected_status_code_editor", [
    ("superuser", 201, 201, 201),
    ("admin", 403, 403, 201),
    ("editor_all", 403, 403, 403),
])
def test_create_db_manager(authorized_client, test_users, user_role, expected_status_code_superuser, expected_status_code_admin, expected_status_code_editor, user_data):
    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.post("/auth/register", json = user_data(f"testsuperuser@example.com", "SUPERUSER", "ALL"))
    assert response.status_code == expected_status_code_superuser

    response: Response = authorized_user.post("/auth/register", json = user_data(f"testadmin@example.com", "ADMIN", "ALL"))
    assert response.status_code == expected_status_code_admin

    response: Response = authorized_user.post("/auth/register", json = user_data(f"testeditor@example.com", "EDITOR", "ALL"))
    assert response.status_code == expected_status_code_editor


def test_create_db_manager_duplicate(authorized_client, test_users, user_data):
    authorized_superuser = authorized_client(test_users["superuser"])
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testuser@example.com", "SUPERUSER", "ALL"))
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testuser@example.com", "SUPERUSER", "ALL"))
    assert response.status_code == 409


def test_create_db_manager_invalid_email(authorized_client, test_users, user_data):
    authorized_superuser = authorized_client(test_users["superuser"])
    response: Response = authorized_superuser.post("/auth/register", json = user_data("invalidemail", "SUPERUSER", "ALL"))
    assert response.status_code == 422


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 200),
    ("admin", 200),
    ("editor_all", 403),
])
def test_get_db_managers(authorized_client, test_users, user_data, user_role, expected_status_code):
    authorized_superuser = authorized_client(test_users["superuser"])
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testsuperuser@example.com", "SUPERUSER", "ALL"))
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testadmin@example.com", "ADMIN", "ALL"))
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testeditor@example.com", "EDITOR", "ALL"))
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])
    response: Response = authorized_user.get("/db-managers")
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        for manager in response.json():
            assert manager['role'] in ['ADMIN', 'EDITOR', 'SUPERUSER']
    
@pytest.mark.parametrize("user_role, expected_status_code_superuser, expected_status_code_admin, expected_status_code_editor", [
    ("superuser", 200, 200, 200),
    ("admin", 403, 403, 200),
    ("editor_all", 403, 403, 403),
])
def test_get_db_managers_query(authorized_client, test_users, user_data, user_role, expected_status_code_superuser, expected_status_code_admin, expected_status_code_editor):
    authorized_superuser = authorized_client(test_users["superuser"])
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testsuperuser@example.com", "SUPERUSER", "ALL"))
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testadmin@example.com", "ADMIN", "ALL"))
    assert response.status_code == 201
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testeditor@example.com", "EDITOR", "ALL"))
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])
    response: Response = authorized_user.get(f"/db-managers?role=SUPERUSER")
    assert response.status_code == expected_status_code_superuser

    if expected_status_code_superuser == 200:
        for manager in response.json():
            assert manager['role'] == 'SUPERUSER'

    response: Response = authorized_user.get(f"/db-managers?role=ADMIN")
    assert response.status_code == expected_status_code_admin
    if expected_status_code_admin == 200:
        for manager in response.json():
            assert manager['role'] == 'ADMIN'

    response: Response = authorized_user.get(f"/db-managers?role=EDITOR")
    assert response.status_code == expected_status_code_editor
    if expected_status_code_editor == 200:
        for manager in response.json():
            assert manager['role'] == 'EDITOR'


@pytest.mark.parametrize("user_role, expected_status_code_superuser, expected_status_code_admin, expected_status_code_editor", [
    ("superuser", 204, 204, 204),
    ("admin", 403, 403, 204),
    ("editor_all", 403, 403, 403),
])
def test_delete_db_manager(authorized_client, test_users, user_data, user_role, expected_status_code_superuser, expected_status_code_admin, expected_status_code_editor):
    authorized_superuser = authorized_client(test_users["superuser"])
    
    response: Response = authorized_superuser.post("/auth/register", json = user_data("testsuperuser@example.com", "SUPERUSER", "ALL"))
    assert response.status_code == 201

    response: Response = authorized_superuser.post("/auth/register", json = user_data("testadmin@example.com", "ADMIN", "ALL"))
    assert response.status_code == 201

    response: Response = authorized_superuser.post("/auth/register", json = user_data("testeditor@example.com", "EDITOR", "ALL"))
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete(f"/db-managers/testsuperuser@example.com")
    assert response.status_code == expected_status_code_superuser

    response: Response = authorized_user.delete(f"/db-managers/testadmin@example.com")
    assert response.status_code == expected_status_code_admin

    response: Response = authorized_user.delete(f"/db-managers/testeditor@example.com")
    assert response.status_code == expected_status_code_editor