from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from app.utils.lang import isDevanagariWord

router = APIRouter(
    prefix="/words",
    tags=["Words"],
)

@router.get("/", response_model=List[schemas.WordOut])
def get_words(db: Session = Depends(get_db)):
    db_words = db.query(models.SanskritWord).all()

    words = []

    for db_word in db_words:
        word = {}
        
        word["id"] = db_word.id
        word["sanskrit_word"] = db_word.sanskrit_word
        word["english_word"] = db_word.english_word
        word["etymology"] = [x.etymology for x in db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).all()]
        word["derivation"] = [x.derivation for x in db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).all()]
        word["translations"] = [{
            "english_translation": x.english_translation,
            "sanskrit_translation": x.hindi_translation,
            "kannada_translation": x.kannada_translation,
             } for x in db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).all()]
        word["nyaya_reference_text"] = [{
            "source": x.source,
            "description": x.description
        } for x in db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).all()]
        word["synonyms"] = [x.synonym for x in db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).all()]
        word["antonyms"] = [x.antonym for x in db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).all()]

        words.append(word)
        
    return words

@router.get("/{word}", response_model=schemas.WordOut)
def get_word(word: str, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_word == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    word = {}

    word["id"] = db_word.id
    word["sanskrit_word"] = db_word.sanskrit_word
    word["english_word"] = db_word.english_word
    word["etymologies"] = [x.etymology for x in db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).all()]
    word["derivations"] = [x.derivation for x in db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).all()]
    translation = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).first()
    word["translation"] = {
        "english_translation": translation.english_translation,
        "hindi_translation": translation.hindi_translation,
        "kannada_translation": translation.kannada_translation,
            } 
    word["nyaya_reference_texts"] = [{
        "source": x.source,
        "description": x.description
    } for x in db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).all()]
    word["synonyms"] = [x.synonym for x in db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).all()]
    word["antonyms"] = [x.antonym for x in db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).all()]
    
    return word

@router.post("/")
def create_word(word: schemas.Word, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()

    if db_word:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Word already exists")

    if not isDevanagariWord(word.sanskrit_word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word is not in Devanagari")
    
    new_word = models.SanskritWord(
        sanskrit_word = word.sanskrit_word,
        english_word = transliterate(word.sanskrit_word, sanscript.DEVANAGARI, sanscript.HK),
    )
    db.add(new_word)
    db.flush()

    if word.etymologies:
        etymologies = [models.Etymology(
            sanskrit_word_id = new_word.id,
            etymology = etymology
        ) for etymology in word.etymologies]
        db.add_all(etymologies)

    if word.derivations:
        derivations = [models.Derivation(
            sanskrit_word_id = new_word.id,
            derivation = derivation
        ) for derivation in word.derivations]
        db.add_all(derivations)


    if word.translation:
        translation = models.Translation(
            sanskrit_word_id = new_word.id,
            english_translation = word.translation.english_translation,
            kannada_translation = word.translation.kannada_translation,
            hindi_translation = word.translation.hindi_translation,
            detailedDescription = word.translation.detailedDescription,
        )
        db.add(translation)
    
    
    if word.reference_nyaya_texts:
        references = [models.ReferenceNyayaText(
            sanskrit_word_id = new_word.id,
            source = reference.source,
            description = reference.description
        ) for reference in word.reference_nyaya_texts]
        db.add_all(references)
    
    
    if word.synonyms:
        synonyms = [models.Synonym(
            sanskrit_word_id = new_word.id,
            synonym = synonym
        ) for synonym in word.synonyms]
        db.add_all(synonyms)
    
    
    if word.antonyms:
        antonyms = [models.Antonym(
            sanskrit_word_id = new_word.id,
            antonym = antonym
        ) for antonym in word.antonyms]
        db.add_all(antonyms)
    
    db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Word created"})

@router.put("/")
def update_word(word: schemas.WordOut, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.id == word.id).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word with id {word.id} not found")
    
    
    db_word.sanskrit_word = word.sanskrit_word
    db_word.english_word = word.english_word

    if word.etymologies:
        db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == word.id).delete()

        etymologies = [models.Etymology(
            sanskrit_word_id = word.id,
            etymology = etymology
        ) for etymology in word.etymologies]
        
        db.add_all(etymologies)

    if word.derivations:
        db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == word.id).delete()

        derivations = [models.Derivation(
            sanskrit_word_id = word.id,
            derivation = derivation
        ) for derivation in word.derivations]
        
        db.add_all(derivations)


    if word.translation:
        db.query(models.Translation).filter(models.Translation.sanskrit_word_id == word.id).delete()

        translations = models.Translation(
            sanskrit_word_id = word.id,
            english_translation = word.translation.english_translation,
            kannada_translation = word.translation.kannada_translation,
            hindi_translation = word.translation.hindi_translation,
            detailedDescription = word.translation.detailedDescription,
        )
        
        db.add(translations)
    
    
    if word.reference_nyaya_texts:
        db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == word.id).delete()

        references = [models.ReferenceNyayaText(
            sanskrit_word_id = word.id,
            source = reference.source,
            description = reference.description
        ) for reference in word.reference_nyaya_texts]
        
        db.add_all(references)
    
    
    if word.synonyms:
        db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == word.id).delete()

        synonyms = [models.Synonym(
            sanskrit_word_id = word.id,
            synonym = synonym
        ) for synonym in word.synonyms]
        
        db.add_all(synonyms)
    
    
    if word.antonyms:
        db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == word.id).delete()
        
        antonyms = [models.Antonym(
            sanskrit_word_id = word.id,
            antonym = antonym
        ) for antonym in word.antonyms]
        
        db.add_all(antonyms)

    db.commit()
    db.refresh(db_word)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Word updated"})


@router.delete("/{word}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word(word: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_word == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")

    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id).delete(synchronize_session=False)
    db.query(models.SanskritWord).filter(models.SanskritWord.id == db_word.id).delete(synchronize_session=False)

    db.commit()