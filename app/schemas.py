from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from enum import Enum


class Etymology(BaseModel):
    sanskrit_word_id: int
    meaning_id: int
    etymology: str


class EtymologyOut(Etymology):
    id: int


class Derivation(BaseModel):
    sanskrit_word_id: int
    meaning_id: int
    derivation: str


class DerivationOut(Derivation):
    id: int


class Translation(BaseModel):
    language: str
    translation: List[str]


class TranslationOut(Translation):
    id: int


class NyayaTextReference(BaseModel):
    source: str
    description: Optional[str] = None


class NyayaTextReferenceOut(NyayaTextReference):
    id: int


class Example(BaseModel):
    example_sentence: str
    applicable_modern_context: Optional[str] = None


class ExampleOut(Example):
    id: int


class Meaning(BaseModel):
    meaning: str
    etymologies: Optional[List[str]] = None
    derivations: Optional[List[str]] = None
    translations: Optional[List[Translation]] = None
    reference_nyaya_texts: Optional[List[NyayaTextReference]] = None
    examples: Optional[List[Example]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None


class MeaningOut(Meaning):
    meaning_id: int
    translations: Dict[str, List[str]]


class MeaningUpdate(Meaning):
    meaning_id: int
    translations: Optional[List[Translation]] = None


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

class WordUpdate(Word):
    id: int
    meanings: List[MeaningUpdate]


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
    password: str


class DBManagerOut(DBManager):
    pass


class DBManagerUpdate(DBManager):
    pass


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr