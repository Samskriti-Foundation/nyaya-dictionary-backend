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

@router.get("/{id}", response_model=schemas.WordOut)
def get_word(id: int, db: Session = Depends(get_db)):
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.id == id).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word with id {id} not found")
    
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

    if word.etymology:
        etymologies = [models.Etymology(
            sanskrit_word_id = new_word.id,
            etymology = etymology
        ) for etymology in word.etymology]
        db.add_all(etymologies)

    if word.derivation:
        derivations = [models.Derivation(
            sanskrit_word_id = new_word.id,
            derivation = derivation
        ) for derivation in word.derivation]
        db.add_all(derivations)


    if word.translation:
        translations = [models.Translation(
            sanskrit_word_id = new_word.id,
            english_translation = translation.english_translation,
            kannada_translation = translation.kannada_translation,
            hindi_translation = translation.hindi_translation,
            detailedDescription = translation.detailedDescription,
        ) for translation in word.translation]
        db.add_all(translations)
    
    
    if word.reference_nyaya_text:
        references = [models.ReferenceNyayaText(
            sanskrit_word_id = new_word.id,
            source = reference.source,
            description = reference.description
        ) for reference in word.reference_nyaya_text]
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

    if word.etymology:
        db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == word.id).delete()

        etymologies = [models.Etymology(
            sanskrit_word_id = word.id,
            etymology = etymology
        ) for etymology in word.etymology]
        
        db.add_all(etymologies)

    if word.derivation:
        db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == word.id).delete()

        derivations = [models.Derivation(
            sanskrit_word_id = word.id,
            derivation = derivation
        ) for derivation in word.derivation]
        
        db.add_all(derivations)


    if word.translation:
        db.query(models.Translation).filter(models.Translation.sanskrit_word_id == word.id).delete()

        translations = [models.Translation(
            sanskrit_word_id = word.id,
            english_translation = translation.english_translation,
            kannada_translation = translation.kannada_translation,
            hindi_translation = translation.hindi_translation,
            detailedDescription = translation.detailedDescription,
        ) for translation in word.translation]
        
        db.add_all(translations)
    
    
    if word.reference_nyaya_text:
        db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == word.id).delete()

        references = [models.ReferenceNyayaText(
            sanskrit_word_id = word.id,
            source = reference.source,
            description = reference.description
        ) for reference in word.reference_nyaya_text]
        
        db.add_all(references)
    
    
    if word.synonyms:
        synonyms = [models.Synonym(
            sanskrit_word_id = word.id,
            synonym = synonym
        ) for synonym in word.synonyms]
        db.add_all(synonyms)
    
    
    if word.antonyms:
        antonyms = [models.Antonym(
            sanskrit_word_id = word.id,
            antonym = antonym
        ) for antonym in word.antonyms]
        db.add_all(antonyms)

    db.commit()
    db.refresh(db_word)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Word updated"})


@router.delete("/{id}")
def delete_word(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.id == id).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word with id {id} not found")

    db.query(models.SanskritWord).filter(models.SanskritWord.id == id).delete()
    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == id).delete()
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == id).delete()
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == id).delete()
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == id).delete()
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == id).delete()
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == id).delete()

    db.commit()

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Word deleted"})