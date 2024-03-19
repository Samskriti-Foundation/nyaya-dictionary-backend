from sqlalchemy import Column,Integer, String, DateTime, ForeignKey, Boolean
from .database import Base
from datetime import datetime, UTC

class SanskritWord(Base):
    __tablename__ = "sanskrit_words"

    id = Column(Integer, primary_key=True, index=True)
    technicalTermDevanagiri = Column(String, index=True)
    technicalTermRoman = Column(String, index=True)
    etymology = Column(String)
    derivation = Column(String)



class EnglishTranslation(Base):
    __tablename__ = "english_translations"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    translation = Column(String)
    detailedDescription = Column(String)


class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    example_sentence = Column(String)
    applicableModernContext = Column(String)


class ReferenceNyayaText(Base):
    __tablename__ = "reference_nyaya_texts"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    source = Column(String)
    description = Column(String)


class Synonym(Base):
    __tablename__ = "synonyms"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    synonym = Column(String)


class Antonym(Base):
    __tablename__ = "antonyms"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    antonym = Column(String)



class Admin(Base):
    __tablename__ = "admins"

    email = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(UTC))