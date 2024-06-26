from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime


class Meaning(BaseModel):
    sanskrit_word_id: int
    meaning: str
    

class MeaningOut(Meaning):
    id: int


class MeaningCreate(BaseModel):
    meaning: str


class Etymology(BaseModel):
    etymology: str


class EtymologyOut(Etymology):
    sanskrit_word_id: int
    meaning_id: int
    id: int


class Derivation(BaseModel):
    derivation: str


class DerivationOut(Derivation):
    id: int
    sanskrit_word_id: int
    meaning_id: int


class Translation(BaseModel):
    language: str
    translation: str


class TranslationOut(Translation):
    id: int
    sanskrit_word_id: int
    meaning_id: int


class NyayaTextReference(BaseModel):
    source: str
    description: Optional[str] = None


class NyayaTextReferenceOut(NyayaTextReference):
    id: int
    sanskrit_word_id: int
    meaning_id: int


class Example(BaseModel):
    example_sentence: str
    applicable_modern_context: Optional[str] = None


class ExampleOut(Example):
    id: int
    sanskrit_word_id: int
    meaning_id: int


class Synonym(BaseModel):
    synonym: str


class SynonymOut(Synonym):
    id: int
    sanskrit_word_id: int
    meaning_id: int


class Antonym(BaseModel):
    antonym: str


class AntonymOut(Antonym):
    id: int
    sanskrit_word_id: int
    meaning_id: int


class Word(BaseModel):
    sanskrit_word: str
    english_transliteration: Optional[str] = None
    meaning_ids: Optional[List[int]] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.meaning_ids is None:
            self.meaning_ids = []


class WordOut(Word):
    id: int


class WordCreate(BaseModel):
    sanskrit_word: str
    english_transliteration: Optional[str] = None


class WordUpdate(BaseModel):
    sanskrit_word: Optional[str] = None
    english_transliteration: Optional[str] = None


class Role(str, Enum):
    SUPERUSER = "SUPERUSER"
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"


class Access(str, Enum):
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"
    READ_WRITE_MODIFY = "READ_WRITE_MODIFY"
    ALL = "ALL"


class DBManager(BaseModel):
    email: EmailStr 
    first_name: str
    last_name: str
    role: Role = Role.EDITOR
    access: Access = Access.READ_ONLY


class DBManagerIn(DBManager):
    password: str | bytes


class DBManagerOut(DBManager):
    pass


class DBManagerUpdate(DBManager):
    pass


class PasswordUpdate(BaseModel):
    current_password: str | bytes
    new_password: str | bytes


class DBLog(BaseModel):
    timestamp: datetime
    table_name: str
    record_id: int
    operation: str
    db_manager_email: str
    affected_value: str


class AuthLog(BaseModel):
    timestamp: datetime
    client_ip: str
    db_manager_email: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    email: EmailStr
    role: Role
    access: Access