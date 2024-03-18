from fastapi.testclient import TestClient



def test_create_admin(client):
    response = client.post("/admins/", json={
        "email": "admin@gmailcom",
        "first_name": "Admin",
        "last_name": "User",
        "password": "123"
    })

    new_admin = response.json()

    assert new_admin["email"] == "admin@gmailcom"
    assert new_admin["first_name"] == "Admin"
    assert new_admin["last_name"] == "User"