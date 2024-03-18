from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
import pandas as pd
from app import models
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


def checkFileTypeAndReturnDataFrame(file: UploadFile) -> pd.DataFrame | None:
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. Only CSV and Excel files are allowed.",
        )
    return df


columns = {
    "technicalTermDevanagiri",
    "technicalTermRoman",
    "etymology",
    "derivation",
    "source",
    "description",
    "translation",
    "detailedDescription",
    "example_sentence",
    "applicableModernContext",
    "synonyms",
    "antonyms",
    }


def checkIfColumnsMatch(columns, df):
    if not columns.issubset(df.columns):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column names do not match. Please check the file and try again.",
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = checkFileTypeAndReturnDataFrame(file)
        checkIfColumnsMatch(columns, df)

        for _, row in df.iterrows():
            word = models.SanskritWord(
                technicalTermDevanagiri=row["technicalTermDevanagiri"],
                technicalTermRoman=row["technicalTermRoman"],
                etymology=row["etymology"],
                derivation=row["derivation"],
            )

            existing_word = db.query(models.SanskritWord).filter(
                models.SanskritWord.technicalTermDevanagiri == word.technicalTermDevanagiri
            ).first()

            if existing_word:
                # Update existing word with new information
                existing_word.technicalTermRoman = word.technicalTermRoman
                existing_word.etymology = word.etymology
                existing_word.derivation = word.derivation

            else:
                # Word doesn't exist, insert it
                db.add(word)
                db.flush()
                existing_word = word  # Set existing_word to the newly inserted word

            # Update or insert synonyms
            synonyms = row["synonyms"].split(" ")
            synonyms = [synonym.strip() for synonym in synonyms]

            existing_synonyms = db.query(models.Synonym).filter(
                models.Synonym.sanskrit_word_id == existing_word.id
            ).all()

            for synonym in existing_synonyms:
                if synonym.synonym not in synonyms:
                    db.delete(synonym)

            for new_synonym in synonyms:
                if new_synonym:
                    synonym = models.Synonym(
                        sanskrit_word_id=existing_word.id,
                        synonym=new_synonym
                    )
                    db.add(synonym)

            # Update or insert antonyms
            antonyms = row["antonyms"].split(",")
            antonyms = [antonym.strip() for antonym in antonyms]

            existing_antonyms = db.query(models.Antonym).filter(
                models.Antonym.sanskrit_word_id == existing_word.id
            ).all()

            for antonym in existing_antonyms:
                if antonym.antonym not in antonyms:
                    db.delete(antonym)

            for new_antonym in antonyms:
                if new_antonym:
                    antonym = models.Antonym(
                        sanskrit_word_id=existing_word.id,
                        antonym=new_antonym
                    )
                    db.add(antonym)

           # Update or insert translation
            translation = row["translation"].strip()
            existing_translation = db.query(models.EnglishTranslation).filter(
                models.EnglishTranslation.sanskrit_word_id == existing_word.id
            ).first()

            if existing_translation:
                existing_translation.translation = translation
            else:
                new_translation = models.EnglishTranslation(
                    sanskrit_word_id=existing_word.id,
                    translation=translation,
                    detailedDescription=row["detailedDescription"]
                )
                db.add(new_translation)

            # Update or insert example
            example = row["example_sentence"].strip()
            existing_example = db.query(models.Example).filter(
                models.Example.sanskrit_word_id == existing_word.id
            ).first()

            if existing_example:
                existing_example.example_sentence = example
            else:
                new_example = models.Example(
                    sanskrit_word_id=existing_word.id,
                    example_sentence=example,
                    applicableModernContext=row["applicableModernContext"]
                )
                db.add(new_example)

            # Update or insert nyaya text
            existing_nyaya_text = db.query(models.ReferenceNyayaText).filter(
                models.ReferenceNyayaText.sanskrit_word_id == existing_word.id
            ).first()

            if existing_nyaya_text:
                existing_nyaya_text.source = row["source"]
                existing_nyaya_text.description = row["description"]
            else:
                new_nyaya_text = models.ReferenceNyayaText(
                    sanskrit_word_id=existing_word.id,
                    source=row["source"],
                    description=row["description"]
                )
                db.add(new_nyaya_text)

        db.commit()
        return {"message": "Data uploaded successfully"}

    except Exception as e:
        db.rollback()
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading data: {str(e)} Please check the file and try again.",
        )