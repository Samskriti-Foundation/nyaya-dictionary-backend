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
    tags=["Word - Synonyms"],
)


@router.get("/{word}/{meaning_id}/synonyms", response_model=List[schemas.SynonymOut])
def get_word_synonyms(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonyms = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id).all()

    return db_synonyms


@router.get("/{word}/{meaning_id}/synonyms/{synonym_id}", response_model=schemas.SynonymOut)
def get_word_synonym(word: str, meaning_id: int, synonym_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonym = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).first()

    if not db_synonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Synonym - {synonym_id} not found")
    
    return db_synonym


@router.post("/{word}/{meaning_id}/synonyms", status_code=status.HTTP_201_CREATED)
def create_word_synonym(word: str, meaning_id: int, synonym: schemas.Synonym, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    new_synonym = models.Synonym(**synonym.model_dump(), sanskrit_word_id=db_word.id, meaning_id=meaning_id)

    db.add(new_synonym)
    db.commit()
    db.refresh(new_synonym)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Synonym created successfully"})


@router.put("/{word}/{meaning_id}/synonyms/{synonym_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_word_synonym(word: str, meaning_id: int, synonym_id: int, synonym: schemas.Synonym, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonym = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).first()

    if not db_synonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Synonym - {synonym_id} not found")
    
    db_synonym.synonym = synonym.synonym
    db.commit()
    db.refresh(db_synonym)


@router.delete("/{word}/{meaning_id}/synonyms/{synonym_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_synonym(word: str, meaning_id: int, synonym_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_synonym = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).first()

    if not db_synonym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Synonym - {synonym_id} not found")
    
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id, models.Synonym.id == synonym_id).delete()
    db.commit()



@router.delete("/{word}/{meaning_id}/synonyms", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_synonyms(word: str, meaning_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()

    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, models.Synonym.meaning_id == meaning_id).delete()
    db.commit()