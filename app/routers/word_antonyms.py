from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas
from typing import List
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.middleware import auth_middleware, logger_middleware


router = APIRouter(
    prefix="/words",
    tags=["Words - Antonyms"],
)


@router.get("/{word}/{meaning_id}/antonyms", response_model=List[schemas.AntonymOut])
def get_word_antonyms(word: str, meaning_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the antonyms for a given word and meaning ID.
    
    Parameters:
    - word: a string representing the word for which antonyms are to be retrieved
    - meaning_id: an integer representing the meaning ID associated with the word
    - db: a Session dependency used for the database connection
    
    Returns:
    - List of AntonymOut schemas representing the antonyms of the word
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_antonyms = db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id).all()

    return db_antonyms


@router.get("/{word}/{meaning_id}/antonyms/{antonym_id}")
def get_word_anyonym(word: str, meaning_id: int, antonym_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the specific antonym for a given word, meaning ID, and antonym ID.

    Parameters:
    - word: a string representing the word for which the antonym is to be retrieved
    - meaning_id: an integer representing the meaning ID associated with the word
    - antonym_id: an integer representing the specific antonym ID to retrieve
    - db: a Session dependency used for the database connection

    Returns:
    - The specific Antonym model representing the requested antonym
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_antonym = db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id, models.Antonym.id == antonym_id).first()

    if not db_antonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Antonym - {antonym_id} not found")

    return db_antonym

@router.post("/{word}/{meaning_id}/antonyms", status_code=status.HTTP_201_CREATED)
async def create_word_antonym(word: str, meaning_id: int, antonym: schemas.Antonym, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Create a new antonym for a given word and meaning ID. 

    Parameters:
    - word: a string representing the word for which the antonym is to be created
    - meaning_id: an integer representing the meaning ID associated with the word
    - antonym: an object of type schemas.Antonym containing the antonym information
    - db: a Session dependency used for the database connection
    - current_db_manager: an object of type schemas.DBManager representing the current database manager

    Returns:
    - A JSONResponse with status code 201 and a message indicating the successful creation of the antonym
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    new_antonym = models.Antonym(meaning_id=meaning_id, sanskrit_word_id=db_word.id, antonym=antonym.antonym)

    db.add(new_antonym)
    db.commit()
    db.refresh(new_antonym)

    await logger_middleware.log_database_operations("antonyms", new_antonym.id, "CREATE", current_db_manager.email, antonym.antonym)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Successfully created antonym"})


@router.put("/{word}/{meaning_id}/antonyms/{antonym_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word_antonym(word: str, meaning_id: int, antonym_id: int, antonym: schemas.Antonym, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A description of the function that updates a word antonym based on the provided parameters.

    Parameters:
    - word: a string representing the word for which the antonym is to be updated
    - meaning_id: an integer representing the meaning ID associated with the antonym
    - antonym_id: an integer representing the antonym ID to be updated
    - antonym: an object of type schemas.Antonym containing the updated antonym information
    - db: a Session dependency used for the database connection
    - current_db_manager: an object of type schemas.DBManager representing the current database manager

    This function updates the antonym of a word based on the provided IDs and new antonym information.
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_antonym = db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id, models.Antonym.id == antonym_id).first()
    
    if not db_antonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Antonym - {antonym} not found")
    
    db_antonym.antonym = antonym.antonym
    db.commit()
    db.refresh(db_antonym)

    await logger_middleware.log_database_operations("antonyms", antonym_id, "UPDATE", current_db_manager.email, antonym.antonym)


@router.delete("/{word}/{meaning_id}/antonyms/{antonym_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_antonym(word: str, meaning_id: int, antonym_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A description of the function that deletes a word antonym based on the provided parameters.
    
    Parameters:
    - word: a string representing the word for which the antonym is to be deleted
    - meaning_id: an integer representing the meaning ID associated with the antonym
    - antonym_id: an integer representing the antonym ID to be deleted
    - db: a Session dependency used for the database connection
    - current_db_manager: an object of type schemas.DBManager representing the current database manager

    This function deletes the antonym of a word based on the provided IDs.
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    antonym = db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id, models.Antonym.id == antonym_id).first()
    
    if not antonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Antonym - {antonym} not found")
    
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id, models.Antonym.id == antonym_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("antonyms", antonym_id, "DELETE", current_db_manager.email, antonym.antonym)


@router.delete("/{word}/{meaning_id}/antonyms", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_antonyms(word: str, meaning_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function that deletes all antonyms associated with a word based on the provided word and meaning ID.

    Parameters:
        - word: a string representing the word for which the antonyms are to be deleted
        - meaning_id: an integer representing the meaning ID associated with the antonyms
        - db: a Session dependency used for the database connection
        - current_db_manager: an object of type schemas.DBManager representing the current database manager

    This function deletes all antonyms of a word based on the provided IDs and logs the database operation.
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("antonyms", meaning_id, "DELETE_ALL", current_db_manager.email)