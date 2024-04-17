from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord, isEnglishWord
from app.middleware import auth_middleware


router = APIRouter(
    prefix="/words",
    tags=["Words"],
)


@router.get("/", response_model=List[schemas.WordOut])
def get_words(db: Session = Depends(get_db)):
    db_words = db.query(models.SanskritWord).all()

    words = []

    for db_word in db_words:
        meaning_ids = db.query(models.Meaning.id).filter(models.Meaning.sanskrit_word_id == db_word.id).all()
        words.append({
            "id": db_word.id,
            "sanskrit_word": db_word.sanskrit_word,
            "english_transliteration": db_word.english_transliteration,
            "meaning_ids": [x[0] for x in meaning_ids]
        })
    return words


@router.get("/{word}", response_model=schemas.WordOut)
def get_word(word: str, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    meaning_ids = db.query(models.Meaning.id).filter(models.Meaning.sanskrit_word_id == db_word.id).all()

    return {
        "id": db_word.id,
        "sanskrit_word": db_word.sanskrit_word,
        "english_transliteration": db_word.english_transliteration,
        "meaning_ids": [x[0] for x in meaning_ids]
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_word(word: schemas.WordCreate, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if word.sanskrit_word == "" or not word.sanskrit_word:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"sanskrit_word cannot be empty")
    
    if not isDevanagariWord(word.sanskrit_word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"sanskrit_word must be in Devanagari")

    if isDevanagariWord(word.sanskrit_word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word.english_transliteration).first()
    
    if db_word:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Word - {word.sanskrit_word} already exists")

    if not word.english_transliteration or word.english_transliteration == "":
        word.english_transliteration = transliterate(word.sanskrit_word, sanscript.DEVANAGARI, sanscript.IAST)

    new_word = models.SanskritWord(**word.model_dump())
    db.add(new_word)
    db.commit()
    db.refresh(new_word)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Word added successfully"})


@router.put("/{word}", status_code=status.HTTP_200_OK)
def update_word(word: str, wordIn: schemas.WordUpdate, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(wordIn.sanskrit_word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {wordIn.sanskrit_word} not found")
    
    if wordIn.sanskrit_word != word and db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == wordIn.sanskrit_word).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Word - {wordIn.sanskrit_word} already exists")
    
    if wordIn.english_transliteration != db_word.english_transliteration and db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == wordIn.english_transliteration).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"English Transliteration - {wordIn.english_transliteration} already exists")
    
    if not wordIn.english_transliteration or wordIn.english_transliteration == "":
        wordIn.english_transliteration = transliterate(wordIn.sanskrit_word, sanscript.DEVANAGARI, sanscript.IAST)
    
    db_word.sanskrit_word = wordIn.sanskrit_word
    db_word.english_transliteration = wordIn.english_transliteration
    
    db.commit()
    db.refresh(db_word)
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Word updated successfully", "word": db_word.sanskrit_word})



@router.delete("/{word}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word(word: str, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Example).filter(models.Example.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.SanskritWord).filter(models.SanskritWord.id == db_word.id).delete(synchronize_session=False)

    db.commit()