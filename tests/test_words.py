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


def test_create_word(authorized_admin, sample_input_data):
    response: Response = authorized_admin.post("/words", json=sample_input_data)
    assert response.status_code == 201


def test_get_words(authorized_admin):
    response: Response = authorized_admin.get("/words")
    assert response.status_code == 200


def test_get_word(authorized_admin, sample_input_data, sample_output_data):
    response: Response = authorized_admin.post("/words", json=sample_input_data)
    assert response.status_code == 201

    response: Response = authorized_admin.get(f"/words/{sample_input_data['sanskrit_word']}")
    assert response.status_code == 200
    
    sample_output_data["meaning_ids"] = []
    assert response.json() == sample_output_data


def test_update_word(authorized_admin, sample_input_data):
    response: Response = authorized_admin.post("/words", json=sample_input_data)
    assert response.status_code == 201

    response: Response = authorized_admin.put(f"/words/{sample_input_data['sanskrit_word']}", json={
        "sanskrit_word": "स्वर्ग",
        "english_transliteration": "svarga",
    })
    
    assert response.status_code == 200