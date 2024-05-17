from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.database import get_db
from app.middleware import auth_middleware, logger_middleware


router = APIRouter(
    prefix="/words",
    tags=["Word - Nyaya Text References"]
)


@router.get("/{word}/{meaning_id}/nyaya-text-references", response_model=List[schemas.NyayaTextReferenceOut])
def get_word_nyaya_text_references(word: str, meaning_id: int, db: Session = Depends(get_db)):
    """
    Retrieves Nyaya text references for a specific word and meaning ID from the database.

    Parameters:
        - word: a string representing the word to search for
        - meaning_id: an integer representing the meaning ID to search for
        - db: a SQLAlchemy Session dependency

    Returns:
        - A list of Nyaya text references associated with the word and meaning ID
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_nyaya_text_references = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id).all()

    return db_nyaya_text_references


@router.get("/{word}/{meaning_id}/nyaya-text-references/{nyaya_text_id}", response_model=schemas.NyayaTextReferenceOut)
def get_word_reference_nyaya_text(word: str, meaning_id: int, nyaya_text_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific Nyaya text reference for a word, meaning ID, and Nyaya text ID from the database.

    Parameters:
        - word: a string representing the word to search for
        - meaning_id: an integer representing the meaning ID to search for
        - nyaya_text_id: an integer representing the Nyaya text ID to search for
        - db: a SQLAlchemy Session dependency

    Returns:
        - The Nyaya text reference associated with the word, meaning ID, and Nyaya text ID
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_reference_nyaya_text = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id, models.ReferenceNyayaText.id == nyaya_text_id).first()

    if not db_reference_nyaya_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reference Nyaya Text - {nyaya_text_id} not found")  

    return db_reference_nyaya_text


@router.post("/{word}/{meaning_id}/nyaya-text-references", status_code=status.HTTP_201_CREATED)
async def create_word_reference_nyaya_text(word: str, meaning_id: int, reference_nyaya_text: schemas.NyayaTextReference, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Retrieves a specific Nyaya text reference for a word, meaning ID, and Nyaya text ID from the database.

    Parameters:
        - word: a string representing the word to search for
        - meaning_id: an integer representing the meaning ID to search for
        - nyaya_text_id: an integer representing the Nyaya text ID to search for
        - db: a SQLAlchemy Session dependency

    Returns:
        - The Nyaya text reference associated with the word, meaning ID, and Nyaya text ID
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    new_reference_nyaya_text = models.ReferenceNyayaText(**reference_nyaya_text.model_dump(), sanskrit_word_id = db_word.id, meaning_id = meaning_id)
    db.add(new_reference_nyaya_text)
    db.commit()
    db.refresh(new_reference_nyaya_text)

    await logger_middleware.log_database_operations("reference_nyaya_texts", new_reference_nyaya_text.id, "CREATE", current_db_manager.email, f"{new_reference_nyaya_text.source} - {new_reference_nyaya_text.description}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Reference Nyaya Text created successfully"})


@router.put("/{word}/{meaning_id}/nyaya-text-references/{nyaya_text_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word_reference_nyaya_text(word: str, meaning_id: int, nyaya_text_id: int, reference_nyaya_text: schemas.NyayaTextReference, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Updates a reference to a Nyaya text for a specific word, meaning ID, and Nyaya text ID in the database.

    Parameters:
        - word: a string representing the word to update the reference for
        - meaning_id: an integer representing the meaning ID of the word
        - nyaya_text_id: an integer representing the Nyaya text ID to update the reference for
        - reference_nyaya_text: a NyayaTextReference object containing the reference details
        - db: a SQLAlchemy Session dependency
        - current_db_manager: a DBManager object representing the current database manager

    Returns:
        - None
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_nyaya_text_reference = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id, models.ReferenceNyayaText.id == nyaya_text_id).first()

    if not db_nyaya_text_reference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reference Nyaya Text - {nyaya_text_id} not found")
    
    db_nyaya_text_reference.source = reference_nyaya_text.source
    db_nyaya_text_reference.description = reference_nyaya_text.description
    
    db.commit()

    await logger_middleware.log_database_operations("reference_nyaya_texts", nyaya_text_id, "UPDATE", current_db_manager.email, f"{reference_nyaya_text.source} - {reference_nyaya_text.description}")


@router.delete("/{word}/{meaning_id}/nyaya-text-references/{nyaya_text_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_reference_nyaya_text(word: str, meaning_id: int, nyaya_text_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to delete a reference Nyaya text associated with a word and a specific meaning.
    
    Parameters:
    - word: str - The word for which the reference Nyaya text is being deleted.
    - meaning_id: int - The ID of the meaning associated with the reference Nyaya text.
    - nyaya_text_id: int - The ID of the reference Nyaya text to be deleted.
    - db: Session - The database session.
    - current_db_manager: schemas.DBManager - The current database manager accessing the operation.
    
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
    
    db_reference_nyaya_text = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.meaning_id == meaning_id, models.ReferenceNyayaText.id == nyaya_text_id).first()

    if not db_reference_nyaya_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reference Nyaya Text - {nyaya_text_id} not found")
    
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.meaning_id == meaning_id, models.ReferenceNyayaText.id == nyaya_text_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("reference_nyaya_texts", nyaya_text_id, "DELETE", current_db_manager.email, f"{db_reference_nyaya_text.source}")


@router.delete("/{word}/{meaning_id}/nyaya-text-references", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_nyaya_text_references(word: str, meaning_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to delete Nyaya text references associated with a word and a specific meaning ID.
    
    Parameters:
        - word: str - The word for which the Nyaya text references are being deleted
        - meaning_id: int - The ID of the meaning associated with the Nyaya text references
        - db: Session - The database session
        - current_db_manager: schemas.DBManager - The current database manager accessing the operation
    
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
    
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("reference_nyaya_texts", meaning_id, "DELETE_ALL", current_db_manager.email)