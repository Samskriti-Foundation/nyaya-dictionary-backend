from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from app.utils.lang import isDevanagariWord

router = APIRouter(
    prefix="/words",
    tags=["Words"],
)

@router.get("/", response_model=List[schemas.WordOut])
def get_words(db: Session = Depends(get_db)):
    """
    Retrieves a list of words from the database and returns them as a list of `schemas.WordOut` objects.

    Parameters:
        db (Session): The database session object.

    Returns:
        List[schemas.WordOut]: A list of `schemas.WordOut` objects representing the retrieved words.
    """
    db_words = db.query(models.SanskritWord).all()

    words = []

    for db_word in db_words:
        word = {}

        word["id"] = db_word.id
        word["sanskrit_word"] = db_word.sanskrit_word
        word["english_word"] = db_word.english_word
        word["etymologies"] = [x.etymology for x in db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).all()]
        word["derivations"] = [x.derivation for x in db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).all()]
        
        translation_query = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).all()
        translations = {}
        for translation in translation_query:
            translations.setdefault(translation.language, []).append(translation.translation)
        word["translations"] = translations
        
        word["nyaya_reference_texts"] = [{
            "source": x.source,
            "description": x.description
        } for x in db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).all()]
        word["synonyms"] = [x.synonym for x in db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).all()]
        word["antonyms"] = [x.antonym for x in db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).all()]

        words.append(word)
        
    return words

