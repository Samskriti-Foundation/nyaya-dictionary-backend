def test_get_words(client):
    response = client.get("/words")
    assert response.status_code == 200


def test_create_word(authorized_client):
    response = authorized_client.post("/words", json={
        "technicalTermDevanagiri": "test",
        "technicalTermRoman": "test",
        "etymology": "test",
        "derivation": "test",
        "source": "test",
        "description": "test",
        "translation": "test",
        "detailedDescription": "test"
    })

    assert response.status_code == 201

def test_get_word(authorized_client, client):
    response = authorized_client.post("/words", json={
        "technicalTermDevanagiri": "test",
        "technicalTermRoman": "test",
        "etymology": "test",
        "derivation": "test",
        "source": "test",
        "description": "test",
        "translation": "test",
        "detailedDescription": "test"
    })

    assert response.status_code == 201

    response = client.get("/words/test")
    assert response.status_code == 200
    