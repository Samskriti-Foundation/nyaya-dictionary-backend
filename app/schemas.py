from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict


class WordTranslation(BaseModel):
    language: str
    translation: List[str]


class NyayaTextReference(BaseModel):
    source: Optional[str] = None
    description: Optional[str] = None

class Word(BaseModel):
    sanskrit_word: str
    english_transliteration: str | None
    etymologies: Optional[List[str]] = None
    derivations: Optional[List[str]] = None
    translations: Optional[List[WordTranslation]] = None
    detailed_description: Optional[str] = None
    reference_nyaya_texts: Optional[List[NyayaTextReference]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None


class WordOut(Word):
    id: int
    translations: Dict[str, List[str]]


class WordUpdate(WordOut):
    translations: Optional[List[WordTranslation]] = None


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