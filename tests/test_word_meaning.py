import pytest
from fastapi import Response


@pytest.fixture
def sample_word_input():
    return {
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarga",
    }


@pytest.fixture
def sample_word_output():
    return {
        "id": 1,
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarga",
    }


@pytest.fixture
def sample_meaning_input():
    return {
        "meaning": "test"
    }


@pytest.fixture
def sample_meaning_output():
    return {
        "id": 1,
        "sanskrit_word_id": 1,
        "meaning": "test"
    }



def test_create_meaning(authorized_client, test_admin, sample_word_input, sample_meaning_input, sample_meaning_output):
    authorized_admin = authorized_client(test_admin)
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_admin.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 201

    response: Response = authorized_admin.get("/words/svarga/meanings/1")
    assert response.json() == sample_meaning_output


def test_create_meaning_invalid_access(authorized_client, test_admin, test_editor_read_only, sample_word_input, sample_meaning_input):
    authorized_admin = authorized_client(test_admin)
    authorized_editor = authorized_client(test_editor_read_only)
    
    response: Response = authorized_admin.post("/words", json=sample_word_input)
    assert response.status_code == 201

    response: Response = authorized_editor.post("/words/svarga/meanings", json=sample_meaning_input)
    assert response.status_code == 403