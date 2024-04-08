from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.utils.lang import isDevanagariWord
from app.utils.converter import access_to_int
from app import schemas, models
from app.middleware.auth_middleware import get_current_db_manager


router = APIRouter(
    prefix="/words",
    tags=["Words"],
)


@router.get("/{word}/{meaning_id}/etymologies")
def get_word_etymologies(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_etymologies = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id).all()

    etymologies = [x.etymology for x in db_etymologies]

    return etymologies


@router.post("/{word}/{meaning_id}/etymologies")
def add_word_etymologies(word: str, meaning_id: int, etymology: str, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
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
        etymology = etymology
    )

    db.add(etymology)
    db.commit()
    db.refresh(etymology)

    return {"Message": "Etymology added successfully"}