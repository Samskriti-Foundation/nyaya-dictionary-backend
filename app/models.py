from sqlalchemy import Column,Integer, String, DateTime, ForeignKey, Enum
from .database import Base
from datetime import datetime, UTC

class SanskritWord(Base):
    __tablename__ = "sanskrit_words"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word = Column(String, index=True, unique=True)
    english_transliteration = Column(String, index=True)


class Meaning(Base):
    __tablename__ = "meanings"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning = Column(String, nullable=False)


class Etymology(Base):
    __tablename__ = "etymologies"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning_id = Column(Integer, ForeignKey("meanings.id"))
    etymology = Column(String)


class Derivation(Base):
    __tablename__ = "derivations"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning_id = Column(Integer, ForeignKey("meanings.id"))
    derivation = Column(String)


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning_id = Column(Integer, ForeignKey("meanings.id"))
    translation = Column(String, nullable=False)
    language = Column(String, nullable=False)


class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning_id = Column(Integer, ForeignKey("meanings.id"))
    example_sentence = Column(String)
    applicable_modern_context = Column(String)


class ReferenceNyayaText(Base):
    __tablename__ = "reference_nyaya_texts"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning_id = Column(Integer, ForeignKey("meanings.id"))
    source = Column(String)
    description = Column(String)


class Synonym(Base):
    __tablename__ = "synonyms"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning_id = Column(Integer, ForeignKey("meanings.id"))
    synonym = Column(String)


class Antonym(Base):
    __tablename__ = "antonyms"

    id = Column(Integer, primary_key=True, index=True)
    sanskrit_word_id = Column(Integer, ForeignKey("sanskrit_words.id"))
    meaning_id = Column(Integer, ForeignKey("meanings.id"))
    antonym = Column(String)



class DBManagers(Base):
    __tablename__ = "db_managers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(Enum("superuser", "admin", "editor"), default="editor")
    access_token = Column(Enum("READ_ONLY", "READ_WRITE", "READ_WRITE_MODIFY", "ALL"), default="READ_ONLY")
    created_at = Column(DateTime, default=datetime.now(UTC))


class DatabaseAudit(Base):
    __tablename__ = "database_audits"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    record_id = Column(Integer, nullable=False)
    operation = Column(String, nullable=False)
    db_manager_id = Column(Integer, ForeignKey("db_managers.id"))
    timestamp = Column(DateTime, default=datetime.now(UTC))
    new_value = Column(String, nullable=False)


class LoginAudit(Base):
    __tablename__ = "login_audits"

    id = Column(Integer, primary_key=True, index=True)
    db_manager_id = Column(Integer, ForeignKey("db_managers.id"))
    ip_address = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(UTC))


# class AdminAudit(Base):
#     __tablename__ = "admin_audits"

#     id = Column(Integer, primary_key=True, index=True)