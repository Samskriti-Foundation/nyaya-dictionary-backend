import pytest
from fastapi import Response

@pytest.fixture
def sample_derivation_input():
    return {
        "derivation": "कृत्वे स्वर्गः इति रूपम् ।"
    }


@pytest.fixture
def sample_derivation_output():
    return {
        "id": 1,
        "derivation": "कृत्वे स्वर्गः इति रूपम् ।",
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
def test_create_derivations(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_derivation_input, sample_derivation_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.post("/words/svarga/1/derivations", json=sample_derivation_input)
    assert response.status_code == expected_status_code


    if response.status_code == 201:
        response: Response = authorized_user.get("/words/svarga/1/derivations/1")
        assert response.status_code == 200
        assert response.json() == sample_derivation_output


def test_get_derivations(authorized_client, client, test_users, sample_word_input, sample_meaning_input, sample_derivation_input, sample_derivation_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    for _ in range(5):
        response: Response = authorized_admin.post("/words/svarga/1/derivations", json=sample_derivation_input)
        assert response.status_code == 201
    

    response: Response = client.get("/words/svarga/1/derivations")
    assert response.status_code == 200
    output_list = response.json()
    assert len(output_list) == 5

    for index, derivation in enumerate(output_list):
        output = sample_derivation_output.copy()
        output.update({"id": index+1})
        assert derivation == output


def test_get_derivation(authorized_client, client, test_users, sample_word_input, sample_meaning_input, sample_derivation_input, sample_derivation_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/derivations", json=sample_derivation_input)
    assert response.status_code == 201


    response: Response = client.get("/words/svarga/1/derivations/1")
    assert response.status_code == 200
    assert response.json() == sample_derivation_output


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 204),
    ("editor_all", 204),
])
def test_update_derivation(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_derivation_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/derivations", json=sample_derivation_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    updated_derivation = sample_derivation_input.copy()
    updated_derivation.update({"derivation": "सु पूर्वक `अर्ज अर्जने  इत्यस्माद्धातोः `अकर्तरि च कारके संज्ञायाम्"})
    response: Response = authorized_user.put("/words/svarga/1/derivations/1", json=updated_derivation)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_derivation(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_derivation_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/derivations", json=sample_derivation_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/derivations/1")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_all_derivations(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_derivation_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/derivations", json=sample_derivation_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/derivations")
    assert response.status_code == expected_status_code

    if response.status_code == 204:
        response: Response = authorized_user.get("/words/svarga/1/derivations")
        assert response.status_code == 200
        assert response.json() == []