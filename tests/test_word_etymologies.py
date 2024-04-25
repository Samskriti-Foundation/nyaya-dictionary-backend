import pytest
from fastapi import Response


@pytest.fixture
def sample_etymology_input():
    return {
        "etymology": "सुष्ठु अर्ज्यते इति स्वर्गः ।"
    }


@pytest.fixture
def sample_etymology_output():
    return {
        "id": 1,
        "etymology": "सुष्ठु अर्ज्यते इति स्वर्गः ।",
        "meaning_id": 1,
        "sanskrit_word_id": 1
    }

@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 201),
    ("admin", 201),
    ("editor_read_only", 403),
    ("editor_read_write", 201),
    ("editor_read_write_modify", 201),
    ("editor_all", 201),
])
def test_create_etymology(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_etymology_input, sample_etymology_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.post("/words/svarga/1/etymologies", json=sample_etymology_input)
    assert response.status_code == expected_status_code


    if response.status_code == 201:
        response: Response = authorized_user.get("/words/svarga/1/etymologies/1")
        assert response.status_code == 200
        assert response.json() == sample_etymology_output


def test_get_etymologies(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_etymology_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/etymologies", json=sample_etymology_input)
    assert response.status_code == 201

    response: Response = client.get("/words/svarga/1/etymologies")
    assert response.status_code == 200



def test_get_etymology(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_etymology_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/etymologies", json=sample_etymology_input)


    response: Response = client.get("/words/svarga/1/etymologies/1")
    assert response.status_code == 200

@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 204),
    ("editor_all", 204),
])
def test_update_etymology(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_etymology_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/etymologies", json=sample_etymology_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    updated_etymology = sample_etymology_input.copy()
    updated_etymology.update({"etymology": "सुष्ठु ऋज्यते स्थीयते अस्मिन्निति स्वर्गः । सुख स्थानम् ।"})
    response: Response = authorized_user.put("/words/svarga/1/etymologies/1", json=updated_etymology)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_etymology(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_etymology_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/etymologies", json=sample_etymology_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/etymologies/1")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_etymologies(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_etymology_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/etymologies", json=sample_etymology_input)


    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/etymologies")
    assert response.status_code == expected_status_code

    
    if expected_status_code == 204:
        response: Response = authorized_user.get("/words/svarga/1/etymologies")
        assert response.status_code == 200  