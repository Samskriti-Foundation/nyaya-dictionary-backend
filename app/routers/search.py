from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.utils.lang import isDevanagariWord
from app.database import get_db

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

def isSanskritWord(word) -> bool:
    devanagari_range = (0x0900, 0x097F)
    return all(ord(char) >= devanagari_range[0] and ord(char) <= devanagari_range[1] for char in word)

@router.get("/{word}")
def search(word: str, limit: int = 5, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        matches = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word.contains(word)).limit(limit).all()
    else:
        matches = db.query(models.SanskritWord).filter(models.SanskritWord.english_word.icontains(word)).limit(limit).all()

    if not matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No match found")
    
    res = []
    for match in matches:
        res.append(match.sanskrit_word)
        res.append(match.english_word)

    return res