from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List
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

@router.get("/{id}")
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
    if current_user.is_superuser == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    

    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()

    if db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word already exists")
    
    new_word = models.SanskritWord(
        sanskrit_word = word.sanskrit_word,
        english_word = "hi"
    )
    db.add(new_word)
    db.flush()

    if word.etymology:
        for etymology in word.etymology:
            db.add(models.Etymology(
                sanskrit_word_id = new_word.id,
                etymology = etymology
            ))
    
    if word.derivation:
        for derivation in word.derivation:
            db.add(models.Derivation(
                sanskrit_word_id = new_word.id,
                derivation = derivation
            ))


    if word.translation:
        for translation in word.translation:
            db.add(models.Translation(
                sanskrit_word_id = new_word.id,
                english_translation = translation.english_translation,
                kannada_translation = translation.kannada_translation,
                hindi_translation = translation.hindi_translation,
                detailedDescription = translation.detailedDescription,
            ))
    
    
    if word.reference_nyaya_text:
        for reference in word.reference_nyaya_text:
            db.add(models.ReferenceNyayaText(
                sanskrit_word_id = new_word.id,
                source = reference.source,
                description = reference.description
            ))
    
    
    if word.synonyms:
        for synonym in word.synonyms:
            db.add(models.Synonym(
                sanskrit_word_id = new_word.id,
                synonym = synonym
            ))
    
    
    if word.antonyms:
        for antonym in word.antonyms:
            db.add(models.Antonym(
                sanskrit_word_id = new_word.id,
                antonym = antonym
            ))

    db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Word created"})

@router.put("/")
def update_word(word: schemas.WordOut, db: Session = Depends(get_db)):
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.id == word.id).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word with id {word.id} not found")
    
    db_word.sanskrit_word = word.sanskrit_word
    db_word.english_word = word.english_word

    if word.etymology:
        ety = db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == word.id).first()
        if ety:
            ety.etymology = word.etymology
        else:
            db.add(models.Etymology(
                sanskrit_word_id = word.id,
                etymology = word.etymology
            ))
        
    if word.derivation:
        der = db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == word.id).first()
        if der:
            der.derivation = word.derivation
        else:
            db.add(models.Derivation(
                sanskrit_word_id = word.id,
                derivation = word.derivation
            ))
    

    if word.translation:
        trans = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == word.id).first()
        if trans:
            trans.english_translation = word.english_translation
            trans.kannada_translation = word.kannada_translation
            trans.hindi_translation = word.hindi_translation
            trans.detailedDescription = word.detailedDescription
        else:
            db.add(models.Translation(
                sanskrit_word_id = word.id,
                english_translation = word.english_translation,
                kannada_translation = word.kannada_translation,
                hindi_translation = word.hindi_translation,
                detailedDescription = word.detailedDescription
            ))
    

    if word.reference_nyaya_text:
        ref = db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == word.id).first()
        if ref:
            ref.source = word.source
            ref.description = word.description
        else:
            db.add(models.ReferenceNyayaText(
                sanskrit_word_id = word.id,
                source = word.source,
                description = word.description
            ))
    

    if word.synonyms:
        syn = db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == word.id).first()
        if syn:
            syn.synonym = word.synonyms
        else:
            db.add(models.Synonym(
                sanskrit_word_id = word.id,
                synonym = word.synonyms
            ))

    
    if word.antonyms:
        ant = db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == word.id).first()
        if ant:
            ant.antonym = word.antonyms
        else:
            db.add(models.Antonym(
                sanskrit_word_id = word.id,
                antonym = word.antonyms
            ))

    db.commit()
    db.refresh(db_word)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Word updated"})


@router.delete("/{id}")
def delete_word(id: int, db: Session = Depends(get_db)):
    db.query(models.SanskritWord).filter(models.SanskritWord.id == id).delete()
    db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == id).delete()
    db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == id).delete()
    db.query(models.Translation).filter(models.Translation.sanskrit_word_id == id).delete()
    db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == id).delete()
    db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == id).delete()
    db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == id).delete()

    db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Word deleted"})