from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from sqlalchemy.orm import Session
import models, schemas

router = APIRouter(
    prefix="/words",
    tags=["Words"],
)

@router.get("/")
def get_words(db: Session = Depends(get_db)):
    words = db.query(models.SanskritWord).all()
    return words


@router.get("/{word}")
def get_word(word: str, db: Session = Depends(get_db)):
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.technicalTermRoman == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    
    return db_word

@router.post("/")
def create_word(word: schemas.WordBase, db: Session = Depends(get_db)):
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.technicalTermRoman == word.word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    
    return db_word