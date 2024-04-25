import pytest
from fastapi import Response


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 201),
    ("admin", 201),
    ("editor_read_only", 403),
    ("editor_read_write", 201),
    ("editor_read_write_modify", 201),
    ("editor_all", 201),
])
def test_create_meaning(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_meaning_output):
    authorized_user = authorized_client(test_users[user_role])
    
    response: Response = authorized_user.post("/words", json=sample_word_input)
    assert response.status_code == expected_status_code

    response: Response = authorized_user.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == expected_status_code

    if expected_status_code == 201:
        response: Response = authorized_user.get("/words/svarga/meanings/1")
        assert response.json() == sample_meaning_output


def test_get_meanings(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_meaning_output):
    authorized_editor = authorized_client(test_users["editor_all"])
    response: Response = authorized_editor.post("/words", json=sample_word_input)
    assert response.status_code == 201

    for _ in range(5):
        response: Response = authorized_editor.post("/words/svarga/meanings", json=sample_meaning_input)
        assert response.status_code == 201

    response: Response = client.get("/words/svarga/meanings")
    assert response.status_code == 200

    output_list = response.json()
    assert len(output_list) == 5

    for index, meaning in enumerate(output_list):
        output = sample_meaning_output.copy()
        output.update({"id": index+1})
        assert meaning == output


def test_get_meaning(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_meaning_output):
    authorized_editor = authorized_client(test_users["editor_all"])
    response: Response = authorized_editor.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_editor.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = client.get("/words/svarga/meanings/1")
    assert response.status_code == 200

    assert response.json() == sample_meaning_output


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 204),
    ("editor_all", 204),
])
def test_update_meaning(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_meaning_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201
    
    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    updated_meaning = sample_meaning_output.copy()
    updated_meaning.update({"meaning": "updated meaning"})

    response: Response = authorized_user.put("/words/svarga/meanings/1", json=updated_meaning)
    assert response.status_code == expected_status_code
    

@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_meaning(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/meanings/1")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_meanings(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    for _ in range(5):
        response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
        assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/meanings")
    assert response.status_code == expected_status_code

    if response.status_code == 204:
        response: Response = authorized_user.get("/words/svarga/meanings")
        assert response.status_code == 200
        assert len(response.json()) == 0