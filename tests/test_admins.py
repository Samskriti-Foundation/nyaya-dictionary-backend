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

    print(response.json())
    assert response.status_code == 422