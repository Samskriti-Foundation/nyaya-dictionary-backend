from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.database import get_db
from app.middleware import auth_middleware


router = APIRouter(
    prefix="/words",
    tags=["Word - Nyaya Text References"]
)


@router.get("/{word}/{meaning_id}/nyaya_text_references", response_model=List[schemas.NyayaTextReferenceOut])
def get_word_nyaya_text_references(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_nyaya_text_references = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id).all()

    return db_nyaya_text_references


@router.get("/{word}/{meaning_id}/nyaya_text_references/{nyaya_text_id}", response_model=schemas.NyayaTextReferenceOut)
def get_word_reference_nyaya_text(word: str, meaning_id: int, nyaya_text_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_reference_nyaya_text = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id, models.ReferenceNyayaText.id == nyaya_text_id).first()

    if not db_reference_nyaya_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reference Nyaya Text - {nyaya_text_id} not found")  

    return db_reference_nyaya_text


@router.post("/{word}/{meaning_id}/nyaya_text_references", status_code=status.HTTP_201_CREATED)
def create_word_reference_nyaya_text(word: str, meaning_id: int, reference_nyaya_text: schemas.NyayaTextReference, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    new_reference_nyaya_text = models.ReferenceNyayaText(**reference_nyaya_text.model_dump(), sanskrit_word_id = db_word.id, meaning_id = meaning_id)
    db.add(new_reference_nyaya_text)
    db.commit()
    db.refresh(new_reference_nyaya_text)


@router.put("{word}/{meaning_id}/nyaya_text_references/{nyaya_text_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_word_reference_nyaya_text(word: str, meaning_id: int, nyaya_text_id: int, reference_nyaya_text: schemas.NyayaTextReference, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_nyaya_text_reference = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id, models.ReferenceNyayaText.id == nyaya_text_id).first()

    if not db_nyaya_text_reference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reference Nyaya Text - {nyaya_text_id} not found")
    
    db_nyaya_text_reference.source = reference_nyaya_text.source
    db_nyaya_text_reference.description = reference_nyaya_text.description
    
    db.commit()


@router.delete("/{word}/{meaning_id}/nyaya_text_references/{nyaya_text_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_reference_nyaya_text(word: str, meaning_id: int, nyaya_text_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.id == nyaya_text_id).delete()
    db.commit()


@router.delete("/{word}/{meaning_id}/nyaya_text_references", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_nyaya_text_references(word: str, meaning_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()

    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id).delete()
    db.commit()