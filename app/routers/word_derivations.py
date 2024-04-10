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
    tags=["Word - Derivations"],
)


@router.get("/{word}/{meaning_id}/derivations", response_model=List[schemas.DerivationOut])
def get_word_derivations(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_derivations = db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id).all()

    return db_derivations


@router.get("/{word}/{meaning_id}/derivations/{derivation_id}", response_model=schemas.DerivationOut)
def get_word_derivation(word: str, meaning_id: int, derivation_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_derivation = db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id, models.Derivation.id == derivation_id).first()

    if not db_derivation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Derivation - {derivation_id} not found")
    
    return db_derivation


@router.post("/{word}/{meaning_id}/derivations")
def create_word_derivation(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_derivation = models.Derivation(sanskrit_word_id=db_word.id, meaning_id=meaning_id, derivation="")

    db.add(db_derivation)
    db.commit()
    db.refresh(db_derivation)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Derivation added successfully"})


@router.put("/{word}/{meaning_id}/derivations/{derivation_id}")
def update_word_derivation(word: str, meaning_id: int, derivation_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id, models.Derivation.id == derivation_id).update({"derivation": ""})
    db.commit()

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Derivation updated successfully"})


@router.delete("/{word}/{meaning_id}/derivations", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_derivations(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id).delete()
    db.commit()

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Derivations deleted successfully"})


@router.delete("/{word}/{meaning_id}/derivations/{derivation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_derivation(word: str, meaning_id: int, derivation_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id, models.Derivation.id == derivation_id).delete()
    db.commit()

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Derivation deleted successfully"})