@router.get("/{word}", response_model=schemas.WordOut)
def get_word(word: str, db: Session = Depends(get_db)):
    """
    Retrieves information about a word from the database based on the provided word.
    
    Parameters:
        word (str): The word to retrieve information for.
        db (Session, optional): The database session. Defaults to the result of the `get_db` function.
    
    Returns:
        dict: A dictionary containing information about the word, including its ID, Sanskrit word, English word, etymologies, derivations, translations, reference texts, synonyms, and antonyms.
    
    Raises:
        HTTPException: If the word is not found in the database.
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_word == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    word = {}

    word["id"] = db_word.id
    word["sanskrit_word"] = db_word.sanskrit_word
    word["english_word"] = db_word.english_word
    word["etymologies"] = [x.etymology for x in db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).all()]
    word["derivations"] = [x.derivation for x in db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).all()]
    
    translation_query = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).all()
    translations = {}
    for translation in translation_query:
        translations.setdefault(translation.language, []).append(translation.translation)
    word["translations"] = translations
    
    word["nyaya_reference_texts"] = [{
        "source": x.source,
        "description": x.description
    } for x in db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).all()]
    word["synonyms"] = [x.synonym for x in db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).all()]
    word["antonyms"] = [x.antonym for x in db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).all()]
    
    return word

@router.post("/")
def create_word(word: schemas.Word, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Create a new Sanskrit word in the database. Checks if the word already exists, if it's in Devanagari script, and then adds it to the database along with its translations, etymologies, derivations, detailed description, reference Nyaya texts, synonyms, and antonyms. Returns a message confirming the word creation. 
    """
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()

    if db_word:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Word already exists")

    if not isDevanagariWord(word.sanskrit_word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word is not in Devanagari")
    
    new_word = models.SanskritWord(
        sanskrit_word = word.sanskrit_word,
        english_word = transliterate(word.sanskrit_word, sanscript.DEVANAGARI, sanscript.HK),
    )
    db.add(new_word)
    db.flush()

    if word.etymologies:
        etymologies = [models.Etymology(
            sanskrit_word_id = new_word.id,
            etymology = etymology
        ) for etymology in word.etymologies]
        db.add_all(etymologies)

    if word.derivations:
        derivations = [models.Derivation(
            sanskrit_word_id = new_word.id,
            derivation = derivation
        ) for derivation in word.derivations]
        db.add_all(derivations)


    if word.translations:
        translations = [models.Translation(
            sanskrit_word_id=new_word.id,
            language=translation.language,
            translation=tran
        ) for translation in word.translations for tran in translation.translation]
        db.add_all(translations)
    
    
    if word.detailed_description:
        detailed_description = models.Description(
            sanskrit_word_id = new_word.id,
            description = word.detailed_description
        )
        db.add(detailed_description)
    
    
    if word.reference_nyaya_texts:
        references = [models.ReferenceNyayaText(
            sanskrit_word_id = new_word.id,
            source = reference.source,
            description = reference.description
        ) for reference in word.reference_nyaya_texts]
        db.add_all(references)
    
    
    if word.synonyms:
        synonyms = [models.Synonym(
            sanskrit_word_id = new_word.id,
            synonym = synonym
        ) for synonym in word.synonyms]
        db.add_all(synonyms)
    
    
    if word.antonyms:
        antonyms = [models.Antonym(
            sanskrit_word_id = new_word.id,
            antonym = antonym
        ) for antonym in word.antonyms]
        db.add_all(antonyms)
    
    db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Word created"})

@router.put("/")
def update_word(word: schemas.WordUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Updates a word in the database.

    Parameters:
        word (schemas.WordUpdate): The updated word object.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (int, optional): The ID of the current user. Defaults to Depends(oauth2.get_current_user).

    Raises:
        HTTPException: If the word is not in Devanagari, if the word is not found in the database, or if the word ID is invalid.

    Returns:
        JSONResponse: A JSON response with the message "Word updated" and a status code of 200.
    """
    if not isDevanagariWord(word.sanskrit_word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word is not in Devanagari")
    
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word not found")
    
    if word.id != db_word.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid word ID")
    
    db_word.sanskrit_word = word.sanskrit_word
    db_word.english_word = word.english_word

    if word.etymologies:
        db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == word.id).delete()

        etymologies = [models.Etymology(
            sanskrit_word_id = word.id,
            etymology = etymology
        ) for etymology in word.etymologies]
        
        db.add_all(etymologies)

    if word.derivations:
        db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == word.id).delete()

        derivations = [models.Derivation(
            sanskrit_word_id = word.id,
            derivation = derivation
        ) for derivation in word.derivations]
        
        db.add_all(derivations)


    if word.translations:
        db.query(models.Translation).filter(models.Translation.sanskrit_word_id == word.id).delete()

        translations = [models.Translation(
            sanskrit_word_id=word.id,
            language=translation.language,
            translation=tran
        ) for translation in word.translations for tran in translation.translation]
        
        db.add_all(translations)
    
    
    if word.detailed_description:
        db.query(models.Description).filter(models.Description.sanskrit_word_id == word.id).delete()

        detailed_description = models.Description(
            sanskrit_word_id = word.id,
            description = word.detailed_description
        )
        
        db.add(detailed_description)

    if word.reference_nyaya_texts:
        db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == word.id).delete()

        references = [models.ReferenceNyayaText(
            sanskrit_word_id = word.id,
            source = reference.source,
            description = reference.description
        ) for reference in word.reference_nyaya_texts]
        
        db.add_all(references)
    
    
    if word.synonyms:
        db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == word.id).delete()

        synonyms = [models.Synonym(
            sanskrit_word_id = word.id,
            synonym = synonym
        ) for synonym in word.synonyms]
        
        db.add_all(synonyms)
    
    
    if word.antonyms:
        db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == word.id).delete()
        
        antonyms = [models.Antonym(
            sanskrit_word_id = word.id,
            antonym = antonym
        ) for antonym in word.antonyms]
        
        db.add_all(antonyms)

    db.commit()
    db.refresh(db_word)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Word updated"})


@router.delete("/{word}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word(word: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Delete a word from the database along with all associated etymologies, derivations, translations, descriptions, reference nyaya texts, synonyms, antonyms.
    
    Parameters:
    - word: str - the word to be deleted
    - db: Session - database session
    - current_user: int - the current user id
    
    Returns:
    None
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_word == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Description).filter(models.Description.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.SanskritWord).filter(models.SanskritWord.id == db_word.id).delete(synchronize_session=False)

    db.commit()