from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
from app.middleware import auth_middleware, logger_middleware
from typing import List


router = APIRouter(
    prefix="/words",
    tags=["Word - Examples"],
)


@router.get("/{word}/{meaning_id}/examples", response_model=List[schemas.ExampleOut])
def get_word_examples(word: str, meaning_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_examples = db.query(models.Example).filter(models.Example.sanskrit_word_id == db_word.id, models.Example.meaning_id == meaning_id).all()

    return db_examples


@router.get("/{word}/{meaning_id}/examples/{examples_id}", response_model=schemas.ExampleOut)
def get_word_example(word: str, meaning_id: int, examples_id: int, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_example = db.query(models.Example).filter(models.Example.sanskrit_word_id == db_word.id, models.Example.meaning_id == meaning_id, models.Example.id == examples_id).first()

    if not db_example:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Example - {examples_id} not found")
    
    return db_example
    

@router.post("/{word}/{meaning_id}/examples", status_code=status.HTTP_201_CREATED)
async def create_word_example(word: str, meaning_id: int, example: schemas.Example, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    new_example = models.Example(**example.model_dump(), sanskrit_word_id=db_word.id, meaning_id=meaning_id)

    db.add(new_example)
    db.commit()
    db.refresh(new_example)

    await logger_middleware.log_database_operations("examples", new_example.id, "CREATE", current_user.email, f"{new_example.example_sentence} - {new_example.applicable_modern_context}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Example created successfully"})


@router.put("/{word}/{meaning_id}/examples/{examples_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_word_example(word: str, meaning_id: int, examples_id: int, example: schemas.Example, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_example = db.query(models.Example).filter(models.Example.meaning_id == meaning_id, models.Example.id == examples_id).first()

    if not db_example:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Example - {examples_id} not found")
    
    db_example.example_sentence = example.example_sentence
    db_example.applicable_modern_context = example.applicable_modern_context
    db.commit()
    db.refresh(db_example)

    await logger_middleware.log_database_operations("examples", examples_id, "UPDATE", current_user.email, f"{db_example.example_sentence} - {db_example.applicable_modern_context}")


@router.delete("/{word}/{meaning_id}/examples/{examples_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_example(word: str, meaning_id: int, examples_id: int, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db_example = db.query(models.Example).filter(models.Example.meaning_id == meaning_id, models.Example.id == examples_id).first()

    if not db_example:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Example - {examples_id} not found")
    
    db.query(models.Example).filter(models.Example.meaning_id == meaning_id, models.Example.id == examples_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("examples", examples_id, "DELETE", current_user.email, db_example.example_sentence)


@router.delete("/{word}/{meaning_id}/examples", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_examples(word: str, meaning_id, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_user.access) < access_to_int(schemas.Access.ALL):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    db.query(models.Example).filter(models.Example.sanskrit_word_id == db_word.id, models.Example.meaning_id == meaning_id).delete()
    db.commit()

    await logger_middleware.log_database_operations("examples", meaning_id, "DELETE_ALL", current_user.email)