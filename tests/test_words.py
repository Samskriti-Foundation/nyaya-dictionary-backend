import pytest

@pytest.fixture
def sample_word_input_data():
    return {
    "sanskrit_word": "स्वर्ग",
    "etymologies": [
        "सुखं गम्यते इति स्वर्गः । सुखलोकः ।",
        "सुष्ठु अर्ज्यते इति स्वर्गः ।",
        "सुष्ठु ऋज्यते स्थीयते अस्मिन्निति स्वर्गः । सुख स्थानम् ।",
        "स्वः इति गीयते इति स्वर्गः ।"
    ],
    "derivations": [
        "3 3 121  इति सूत्रेण घञ् प्रत्यये  7 3 53 , ततः `न्यङ्कादीनां च इत्यनेन",
        "इत्यनेन कर्मणि घञि कृत्वे स्वर्ग इति रूपम् ।",
        "कृत्वे स्वर्गः इति रूपम् ।",
        "सु उपसर्ग पूर्वक `ऋजुगतिस्थानार्जनोपार्जनेषु  इत्यस्माद्धातोः हलश्च",
        "सु पूर्वक `अर्ज अर्जने  इत्यस्माद्धातोः `अकर्तरि च कारके संज्ञायाम्"
    ],
    "translations": [
        {
            "language": "English",
            "translation": ["Paradise"]
        },
        {
            "language": "Kannada",
            "translation": ["ಸ್ವರ್ಗಲೋಕ"]
        },
        {
            "language": "Hindi",
            "translation": ["स्वर्गलोक"]
        }
    ],
    "synonyms": ["स्वर्ग", "स्वर्", "नाक", "त्रिदिव", "त्रिदशालय", "सुरलोक", "द्यो", "दिव्", "त्रिविष्टप", "मन्दर"]
}


@pytest.fixture
def sample_output_word_data():
    return {
    "sanskrit_word": "स्वर्ग",
    "etymologies": [
        "सुखं गम्यते इति स्वर्गः । सुखलोकः ।",
        "सुष्ठु अर्ज्यते इति स्वर्गः ।",
        "सुष्ठु ऋज्यते स्थीयते अस्मिन्निति स्वर्गः । सुख स्थानम् ।",
        "स्वः इति गीयते इति स्वर्गः ।"
    ],
    "derivations": [
        "3 3 121  इति सूत्रेण घञ् प्रत्यये  7 3 53 , ततः `न्यङ्कादीनां च इत्यनेन",
        "इत्यनेन कर्मणि घञि कृत्वे स्वर्ग इति रूपम् ।",
        "कृत्वे स्वर्गः इति रूपम् ।",
        "सु उपसर्ग पूर्वक `ऋजुगतिस्थानार्जनोपार्जनेषु  इत्यस्माद्धातोः हलश्च",
        "सु पूर्वक `अर्ज अर्जने  इत्यस्माद्धातोः `अकर्तरि च कारके संज्ञायाम्"
    ],
    "translations": {
        "English": ["Paradise"],
        "Kannada": ["ಸ್ವರ್ಗಲೋಕ"],
        "Hindi": ["स्वर्गलोक"]
    },
    "detailed_description": None,
    "reference_nyaya_texts": None,
    "synonyms": ["स्वर्ग", "स्वर्", "नाक", "त्रिदिव", "त्रिदशालय", "सुरलोक", "द्यो", "दिव्", "त्रिविष्टप", "मन्दर"],
    "antonyms": [],
    "id": 1,
    "english_word": "svarga"
}

def test_get_words(client):
    response = client.get("/words")
    assert response.status_code == 200


def test_get_word(authorized_client, client, sample_word_input_data, sample_output_word_data):
    response = authorized_client.post("/words", json=sample_word_input_data)

    assert response.status_code == 201

    response = client.get("/words/svarga")

    assert response.status_code == 200

    assert response.json() == sample_output_word_data


def test_create_word(authorized_client, sample_word_input_data):
    response = authorized_client.post("/words", json=sample_word_input_data)
    assert response.status_code == 201


def test_create_word_duplicate(authorized_client, sample_word_input_data):
    response = authorized_client.post("/words", json=sample_word_input_data)
    assert response.status_code == 201

    response = authorized_client.post("/words", json=sample_word_input_data)
    assert response.status_code == 409


def test_create_word_invalid(authorized_client):
    response = authorized_client.post("/words", json={
        "sanskrit_word": "abcde",
    })

    assert response.status_code == 400


