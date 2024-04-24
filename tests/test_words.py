import pytest
from fastapi import Response


@pytest.fixture
def sample_input_data():
    return {
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarga",
    }


@pytest.fixture
def sample_output_data():
    return {
        "id": 1,
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarga",
    }


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 201),
    ("admin", 201),
    ("editor_read_only", 403),
    ("editor_read_write", 201),
    ("editor_read_write_modify", 201),
    ("editor_all", 201),
])
def test_create_word(authorized_client, sample_input_data, user_role, test_users, expected_status_code):
    authorized_user = authorized_client(test_users[user_role])
    response: Response = authorized_user.post("/words", json=sample_input_data)
    assert response.status_code == expected_status_code


def test_get_words(client):
    response: Response = client.get("/words")
    assert response.status_code == 200


def test_get_word(authorized_client, test_users, client, sample_input_data, sample_output_data):
    authorized_editor = authorized_client(test_users["editor_all"])
    response: Response = authorized_editor.post("/words", json=sample_input_data)
    assert response.status_code == 201

    response: Response = client.get(f"/words/{sample_input_data['sanskrit_word']}")
    assert response.status_code == 200
    
    sample_output_data["meaning_ids"] = []
    assert response.json() == sample_output_data


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 200),
    ("admin", 200),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 200),
    ("editor_all", 200),
])
def test_update_word(authorized_client, user_role, test_users, sample_input_data, expected_status_code):
    authorized_admin = authorized_client(test_users["admin"])
    response: Response = authorized_admin.post("/words", json=sample_input_data)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])
    response: Response = authorized_user.put(f"/words/{sample_input_data['sanskrit_word']}", json={
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarg",
    })
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response: Response = authorized_user.get(f"/words/{sample_input_data['sanskrit_word']}")
        assert response.json()["english_transliteration"] == "svarg"


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_word(authorized_client, user_role, test_users, sample_input_data, expected_status_code):
    authorized_admin = authorized_client(test_users["admin"])
    response: Response = authorized_admin.post("/words", json=sample_input_data)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])
    response: Response = authorized_user.delete(f"/words/{sample_input_data['sanskrit_word']}")
    assert response.status_code == expected_status_code

    if expected_status_code == 204:
        response: Response = authorized_user.get(f"/words/{sample_input_data['sanskrit_word']}")
        assert response.status_code == 404