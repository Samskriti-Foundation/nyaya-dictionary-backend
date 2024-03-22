def test_get_admins(authorized_client):
    response = authorized_client.get("/admins")
    assert response.status_code == 200


def test_get_admin(authorized_client):
    response = authorized_client.post("/auth/register", json={
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    assert response.status_code == 201

    response = authorized_client.get("/admins/admin@gmail.com")

    assert response.status_code == 200
    assert response.json() == {
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_superuser": False,
    }

def test_create_admin(authorized_client):
    response = authorized_client.post("/auth/register", json={
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    assert response.status_code == 201


def test_create_admin_duplicate_email(authorized_client):
    response = authorized_client.post("/auth/register", json={
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    assert response.status_code == 201

    response = authorized_client.post("/auth/register", json={
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    assert response.status_code == 409


def test_create_admin_invalid_email(authorized_client):
    response = authorized_client.post("/auth/register", json={
        "email": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    assert response.status_code == 422


def test_update_admin(authorized_client):
    response = authorized_client.post("/auth/register", json={
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    assert response.status_code == 201

    response = authorized_client.put("/admins/", json={
        "email": "admin@gmail.com",
        "first_name": "New Admin",
        "last_name": "User",
    })

    assert response.status_code == 200


def test_delete_admin(authorized_client):
    response = authorized_client.post("/auth/register", json={
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    assert response.status_code == 201

    response = authorized_client.delete("/admins/admin@gmail.com")

    assert response.status_code == 204