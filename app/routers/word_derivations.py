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
    tags=["Word - Derivations"],
)


@router.get("/{word}/{meaning_id}/derivations", response_model=List[schemas.DerivationOut])
def get_word_derivations(word: str, meaning_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the derivations of a word based on the provided word and meaning ID.
    
    Parameters:
    - word: a string representing the word to get derivations for
    - meaning_id: an integer representing the meaning ID
    - db: a SQLAlchemy Session dependency
    
    Returns:
    - List of DerivationOut objects representing the derivations of the word
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_derivations = db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id).all()

    return db_derivations


@router.get("/{word}/{meaning_id}/derivations/{derivation_id}", response_model=schemas.DerivationOut)
def get_word_derivation(word: str, meaning_id: int, derivation_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific derivation of a word based on the provided word, meaning ID, and derivation ID.

    Parameters:
    - word: a string representing the word to get the derivation for
    - meaning_id: an integer representing the meaning ID
    - derivation_id: an integer representing the derivation ID
    - db: a SQLAlchemy Session dependency

    Returns:
    - DerivationOut object representing the specific derivation of the word
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_derivation = db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id, models.Derivation.id == derivation_id).first()

    if not db_derivation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Derivation - {derivation_id} not found")
    
    return db_derivation


@router.post("/{word}/{meaning_id}/derivations")
async def create_word_derivation(word: str, meaning_id: int, derivation: schemas.Derivation, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to create a new derivation for a given word and meaning ID.
    
    Parameters:
    - word: a string representing the word for which the derivation is being created
    - meaning_id: an integer representing the meaning ID of the word
    - derivation: an object of type schemas.Derivation containing the derivation information
    - db: a SQLAlchemy Session dependency for the database operations
    - current_user: an object of type schemas.DBManager representing the current user
    
    Returns:
    - A JSONResponse with status code 201 if the derivation is successfully created
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_derivation = models.Derivation(sanskrit_word_id=db_word.id, meaning_id=meaning_id, derivation=derivation.derivation)

    db.add(db_derivation)
    db.commit()
    db.refresh(db_derivation)

    await logger_middleware.log_database_operations("derivations", db_derivation.id, "CREATE", current_user.email, db_derivation.derivation)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Derivation added successfully"})


@router.put("/{word}/{meaning_id}/derivations/{derivation_id}")
async def update_word_derivation(word: str, meaning_id: int, derivation_id: int, derivation: schemas.Derivation, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to update a word derivation based on the provided word, meaning ID, and derivation ID.
    
    Parameters:
    - word: a string representing the word for which the derivation is being updated
    - meaning_id: an integer representing the meaning ID of the word
    - derivation_id: an integer representing the ID of the derivation to be updated
    - derivation: an object of type schemas.Derivation containing the updated derivation information
    - db: a SQLAlchemy Session dependency for the database operations
    - current_user: an object of type schemas.DBManager representing the current user
    
    Returns:
    - A JSONResponse with status code 204 if the derivation is successfully updated
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    updated_derivation = db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id, models.Derivation.id == derivation_id).first()
    updated_derivation.derivation = derivation.derivation
    
    db.commit()

    await logger_middleware.log_database_operations("derivations", derivation_id, "UPDATE", current_user.email, derivation.derivation)

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Derivation updated successfully"})


@router.delete("/{word}/{meaning_id}/derivations", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_derivations(word: str, meaning_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Deletes all derivations of a word based on the given word and meaning_id.
    
    Parameters:
        word (str): The word to delete derivations for.
        meaning_id (int): The meaning ID of the word.
        db (Session): The database session.
        current_user (schemas.DBManager): The current user accessing the database.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("derivations", meaning_id, "DELETE_ALL", current_user.email)


@router.delete("/{word}/{meaning_id}/derivations/{derivation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_derivation(word: str, meaning_id: int, derivation_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to delete a specific word derivation based on the provided word, meaning ID, and derivation ID.
    
    Parameters:
    - word: a string representing the word for which the derivation is being deleted
    - meaning_id: an integer representing the meaning ID of the word
    - derivation_id: an integer representing the ID of the derivation to be deleted
    - db: a SQLAlchemy Session dependency for the database operations
    - current_user: an object of type schemas.DBManager representing the current user
    
    Raises:
    - HTTPException: If the user is not authorized or if the word or derivation is not found
    
    Returns:
    - None
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_derivation = db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id, models.Derivation.id == derivation_id).first()

    if not db_derivation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Derivation - {derivation_id} not found")
    
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id, models.Derivation.id == derivation_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("derivations", derivation_id, "DELETE", current_user.email, db_derivation.derivation)
