import pytest
from fastapi import Response

def test_get_word_meanings(client):
    response: Response = client.get("/words/svarga/meanings")
    assert response.status_code == 200

    for meaning in response.json():
        assert meaning['sanskrit_word_id'] == 1

def test_get_word_meaning(authorized_admin):
    response: Response = authorized_admin.post("/words/svarga/meanings/1")

    assert response.status_code == 200
    assert response.json()['id'] == 1


def test_create_word_meaning(authorized_admin):
    response: Response = authorized_admin.post("/words/svarga/meanings", json={"meaning": "test"})
    assert response.status_code == 201