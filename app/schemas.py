from pydantic import BaseModel, EmailStr
from typing import List, Optional


class WordTranslation(BaseModel):
    english_translation: Optional[str] = None
    kannada_translation: Optional[str] = None
    hindi_translation: Optional[str] = None
    detailedDescription: Optional[str] = None


class NyayaTextReference(BaseModel):
    source: Optional[str] = None
    description: Optional[str] = None

class Word(BaseModel):
    sanskrit_word: str
    etymologies: Optional[List[str]] = None
    derivations: Optional[List[str]] = None
    translation: Optional[WordTranslation] = None
    reference_nyaya_texts: Optional[List[NyayaTextReference]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None


class WordOut(Word):
    id: int
    english_word: str


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