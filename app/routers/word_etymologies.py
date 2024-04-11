from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.utils.lang import isDevanagariWord
from app.utils.converter import access_to_int
from app import schemas, models
from app.middleware.auth_middleware import get_current_db_manager
from typing import List


router = APIRouter(
    prefix="/words",
    tags=["Word - Etymologies"],
)


@router.get("/{word}/{meaning_id}/etymologies", response_model=List[schemas.EtymologyOut])
def get_word_etymologies(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_meaning = db.query(models.Meaning).filter(models.Meaning.id == meaning_id).first()

    if not db_meaning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meaning - {meaning_id} not found")
    
    db_etymologies = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id).all()

    return db_etymologies


@router.get("/{word}/{meaning_id}/etymologies/{etymology_id}", response_model=schemas.EtymologyOut)
def get_word_etymology(word: str, meaning_id: int, etymology_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_meaning = db.query(models.Meaning).filter(models.Meaning.id == meaning_id).first()

    if not db_meaning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meaning - {meaning_id} not found")
    
    db_etymology = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id, models.Etymology.id == etymology_id).first()

    if not db_etymology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Etymology - {etymology_id} not found")
    
    return db_etymology


@router.post("/{word}/{meaning_id}/etymologies")
def add_word_etymology(word: str, meaning_id: int, etymology: schemas.Etymology, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
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
        etymology = etymology.etymology
    )

    db.add(etymology)
    db.commit()
    db.refresh(etymology)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Etymology added successfully"})


@router.put("/{word}/{meaning_id}/etymologies/{etymology_id}")
def update_word_etymology(word: str, meaning_id: int, etymology_id: int, etymology: schemas.Etymology, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_meaning = db.query(models.Meaning).filter(models.Meaning.id == meaning_id).first()

    if not db_meaning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meaning - {meaning_id} not found")
    
    db_etymology = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id, models.Etymology.id == etymology_id).first()

    if not db_etymology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Etymology - {etymology_id} not found")
    
    db_etymology.etymology = etymology

    db.commit()
    db.refresh(db_etymology)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Etymology updated successfully"})


@router.delete("/{word}/{meaning_id}/etymologies", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_etymologies(word: str, meaning_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()

    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id).delete()

    db.commit()


@router.delete("/{word}/{meaning_id}/etymologies/{etymology_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_etymology(word: str, meaning_id: int, etymology_id: int, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()

    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id, models.Etymology.id == etymology_id).delete(synchronize_session=False)
    db.commit()