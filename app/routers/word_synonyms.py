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
    tags=["Word - Synonyms"],
)


@router.get("/{word}/{meaning_id}/synonyms", response_model=List[schemas.SynonymOut])
def get_word_synonyms(word: str, meaning_id: int, db: Session = Depends(get_db)):
    """
    Get synonyms of a word based on the word and meaning_id.
    
    Parameters:
        word (str): The word for which synonyms are requested.
        meaning_id (int): The meaning ID associated with the word.
        db (Session): The SQLAlchemy database session.
    
    Returns:
        List[schemas.SynonymOut]: A list of synonym objects for the given word and meaning_id.
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonyms = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id).all()

    return db_synonyms


@router.get("/{word}/{meaning_id}/synonyms/{synonym_id}", response_model=schemas.SynonymOut)
def get_word_synonym(word: str, meaning_id: int, synonym_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific synonym for a given word and meaning_id.

    Parameters:
        word (str): The word for which the synonym is requested.
        meaning_id (int): The meaning ID associated with the word.
        synonym_id (int): The ID of the specific synonym requested.
        db (Session): The SQLAlchemy database session.

    Returns:
        schemas.SynonymOut: The synonym object for the given word, meaning_id, and synonym_id.
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonym = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).first()

    if not db_synonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Synonym - {synonym_id} not found")
    
    return db_synonym


@router.post("/{word}/{meaning_id}/synonyms", status_code=status.HTTP_201_CREATED)
async def create_word_synonym(word: str, meaning_id: int, synonym: schemas.Synonym, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    A function to create a new synonym for a given word and meaning_id.
    
    Parameters:
        word (str): The word for which the synonym is being created.
        meaning_id (int): The meaning ID associated with the word.
        synonym (schemas.Synonym): The synonym object containing the details of the new synonym.
        db (Session): The SQLAlchemy database session.
        current_user (schemas.DBManager): The current user requesting the synonym creation.
    
    Returns:
        JSONResponse: A response with a message indicating the success of the synonym creation.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    new_synonym = models.Synonym(**synonym.model_dump(), sanskrit_word_id=db_word.id, meaning_id=meaning_id)

    db.add(new_synonym)
    db.commit()
    db.refresh(new_synonym)

    await logger_middleware.log_database_operations("synonyms", new_synonym.id, "CREATE", current_user.email, new_synonym.synonym)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Synonym created successfully"})


@router.put("/{word}/{meaning_id}/synonyms/{synonym_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word_synonym(word: str, meaning_id: int, synonym_id: int, synonym: schemas.Synonym, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Updates a synonym for a specific word and meaning in the database.

    Parameters:
        word (str): The word for which the synonym is being updated.
        meaning_id (int): The ID of the meaning associated with the synonym.
        synonym_id (int): The ID of the synonym being updated.
        synonym (schemas.Synonym): The updated synonym object.
        db (Session): The SQLAlchemy database session.
        current_user (schemas.DBManager): The current user performing the update.

    Returns:
        JSONResponse: A response indicating the success of the synonym update.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonym = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).first()

    if not db_synonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Synonym - {synonym_id} not found")
    
    db_synonym.synonym = synonym.synonym
    db.commit()
    db.refresh(db_synonym)

    await logger_middleware.log_database_operations("synonyms", db_synonym.id, "UPDATE", current_user.email, db_synonym.synonym)


@router.delete("/{word}/{meaning_id}/synonyms/{synonym_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_synonym(word: str, meaning_id: int, synonym_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Deletes a synonym for a specific word and meaning in the database.

    Parameters:
        word (str): The word for which the synonym is being deleted.
        meaning_id (int): The ID of the meaning associated with the synonym.
        synonym_id (int): The ID of the synonym being deleted.
        db (Session): The SQLAlchemy database session.
        current_user (schemas.DBManager): The current user performing the deletion.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonym = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).first()

    if not db_synonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Synonym - {synonym_id} not found")
    
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("synonyms", db_synonym.id, "DELETE", current_user.email, db_synonym.synonym)


@router.delete("/{word}/{meaning_id}/synonyms", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_synonyms(word: str, meaning_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Deletes all synonyms associated with a specific word and meaning from the database.

    Parameters:
        word (str): The word for which synonyms are being deleted.
        meaning_id (int): The ID of the meaning associated with the synonyms.
        db (Session): The SQLAlchemy database session.
        current_user (schemas.DBManager): The current user performing the deletion.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()

    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("synonyms", meaning_id, "DELETE_ALL", current_user.email)