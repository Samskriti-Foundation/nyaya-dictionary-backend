import pytest
from fastapi import Response


@pytest.fixture
def sample_synonym_input():
    return {
        "synonym": "त्रिदिव"
    }


@pytest.fixture
def sample_synonym_output():
    return {
        "id": 1,
        "synonym": "त्रिदिव",
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
def test_create_synonyms(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_synonym_input, sample_synonym_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.post("/words/svarga/1/synonyms", json=sample_synonym_input)
    assert response.status_code == expected_status_code

    if response.status_code == 201:
        response: Response = authorized_user.get("/words/svarga/1/synonyms/1")
        assert response.status_code == 200
        assert response.json() == sample_synonym_output


def test_get_synonyms(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_synonym_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    for _ in range(5):
        response: Response = authorized_admin.post("/words/svarga/1/synonyms", json=sample_synonym_input)
        assert response.status_code == 201
    
    response: Response = client.get("/words/svarga/1/synonyms")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_synonym(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_synonym_input, sample_synonym_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/synonyms", json=sample_synonym_input)
    assert response.status_code == 201

    response: Response = client.get("/words/svarga/1/synonyms/1")
    assert response.status_code == 200
    assert response.json() == sample_synonym_output



@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 204),
    ("editor_all", 204),
])
def test_update_synonym(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_synonym_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)

    response: Response = authorized_admin.post("/words/svarga/1/synonyms", json=sample_synonym_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    updated_synonym = sample_synonym_input.copy()
    updated_synonym.update({"synonym": "सुरलोक"})
    response: Response = authorized_user.put("/words/svarga/1/synonyms/1", json=updated_synonym)
    assert response.status_code == expected_status_code

@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_synonym(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_synonym_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/synonyms", json=sample_synonym_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/synonyms/1")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_synonyms(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_synonym_input, sample_synonym_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/synonyms", json=sample_synonym_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/synonyms")
    assert response.status_code == expected_status_code

    if response.status_code == 204:
        response: Response = authorized_user.get("/words/svarga/1/synonyms")
        assert response.status_code == 200
        assert len(response.json()) == 0
