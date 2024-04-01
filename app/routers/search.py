from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.utils.lang import isDevanagariWord
from app.database import get_db

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

@router.get("/{word}")
def search(word: str, limit: int = 5, db: Session = Depends(get_db)):
    """
    Searches for a word in the database and returns a list of matching sanskrit words and their english transliterations.
    
    Args:
        word (str): The word to search for.
        limit (int, optional): The maximum number of results to return. Defaults to 5.
        db (Session, optional): The database session. Defaults to the result of the `get_db` function.
    
    Returns:
        List[List[str]]: A list of lists, where each inner list contains a sanskrit word and its english transliteration.
    
    Raises:
        HTTPException: If no match is found for the given word.
    """
    if isDevanagariWord(word):
        matches = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word.contains(word)).limit(limit).all()
    else:
        matches = db.query(models.SanskritWord).filter(models.SanskritWord.english_word.icontains(word)).limit(limit).all()

    if not matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No match found")
    
    res = [[match.sanskrit_word, match.english_word] for match in matches]

    return res