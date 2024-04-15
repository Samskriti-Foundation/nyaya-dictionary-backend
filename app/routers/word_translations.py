from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.middleware import auth_middleware


router = APIRouter(
    prefix="/words",
    tags=["Word - Translations"],
)


@router.get("/{word}/{meaning_id}/translations")
def get_word_translations(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_translations = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).all()

    translations = [x.translation for x in db_translations]

    return translations


@router.get("/{word}/{meaning_id}/translations/{translation_id}")
def get_word_translation(word: str, meaning_id: int, translation_id: int, db: Session = Depends(get_db)):
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
def create_word_translation(word: str, meaning_id: int, translation: schemas.Translation, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")   
        
    db_translation = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).first()

    if db_translation:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Translation - {translation.translation} already exists")
    
    new_translation = models.Translation(sanskrit_word_id = db_word.id, meaning_id = meaning_id, translation = translation.translation)
    db.add(new_translation)
    db.commit()
    db.refresh(new_translation)

    return new_translation


@router.delete("/{word}/{meaning_id}/translations/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_translation(word: str, meaning_id: int, translation_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")   
    
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id, models.Translation.id == translation_id).delete()
    db.commit()



@router.delete("/{word}/{meaning_id}/translations", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_translations(word: str, meaning_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
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