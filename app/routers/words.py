from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas
from typing import List
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.middleware import auth_middleware, logger_middleware


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
        meaning_ids = db.query(models.Meaning.id).filter(models.Meaning.sanskrit_word_id == db_word.id).all()
        words.append({
            "id": db_word.id,
            "sanskrit_word": db_word.sanskrit_word,
            "english_transliteration": db_word.english_transliteration,
            "meaning_ids": [x[0] for x in meaning_ids]
        })
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
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    meaning_ids = db.query(models.Meaning.id).filter(models.Meaning.sanskrit_word_id == db_word.id).all()

    return {
        "id": db_word.id,
        "sanskrit_word": db_word.sanskrit_word,
        "english_transliteration": db_word.english_transliteration,
        "meaning_ids": [x[0] for x in meaning_ids]
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_word(word: schemas.WordCreate, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Creates a new word entry in the database based on the provided WordCreate schema.
    
    Parameters:
        word (schemas.WordCreate): The word information to be added.
        db (Session): The database session.
        current_db_manager (schemas.DBManager): The current database manager.
    
    Returns:
        JSONResponse: A JSON response indicating the success of adding the word.
    
    Raises:
        HTTPException: Depending on the authorization level, if the word already exists, or if there are validation errors.
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if word.sanskrit_word == "" or not word.sanskrit_word:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"sanskrit_word cannot be empty")
    
    if not isDevanagariWord(word.sanskrit_word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"sanskrit_word must be in Devanagari")

    if isDevanagariWord(word.sanskrit_word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word.english_transliteration).first()
    
    if db_word:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Word - {word.sanskrit_word} already exists")

    if not word.english_transliteration or word.english_transliteration == "":
        word.english_transliteration = transliterate(word.sanskrit_word, sanscript.DEVANAGARI, sanscript.IAST)

    new_word = models.SanskritWord(**word.model_dump())
    db.add(new_word)
    db.commit()
    db.refresh(new_word)

    await logger_middleware.log_database_operations(table_name="sanskrit_words", record_id=new_word.id, operation="CREATE", db_manager_email=current_db_manager.email, new_value=f"{new_word.sanskrit_word} - {new_word.english_transliteration}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Word added successfully"})


@router.put("/{word}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word(word: str, wordIn: schemas.WordUpdate, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Updates a word entry in the database based on the provided word information.
    
    Parameters:
    - word: str - The word to be updated.
    - wordIn: schemas.WordUpdate - The updated word information.
    - db: Session - The database session.
    - current_db_manager: schemas.DBManager - The current database manager.

    Raises:
    - HTTPException: 403 FORBIDDEN if not authorized, 404 NOT FOUND if the word is not found, 409 CONFLICT if word already exists or English transliteration already exists.

    Returns:
    - No explicit return, updates the database entry.
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(wordIn.sanskrit_word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {wordIn.sanskrit_word} not found")
    
    if wordIn.sanskrit_word != word and db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == wordIn.sanskrit_word).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Word - {wordIn.sanskrit_word} already exists")
    
    if wordIn.english_transliteration != db_word.english_transliteration and db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == wordIn.english_transliteration).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"English Transliteration - {wordIn.english_transliteration} already exists")
    
    if not wordIn.english_transliteration or wordIn.english_transliteration == "":
        wordIn.english_transliteration = transliterate(wordIn.sanskrit_word, sanscript.DEVANAGARI, sanscript.IAST)
    
    db_word.sanskrit_word = wordIn.sanskrit_word
    db_word.english_transliteration = wordIn.english_transliteration
    
    db.commit()
    db.refresh(db_word)
    
    await logger_middleware.log_database_operations(table_name="sanskrit_words", record_id=db_word.id, operation="UPDATE", db_manager_email=current_db_manager.email, new_value=f"{db_word.sanskrit_word} - {db_word.english_transliteration}")

@router.delete("/{word}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word(word: str, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Delete a word from the database along with its associated meanings, etymologies, derivations, translations, reference Nyaya texts, examples, synonyms, antonyms. 
    Parameters:
        - word: str
        - db: Session = Depends(get_db)
        - current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)
    Returns:
        - None
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    word_id = db_word.id

    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Example).filter(models.Example.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.SanskritWord).filter(models.SanskritWord.id == db_word.id).delete(synchronize_session=False)

    db.commit()

    await logger_middleware.log_database_operations(table_name="sanskrit_words", record_id=word_id, operation="DELETE", db_manager_email=current_db_manager.email, new_value=word)
