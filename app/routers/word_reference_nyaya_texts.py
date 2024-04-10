from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.utils.lang import isDevanagariWord
from app.database import get_db


router = APIRouter(
    prefix="/words",
    tags=["Word - Nyaya Text References"]
)


@router.get("/{word}/{meaning_id}/reference_nyaya_texts")
def get_word_reference_nyaya_texts(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_reference_nyaya_texts = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id).all()

    reference_nyaya_texts = [x.source for x in db_reference_nyaya_texts]

    return reference_nyaya_texts