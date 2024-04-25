import pytest
from fastapi import Response


@pytest.fixture
def sample_example_input():
    return {
        "example_sentence": "Some example sentence",
        "applicable_modern_context": "some context"
    }


@pytest.fixture
def sample_example_output():
    return {
        "id": 1,
        "example_sentence": "Some example sentence",
        "applicable_modern_context": "some context",
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
def test_create_example(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_example_input, sample_example_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.post("/words/svarga/1/examples", json=sample_example_input)
    assert response.status_code == expected_status_code

    if response.status_code == 201:
        response: Response = authorized_user.get("/words/svarga/1/examples/1")
        assert response.status_code == 200
        assert response.json() == sample_example_output


def test_get_examples(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_example_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    
    for _ in range(5):
        response: Response = authorized_admin.post("/words/svarga/1/examples", json=sample_example_input)
        assert response.status_code == 201

    response: Response = authorized_admin.get("/words/svarga/1/examples")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_example(authorized_client, test_users, client, sample_word_input, sample_meaning_input, sample_example_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/examples", json=sample_example_input)
    assert response.status_code == 201

    response: Response = authorized_admin.get("/words/svarga/1/examples/1")
    assert response.status_code == 200


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 204),
    ("editor_all", 204),
])
def test_update_example(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_example_input, sample_example_output):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/examples", json=sample_example_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    updated_example = sample_example_output.copy()
    updated_example.update({"example_sentence": "Updated example sentence", "applicable_modern_context": "updated context"})
    response: Response = authorized_user.put("/words/svarga/1/examples/1", json=updated_example)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_example(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_example_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/examples", json=sample_example_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/examples/1")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("user_role, expected_status_code", [
    ("superuser", 204),
    ("admin", 204),
    ("editor_read_only", 403),
    ("editor_read_write", 403),
    ("editor_read_write_modify", 403),
    ("editor_all", 204),
])
def test_delete_examples(authorized_client, test_users, user_role, expected_status_code, sample_word_input, sample_meaning_input, sample_example_input):
    authorized_admin = authorized_client(test_users["admin"])
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/1/examples", json=sample_example_input)
    assert response.status_code == 201

    authorized_user = authorized_client(test_users[user_role])

    response: Response = authorized_user.delete("/words/svarga/1/examples")
    assert response.status_code == expected_status_code

    if response.status_code == 204:
        response: Response = authorized_user.get("/words/svarga/1/examples")
        assert response.status_code == 200
        assert len(response.json()) == 0