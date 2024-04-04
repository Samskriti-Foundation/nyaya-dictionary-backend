from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict


class Translation(BaseModel):
    language: str
    translation: List[str]


class NyayaTextReference(BaseModel):
    source: str
    description: Optional[str] = None


class Example(BaseModel):
    example_sentence: str
    applicable_modern_context: Optional[str] = None


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
    meanings: List[Meaning]


class WordOut(Word):
    id: int
    meanings: List[MeaningOut]


class WordUpdate(Word):
    id: int
    meanings: List[MeaningUpdate]


class AdminBase(BaseModel):
    email: EmailStr 
    password: str
    first_name: str
    last_name: str


class AdminOut(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool


class AdminUpdate(BaseModel):
    email: EmailStr | None
    first_name: str | None
    last_name: str | None


class AdminUpdatePassword(BaseModel):
    current_password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr