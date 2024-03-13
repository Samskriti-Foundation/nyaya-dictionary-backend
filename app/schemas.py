from pydantic import BaseModel, EmailStr


class WordBase(BaseModel):
    technicalTermDevanagiri: str
    technicalTermRoman: str
    etymology: str | None = None
    derivation: str | None = None
    source: str | None = None
    description: str | None = None
    translation: str | None = None
    detailedDescription: str 

class WordOut(WordBase):
    id: int


class AdminBase(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class AdminOut(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr