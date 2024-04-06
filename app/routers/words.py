from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from typing import List
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from app.utils.converter import access_to_int
from app.utils.lang import isDevanagariWord
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
        word = {}

        word["id"] = db_word.id
        word["sanskrit_word"] = db_word.sanskrit_word
        word["english_transliteration"] = db_word.english_transliteration

        meaning_ids = [x.id for x in db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id).all()]
        word["meanings"] = []


        for meaning_id in meaning_ids:
            meaning = {}

            meaning["meaning_id"] = meaning_id
            
            meaning["meaning"] = db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id, models.Meaning.id == meaning_id).first().meaning

            meaning["etymologies"] = [x.etymology for x in db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id).all()]

            meaning["derivations"] = [x.derivation for x in db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id).all()]
            
            meaning["translations"] = [x.translation for x in db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).all()]
            
            meaning["examples"] = [x.example_sentence for x in db.query(models.Example).filter(models.Example.sanskrit_word_id == db_word.id, models.Example.meaning_id == meaning_id).all()]

            translation_query = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).all()
            
            translations = {}
            for translation in translation_query:
                translations.setdefault(translation.language, []).append(translation.translation)
            meaning["translations"] = translations
        
            meaning["nyaya_reference_texts"] = [{
                "source": x.source,
                "description": x.description
            } for x in db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id).all()]
            
            meaning["synonyms"] = [x.synonym for x in db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, meaning_id == models.Synonym.meaning_id).all()]
            meaning["antonyms"] = [x.antonym for x in db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, meaning_id == models.Antonym.meaning_id).all()]

            word["meanings"].append(meaning)

        words.append(word)

    return words

@router.get("/{word}", response_model=schemas.WordOut)
def get_word(word: str, db: Session = Depends(get_db)):
    if isDevanagariWord(word):
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word).first()
    else:
        db_word = db.query(models.SanskritWord).filter(models.SanskritWord.english_transliteration == word).first()

    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word - {word} not found")
    
    word = {}

    word["id"] = db_word.id
    word["sanskrit_word"] = db_word.sanskrit_word
    word["english_transliteration"] = db_word.english_transliteration

    meaning_ids = [x.id for x in db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id).all()]
    word["meanings"] = []


    for meaning_id in meaning_ids:
        meaning = {}

        meaning["meaning_id"] = meaning_id

        meaning["meaning"] = db.query(models.Meaning).filter(models.Meaning.sanskrit_word_id == db_word.id, models.Meaning.id == meaning_id).first().meaning

        meaning["etymologies"] = [x.etymology for x in db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == db_word.id, models.Etymology.meaning_id == meaning_id).all()]

        meaning["derivations"] = [x.derivation for x in db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == db_word.id, models.Derivation.meaning_id == meaning_id).all()]
        
        meaning["translations"] = [x.translation for x in db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).all()]
        
        meaning["examples"] = [x.example_sentence for x in db.query(models.Example).filter(models.Example.sanskrit_word_id == db_word.id, models.Example.meaning_id == meaning_id).all()]

        translation_query = db.query(models.Translation).filter(models.Translation.sanskrit_word_id == db_word.id, models.Translation.meaning_id == meaning_id).all()
        
        translations = {}
        for translation in translation_query:
            translations.setdefault(translation.language, []).append(translation.translation)
        meaning["translations"] = translations
    
        meaning["nyaya_reference_texts"] = [{
            "source": x.source,
            "description": x.description
        } for x in db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == db_word.id, models.ReferenceNyayaText.meaning_id == meaning_id).all()]
        
        meaning["synonyms"] = [x.synonym for x in db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == db_word.id, meaning_id == models.Synonym.meaning_id).all()]
        meaning["antonyms"] = [x.antonym for x in db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == db_word.id, meaning_id == models.Antonym.meaning_id).all()]

        word["meanings"].append(meaning)
    
    return word

@router.post("/")
def create_word(word: schemas.Word, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()

    if db_word:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Word already exists")

    if not isDevanagariWord(word.sanskrit_word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word is not in Devanagari")
    
    new_word = models.SanskritWord(
        sanskrit_word = word.sanskrit_word,
        english_transliteration = word.english_transliteration if word.english_transliteration else transliterate(word.sanskrit_word, sanscript.DEVANAGARI, sanscript.HK),
    )
    db.add(new_word)
    db.flush()


    for meaning in word.meanings:
        new_meaning = models.Meaning(
            sanskrit_word_id = new_word.id,
            meaning = meaning.meaning
        )
        db.add(new_meaning)
        db.flush()


        if meaning.etymologies:
            etymologies = [models.Etymology(
                sanskrit_word_id = new_word.id,
                meaning_id = new_meaning.id,
                etymology = etymology
            ) for etymology in meaning.etymologies]
            db.add_all(etymologies)


        if meaning.derivations:
            derivations = [models.Derivation(
                sanskrit_word_id = new_word.id,
                meaning_id = new_meaning.id,
                derivation = derivation
            ) for derivation in meaning.derivations]
            db.add_all(derivations)


        if meaning.translations:
            translations = [models.Translation(
                sanskrit_word_id=new_word.id,
                meaning_id=new_meaning.id,
                language=translation.language,
                translation=tran
            ) for translation in meaning.translations for tran in translation.translation]
            db.add_all(translations)
        
        
        if meaning.reference_nyaya_texts:
            references = [models.ReferenceNyayaText(
                sanskrit_word_id = new_word.id,
                meaning_id = new_meaning.id,
                source = reference.source,
                description = reference.description
            ) for reference in meaning.reference_nyaya_texts]
            db.add_all(references)
        
        
        if meaning.synonyms:
            synonyms = [models.Synonym(
                sanskrit_word_id = new_word.id,
                meaning_id = new_meaning.id,
                synonym = synonym
            ) for synonym in meaning.synonyms]
            db.add_all(synonyms)
        
        
        if meaning.antonyms:
            antonyms = [models.Antonym(
                sanskrit_word_id = new_word.id,
                meaning_id = new_meaning.id,
                antonym = antonym
            ) for antonym in meaning.antonyms]
            db.add_all(antonyms)
    
    db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Word created"})

@router.put("/")
def update_word(word: schemas.WordUpdate, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager)):
    if access_to_int(current_db_manager.access) < access_to_int(schemas.Access.READ_WRITE_MODIFY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if not isDevanagariWord(word.sanskrit_word):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word is not in Devanagari")
    
    db_word = db.query(models.SanskritWord).filter(models.SanskritWord.sanskrit_word == word.sanskrit_word).first()
    
    if not db_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word not found")
    
    if word.id != db_word.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid word ID")
    
    db_word.sanskrit_word = word.sanskrit_word
    db_word.english_transliteration = word.english_transliteration


    for meaning in word.meanings:
        if meaning.etymologies:
            db.query(models.Etymology).filter(models.Etymology.sanskrit_word_id == word.id, models.Etymology.meaning_id == meaning.meaning_id).delete()

            etymologies = [models.Etymology(
                sanskrit_word_id = word.id,
                meaning_id = meaning.meaning_id,
                etymology = etymology
            ) for etymology in meaning.etymologies]
            
            db.add_all(etymologies)
        

        if meaning.derivations:
            db.query(models.Derivation).filter(models.Derivation.sanskrit_word_id == word.id, models.Derivation.meaning_id == meaning.meaning_id).delete()

            derivations = [models.Derivation(
                sanskrit_word_id = word.id,
                meaning_id = meaning.meaning_id,
                derivation = derivation
            ) for derivation in meaning.derivations]
            
            db.add_all(derivations)
        

        if meaning.translations:
            db.query(models.Translation).filter(models.Translation.sanskrit_word_id == word.id, models.Translation.meaning_id == meaning.meaning_id).delete()

            translations = [models.Translation(
                sanskrit_word_id = word.id,
                meaning_id = meaning.meaning_id,
                language = translation.language,
                translation = tran
            ) for translation in meaning.translations for tran in translation.translation]
            
            db.add_all(translations)


        if meaning.reference_nyaya_texts:
            db.query(models.ReferenceNyayaText).filter(models.ReferenceNyayaText.sanskrit_word_id == word.id, models.ReferenceNyayaText.meaning_id == meaning.meaning_id).delete()

            references = [models.ReferenceNyayaText(
                sanskrit_word_id = word.id,
                meaning_id = meaning.meaning_id,
                source = reference.source,
                description = reference.description
            ) for reference in meaning.reference_nyaya_texts]
            
            db.add_all(references)
        

        if meaning.examples:
            db.query(models.Example).filter(models.Example.sanskrit_word_id == word.id, models.Example.meaning_id == meaning.meaning_id).delete()

            examples = [models.Example(
                sanskrit_word_id = word.id,
                meaning_id = meaning.meaning_id,
                example = example.example_sentence,
                applicable_modern_context = example.applicable_modern_context
            ) for example in meaning.examples]
            
            db.add_all(examples)

        
        if meaning.synonyms:
            db.query(models.Synonym).filter(models.Synonym.sanskrit_word_id == word.id).delete()

            synonyms = [models.Synonym(
                sanskrit_word_id = word.id,
                meaning_id = meaning.meaning_id,
                synonym = synonym
            ) for synonym in meaning.synonyms]
            
            db.add_all(synonyms)
        
        
        if meaning.antonyms:
            db.query(models.Antonym).filter(models.Antonym.sanskrit_word_id == word.id).delete()
            
            antonyms = [models.Antonym(
                sanskrit_word_id = word.id,
                meaning_id = meaning.meaning_id,
                antonym = antonym
            ) for antonym in meaning.antonyms]
            
            db.add_all(antonyms)

    db.commit()
    db.refresh(db_word)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Word updated"})


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