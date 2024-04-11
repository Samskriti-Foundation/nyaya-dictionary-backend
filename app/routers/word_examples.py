from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.middleware import auth_middleware
from typing import List


router = APIRouter(
    prefix="/words",
    tags=["Word - Examples"],
)


@router.get("/{word}/{meaning_id}/examples", response_model=List[schemas.ExampleOut])
def get_word_examples(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_examples = db.query(models.Example.example_sentence, models.Example.applicable_modern_context).filter(models.Example.sanskrit_word_id == db_word.id, models.Example.meaning_id == meaning_id).all()

    return db_examples


@router.get("/{word}/{meaning_id}/examples/{examples_id}", response_model=schemas.ExampleOut)
def get_word_example(word: str, meaning_id, example_id: str, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")