def test_update_word(authorized_client, sample_word_input_data):
    response = authorized_client.post("/words", json=sample_word_input_data)
    assert response.status_code == 201

    response = authorized_client.put("/words", json={
        "id": 1,
        "english_word": "svarga",
        "sanskrit_word": "स्वर्ग",
        "etymologies": [
        "सुखं गम्यते इति स्वर्गः । सुखलोकः ।",
        "सुष्ठु अर्ज्यते इति स्वर्गः ।",
        "सुष्ठु ऋज्यते स्थीयते अस्मिन्निति स्वर्गः । सुख स्थानम् ।",
        "स्वः इति गीयते इति स्वर्गः ।"
        ],
        "derivations": [
        "3 3 121  इति सूत्रेण घञ् प्रत्यये  7 3 53 , ततः `न्यङ्कादीनां च इत्यनेन",
        "इत्यनेन कर्मणि घञि कृत्वे स्वर्ग इति रूपम् ।",
        "कृत्वे स्वर्गः इति रूपम् ।",
        "सु उपसर्ग पूर्वक `ऋजुगतिस्थानार्जनोपार्जनेषु  इत्यस्माद्धातोः हलश्च",
        "सु पूर्वक `अर्ज अर्जने  इत्यस्माद्धातोः `अकर्तरि च कारके संज्ञायाम्"
        ],
        "translation": {
            "english_translation": "Paradise",
            "kannada_translation": "ಸ್ವರ್ಗಲೋಕ",
            "hindi_translation": "स्वर्गलोक"
        },
        "synonyms": ["स्वर्ग", "स्वर्", "नाक", "त्रिदिव", "त्रिदशालय"],
        "antonyms": ["test", "test", "test"]
    })

    assert response.status_code == 200


def test_update_word_invalid(authorized_client, sample_word_input_data):
    response = authorized_client.post("/words", json=sample_word_input_data)
    assert response.status_code == 201

    response = authorized_client.put("/words", json={
        "id": 1,
        "english_word": "svarga",
        "sanskrit_word": "स्वर्",
        "etymologies": [
        "सुखं गम्यते इति स्वर्गः । सुखलोकः ।",
        "सुष्ठु अर्ज्यते इति स्वर्गः ।",
        "सुष्ठु ऋज्यते स्थीयते अस्मिन्निति स्वर्गः । सुख स्थानम् ।",
        "स्वः इति गीयते इति स्वर्गः ।"
        ],
        "derivations": [
        "3 3 121  इति सूत्रेण घञ् प्रत्यये  7 3 53 , ततः `न्यङ्कादीनां च इत्यनेन",
        "इत्यनेन कर्मणि घञि कृत्वे स्वर्ग इति रूपम् ।",
        "कृत्वे स्वर्गः इति रूपम् ।",
        "सु उपसर्ग पूर्वक `ऋजुगतिस्थानार्जनोपार्जनेषु  इत्यस्माद्धातोः हलश्च",
        "सु पूर्वक `अर्ज अर्जने  इत्यस्माद्धातोः `अकर्तरि च कारके संज्ञायाम्"
        ],
        "translation": {
            "english_translation": "Paradise",
            "kannada_translation": "ಸ್ವರ್ಗಲೋಕ",
            "hindi_translation": "स्वर्गलोक"
        },
        "synonyms": ["स्वर्ग", "स्वर्", "नाक", "त्रिदिव", "त्रिदशालय"],
        "antonyms": ["test", "test", "test"]
    })

    assert response.status_code == 404


def test_delete_word(authorized_client, sample_word_input_data):
    response = authorized_client.post("/words", json=sample_word_input_data)
    assert response.status_code == 201

    response = authorized_client.delete("/words/svarga")
    assert response.status_code == 204


def test_delete_word_invalid(authorized_client):
    response = authorized_client.post("/words", json={
        "sanskrit_word": "स्वर्ग",
        "etymologies": [
        "सुखं गम्यते इति स्वर्गः । सुखलोकः ।",
        "सुष्ठु अर्ज्यते इति स्वर्गः ।",
        "सुष्ठु ऋज्यते स्थीयते अस्मिन्निति स्वर्गः । सुख स्थानम् ।",
        "स्वः इति गीयते इति स्वर्गः ।"
        ],
        "derivations": [
        "3 3 121  इति सूत्रेण घञ् प्रत्यये  7 3 53 , ततः `न्यङ्कादीनां च इत्यनेन",
        "इत्यनेन कर्मणि घञि कृत्वे स्वर्ग इति रूपम् ।",
        "कृत्वे स्वर्गः इति रूपम् ।",
        "सु उपसर्ग पूर्वक `ऋजुगतिस्थानार्जनोपार्जनेषु  इत्यस्माद्धातोः हलश्च",
        "सु पूर्वक `अर्ज अर्जने  इत्यस्माद्धातोः `अकर्तरि च कारके संज्ञायाम्"
        ],
        "translation": {
            "english_translation": "Paradise",
            "kannada_translation": "ಸ್ವರ್ಗಲೋಕ",
            "hindi_translation": "स्वर्गलोक"
        },
        "synonyms": ["स्वर्ग", "स्वर्", "नाक", "त्रिदिव", "त्रिदशालय", "सुरलोक", "द्यो", "दिव्", "त्रिविष्टप", "मन्दर"]
    })

    assert response.status_code == 201

    response = authorized_client.delete("/words/visarga")
    assert response.status_code == 404