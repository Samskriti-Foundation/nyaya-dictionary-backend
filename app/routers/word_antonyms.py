from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas
from typing import List
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.middleware import auth_middleware


router = APIRouter(
    prefix="/words",
    tags=["Words - Antonyms"],
)


@router.get("/{word}/{meaning_id}/antonyms", response_model=List[schemas.AntonymOut])
def get_word_antonyms(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_antonyms = db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id).all()

    antonyms = [x.antonym for x in db_antonyms]

    return antonyms


@router.get("{word}/{meaning_id}/antonyms/{antonym_id}")
def get_word_anyonym(word: str, meaning_id: int, antonym_id: int, db: Session = Depends(get_db)):
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
def create_word_antonym(word: str, meaning_id: int, antonym: schemas.Antonym, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
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

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Successfully created antonym"})


@router.put("/{word}/{meaning_id}/antonyms/{antonym_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_word_antonym(word: str, meaning_id: int, antonym_id: int, antonym: schemas.Antonym, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
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


@router.delete("/{word}/{meaning_id}/antonyms/{antonym_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_antonym(word: str, meaning_id: int, antonym_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, models.Antonym.meaning_id == meaning_id, models.Antonym.id == antonym_id).delete()
    db.commit()


@router.delete("/{word}/{meaning_id}/antonyms", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_antonyms(word: str, meaning_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
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