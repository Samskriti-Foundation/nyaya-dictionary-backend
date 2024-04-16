from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.middleware import auth_middleware


router = APIRouter(
    prefix="/words",
    tags=["Word - Meanings"],
)


@router.get("/{word}/meanings", response_model=List[schemas.MeaningOut])
def get_word_meanings(word: str, db: Session = Depends(get_db)):
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
def create_word_meaning(word: str, meaning: schemas.MeaningCreate, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
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
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Meaning created successfully"})


@router.put("/{word}/meanings/{meaning_id}", status_code=status.HTTP_200_OK)
def update_word_meaning(word: str, meaning_id: int, meaning: schemas.MeaningCreate, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
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

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Meaning updated successfully"})


@router.delete("/{word}/meanings/{meaning_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_meaning(word: str, meaning_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    db.query(models.Meaning).filter(models.Meaning.id == meaning_id).delete()
    db.commit()


@router.delete("/{word}/meanings", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_meanings(word: str, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
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