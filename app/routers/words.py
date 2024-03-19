from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2

router = APIRouter(
    prefix="/words",
    tags=["Words"],
)

@router.get("/")
def get_words(db: Session = Depends(get_db)):
    words_query = db.query(
        models.SanskritWord,
        models.EnglishTranslation,
        models.ReferenceNyayaText,
    ).join(models.SanskritWord, models.EnglishTranslation.sanskrit_word_id == models.SanskritWord.id).join(models.ReferenceNyayaText, models.EnglishTranslation.sanskrit_word_id == models.ReferenceNyayaText.sanskrit_word_id).all()

    words = []
    for word_query in words_query:
        word = {
        "technicalTermDevanagiri": word_query.SanskritWord.technicalTermDevanagiri,
        "technicalTermRoman": word_query.SanskritWord.technicalTermRoman,
        "etymology": word_query.SanskritWord.etymology,
        "derivation": word_query.SanskritWord.derivation,
        "source": word_query.ReferenceNyayaText.source,
        "description": word_query.ReferenceNyayaText.description,
        "translation": word_query.EnglishTranslation.translation,
        "detailedDescription": word_query.EnglishTranslation.detailedDescription,
        }
        words.append(word)
    return words

def isSanskritWord(word) -> bool:
    devanagari_range = (0x0900, 0x097F)
    return all(ord(char) >= devanagari_range[0] and ord(char) <= devanagari_range[1] for char in word)

@router.get("/{word}")
def get_word(word: str, db: Session = Depends(get_db)):
    words_query = db.query(
        models.SanskritWord,
        models.EnglishTranslation,
        models.ReferenceNyayaText,
    ).join(models.SanskritWord, models.EnglishTranslation.sanskrit_word_id == models.SanskritWord.id).join(models.ReferenceNyayaText, models.EnglishTranslation.sanskrit_word_id == models.ReferenceNyayaText.sanskrit_word_id)

    if isSanskritWord(word):
        db_word = words_query.filter(models.SanskritWord.technicalTermDevanagiri == word).first()

    else:
        db_word = words_query.filter(models.SanskritWord.technicalTermRoman == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    
    word = {
        "technicalTermDevanagiri": db_word.SanskritWord.technicalTermDevanagiri,
        "technicalTermRoman": db_word.SanskritWord.technicalTermRoman,
        "etymology": db_word.SanskritWord.etymology,
        "derivation": db_word.SanskritWord.derivation,
        "source": db_word.ReferenceNyayaText.source,
        "description": db_word.ReferenceNyayaText.description,
        "translation": db_word.EnglishTranslation.translation,
        "detailedDescription": db_word.EnglishTranslation.detailedDescription,
        }
    
    return word

@router.post("/")
def create_word(word: schemas.WordBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_superuser == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    

    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.technicalTermDevanagiri == word.technicalTermDevanagiri).first()

    if db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word already exists")
    
    db_word = models.SanskritWord(**word.model_dump())
    
    return db_word


# @router.put("/{word}")
# def update_word(word: schemas.WordBase, db: Session = Depends(get_db)):
#     db_word = db.query(models.SanskritWord).filter(models.SanskritWord.technicalTermRoman == word.word).first()
    
#     if not db_word:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    
#     return db_word