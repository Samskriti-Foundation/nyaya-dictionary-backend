from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import schemas, models, oauth2
from app.utils import encrypt
from app.database import get_db
from app.middleware import auth_middleware

router = APIRouter(
    prefix='/logs',
    tags=['Logs']
    )