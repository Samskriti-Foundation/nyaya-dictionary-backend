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
    tags=["Word - Translations"],
)


@router.get("/{word}/{meaning_id}/translations", response_model=List[schemas.TranslationOut])
def get_word_translations(word: str, meaning_id: int, db: Session = Depends(get_db)):
    """
    Retrieves translations for a given word and meaning ID.
    
    Parameters:
    - word: str - The word for which translations are requested.
    - meaning_id: int - The ID of the meaning for which translations are requested.
    - db: Session - The database session to use (provided by Depends(get_db)).
    
    Returns:
    - List[schemas.TranslationOut]: A list of translation objects for the given word and meaning ID.
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_translations = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).all()

    return db_translations


@router.get("/{word}/{meaning_id}/translations/{translation_id}", response_model=schemas.TranslationOut)
def get_word_translation(word: str, meaning_id: int, translation_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific translation for a given word, meaning ID, and translation ID.

    Parameters:
    - word: str - The word for which the translation is being retrieved.
    - meaning_id: int - The ID of the meaning associated with the translation.
    - translation_id: int - The ID of the translation being retrieved.
    - db: Session - The database session to use (provided by Depends(get_db)).

    Returns:
    - schemas.TranslationOut: The translation object for the specified word, meaning ID, and translation ID.
    """
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")   
    
    db_translation = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id, models.Translation.id == translation_id).first()

    if not db_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Translation - {translation_id} not found")  

    return db_translation


@router.post("/{word}/{meaning_id}/translations", status_code=status.HTTP_201_CREATED)
async def create_word_translation(word: str, meaning_id: int, translation: schemas.Translation, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Creates a new word translation in the database.

    Parameters:
    - word: str
    - meaning_id: int
    - translation: schemas.Translation
    - db: Session = Depends(get_db)
    - current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)

    Returns:
    - JSONResponse with status code 201 if successful, containing a success message.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")   
        
    new_translation = models.Translation(sanskrit_word_id = db_word.id, meaning_id = meaning_id, translation = translation.translation, language = translation.language)
    db.add(new_translation)
    db.commit()
    db.refresh(new_translation)

    await logger_middleware.log_database_operations("translations", new_translation.id, "CREATE", current_user.email, f"{new_translation.language} - {new_translation.translation}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Translation created successfully"})


@router.put("/{word}/{meaning_id}/translations/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word_translation(word: str, meaning_id: int, translation_id: int, translation: schemas.Translation, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Updates a specific word translation identified by the word, meaning id, and translation id.
    
    Parameters:
    - word: a string representing the word
    - meaning_id: an integer representing the meaning id
    - translation_id: an integer representing the translation id
    - translation: a schemas.Translation object containing the new translation data
    - db: a Session object for the database connection
    - current_user: a schemas.DBManager object representing the current user
    
    Returns:
    No direct return value. Updates the translation in the database.
    """
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_translation = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id, models.Translation.id == translation_id).first()

    if not db_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Translation - {translation_id} not found")  

    db_translation.translation = translation.translation
    db_translation.language = translation.language
    db.commit()
    db.refresh(db_translation)

    await logger_middleware.log_database_operations("translations", translation_id, "UPDATE", current_user.email, f"{translation.language} - {translation.translation}")

@router.delete("/{word}/{meaning_id}/translations/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_translation(word: str, meaning_id: int, translation_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Deletes a specific translation for a word and meaning based on the provided IDs.

    Parameters:
    - word: str
    - meaning_id: int
    - translation_id: int
    - db: Session = Depends(get_db)
    - current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)

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
    
    db_translation = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id, models.Translation.id == translation_id).first()
    
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id, models.Translation.id == translation_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("translations", translation_id, "DELETE", current_user.email, f"{db_translation.language} - {db_translation.translation}")


@router.delete("/{word}/{meaning_id}/translations", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_translations(word: str, meaning_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    """
    Deletes all translations for a specific word and meaning based on the provided IDs.

    Parameters:
    - word: str - The word for which translations are to be deleted.
    - meaning_id: int - The ID of the meaning for which translations are to be deleted.
    - db: Session - The database session to use (provided by Depends(get_db)).
    - current_user: schemas.DBManager - The current user performing the action.

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
    
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("translations", meaning_id, "DELETE_ALL", current_user.email)