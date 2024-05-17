from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.utils.lang import isDevanagariWord
from app.utils.converter import access_to_int
from app import schemas, models
from app.middleware.auth_middleware import get_current_db_manager
from app.middleware.logger_middleware import log_database_operations
from typing import List


router = APIRouter(
    prefix="/words",
    tags=["Word - Etymologies"],
)


@router.get("/{word}/{meaning_id}/etymologies", response_model=List[schemas.EtymologyOut])
def get_word_etymologies(word: str, meaning_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a list of etymologies for a given word and meaning ID from the database.

    Parameters:
    - word: a string representing the word
    - meaning_id: an integer representing the meaning ID
    - db: a SQLAlchemy Session dependency

    Returns:
    - A list of EtymologyOut objects representing the etymologies for the word and meaning ID
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
    
    db_etymologies = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id).all()

    return db_etymologies


@router.get("/{word}/{meaning_id}/etymologies/{etymology_id}", response_model=schemas.EtymologyOut)
def get_word_etymology(word: str, meaning_id: int, etymology_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific etymology for a given word, meaning ID, and etymology ID.

    Parameters:
    - word: a string representing the word
    - meaning_id: an integer representing the meaning ID
    - etymology_id: an integer representing the etymology ID
    - db: a SQLAlchemy Session dependency

    Returns:
    - An EtymologyOut object representing the retrieved etymology
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
    
    db_etymology = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id, models.Etymology.id == etymology_id).first()

    if not db_etymology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Etymology - {etymology_id} not found")
    
    return db_etymology


@router.post("/{word}/{meaning_id}/etymologies")
async def add_word_etymology(word: str, meaning_id: int, etymology: schemas.Etymology, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
    """
    Adds a new etymology for a word and meaning in the database.

    Parameters:
    - word: str - The word for which the etymology is being added.
    - meaning_id: int - The ID of the meaning associated with the etymology.
    - etymology: schemas.Etymology - The etymology information to be added.
    - db: Session - The database session.
    - current_db_manager: schemas.DBManager - The current database manager.

    Returns:
    - JSONResponse: A response indicating the status of the operation.
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    etymology = models.Etymology(
        sanskrit_word_id = db_word.id,
        meaning_id = meaning_id,
        etymology = etymology.etymology
    )

    db.add(etymology)
    db.commit()
    db.refresh(etymology)

    await log_database_operations("etymology", etymology.id, "CREATE", current_db_manager.email, etymology.etymology)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Etymology added successfully"})


@router.put("/{word}/{meaning_id}/etymologies/{etymology_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word_etymology(word: str, meaning_id: int, etymology_id: int, etymology: schemas.Etymology, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
    """
    Updates the etymology of a word based on the provided word, meaning ID, and etymology ID.
    
    Parameters:
    - word: a string representing the word
    - meaning_id: an integer representing the meaning ID
    - etymology_id: an integer representing the etymology ID
    - etymology: an Etymology object containing the updated etymology information
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
    
    db_meaning = db.query(models.Meaning).filter(models.Meaning.id == meaning_id).first()

    if not db_meaning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meaning - {meaning_id} not found")
    
    db_etymology = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id, models.Etymology.id == etymology_id).first()

    if not db_etymology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Etymology - {etymology_id} not found")
    
    db_etymology.etymology = etymology.etymology

    db.commit()
    db.refresh(db_etymology)

    await log_database_operations("etymology", db_etymology.id, "UPDATE", current_db_manager.email, db_etymology.etymology)


@router.delete("/{word}/{meaning_id}/etymologies", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_etymologies(word: str, meaning_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
    """
    Deletes all etymologies associated with a specific word and meaning ID from the database.

    Parameters:
    - word: a string representing the word
    - meaning_id: an integer representing the meaning ID
    - db: a SQLAlchemy Session dependency
    - current_db_manager: a dependency to get the current database manager

    Returns:
    - No explicit return value, but deletes the etymologies from the database
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()

    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id).delete()
    db.commit()

    await log_database_operations("etymology", meaning_id, "DELETE_ALL", current_db_manager.email)


@router.delete("/{word}/{meaning_id}/etymologies/{etymology_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_etymology(word: str, meaning_id: int, etymology_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
    """
    Deletes a specific etymology for a word and meaning in the database.

    Parameters:
    - word: str - The word for which the etymology is being deleted.
    - meaning_id: int - The ID of the meaning associated with the etymology.
    - etymology_id: int - The ID of the etymology to be deleted.
    - db: Session - The database session.
    - current_db_manager: schemas.DBManager - The current database manager.

    Returns:
    - No explicit return value, but deletes the specified etymology from the database
    """
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()

    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_etymology = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id, models.Etymology.id == etymology_id).first()

    if not db_etymology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Etymology - {etymology_id} not found")
    
    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id, models.Etymology.id == etymology_id).delete()
    db.commit()

    await log_database_operations("etymology", etymology_id, "DELETE", current_db_manager.email, db_etymology.etymology)