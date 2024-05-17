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
    tags=["Word - Meanings"],
)


@router.get("/{word}/meanings", response_model=List[schemas.MeaningOut])
def get_word_meanings(word: str, db: Session = Depends(get_db)):
    """
    Retrieves the meanings of a given word. 
    
    Parameters:
        - word (str): The word for which meanings are to be retrieved.
        - db (Session): The database session dependency.
    
    Returns:
        - List[schemas.MeaningOut]: A list of meanings associated with the input word.
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_meanings = db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id).all()

    return db_meanings


@router.get("/{word}/meanings/{meaning_id}", response_model=schemas.MeaningOut)
def get_word_meaning(word: str, meaning_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the meaning of a given word with a specific meaning ID.

    Parameters:
        - word (str): The word for which the meaning is to be retrieved.
        - meaning_id (int): The ID of the meaning to retrieve.
        - db (Session): The database session dependency.

    Returns:
        - schemas.MeaningOut: The meaning associated with the input word and meaning ID.
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_meaning = db.query(models.Meaning).filter(models.Meaning.id == meaning_id).first()

    if not db_meaning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meaning - {meaning_id} not found")  

    return db_meaning


@router.post("/{word}/meanings", status_code=status.HTTP_201_CREATED)
async def create_word_meaning(word: str, meaning: schemas.MeaningCreate, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Creates a new meaning for a word in the database.

    Parameters:
        - word (str): The word for which the meaning is to be created.
        - meaning (schemas.MeaningCreate): The meaning to be created for the word.
        - db (Session): The database session dependency.
        - current_user (schemas.DBManager): The current user accessing the API.

    Returns:
        - JSONResponse: A JSON response indicating the success of the meaning creation.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    new_meaning = models.Meaning(sanskrit_word_id = db_word.id, meaning = meaning.meaning)
    db.add(new_meaning)
    db.commit()
    db.refresh(new_meaning)

    await logger_middleware.log_database_operations("meanings", new_meaning.id, "CREATE", current_user.email, new_meaning.meaning)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Meaning created successfully"})


@router.put("/{word}/meanings/{meaning_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word_meaning(word: str, meaning_id: int, meaning: schemas.MeaningCreate, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Updates the meaning of a word in the database.

    Parameters:
        - word (str): The word for which the meaning is to be updated.
        - meaning_id (int): The ID of the meaning to be updated.
        - meaning (schemas.MeaningCreate): The updated meaning for the word.
        - db (Session): The database session dependency.
        - current_user (schemas.DBManager): The current user accessing the API.

    Returns:
        None
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    db_meaning = db.query(models.Meaning).filter(models.Meaning.id == meaning_id).first()
    db_meaning.meaning = meaning.meaning
    db.commit()

    await logger_middleware.log_database_operations("meanings", meaning_id, "UPDATE", current_user.email, meaning.meaning)


@router.delete("/{word}/meanings/{meaning_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_meaning(word: str, meaning_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to delete a specific meaning associated with a word.
    
    Parameters:
        - word (str): The word for which the meaning needs to be deleted.
        - meaning_id (int): The ID of the meaning to be deleted.
        - db (Session): The database session dependency.
        - current_user (schemas.DBManager): The current user accessing the API.
    
    Returns:
        None
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    db_meaning = db.query(models.Meaning).filter(models.Meaning.id == meaning_id).first()
    if not db_meaning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meaning - {meaning_id} not found")  

    
    db.query(models.Meaning).filter(models.Meaning.id == meaning_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("meanings", meaning_id, "DELETE", current_user.email, db_meaning.meaning)


@router.delete("/{word}/meanings", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_meanings(word: str, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to delete all meanings associated with a specific word.
    
    Parameters:
        - word (str): The word for which the meanings need to be deleted.
        - db (Session): The database session dependency.
        - current_user (schemas.DBManager): The current user accessing the API.
    
    Returns:
        None
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id).delete()
    db.commit()

    await logger_middleware.log_database_operations("meanings", db_word.id, "DELETE_ALL", current_user.email)