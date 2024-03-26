from sqlalchemy import Column,Integer, String, DateTime, ForeignKey, Boolean
from .database import Base
from datetime import datetime, UTC

class SanskritWord(Base):
    __tablename__ = "sanskrit_words"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word = Column(String, index=True, unique=True)
    english_word = Column(String, index=True)


class Etymology(Base):
    __tablename__ = "etymologies"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    etymology = Column(String)


class Derivation(Base):
    __tablename__ = "derivations"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    derivation = Column(String)


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    translation = Column(String, nullable=False)
    language = Column(String, nullable=False)


class Description(Base):
    __tablename__ = "descriptions"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    description = Column(String, nullable=False)

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