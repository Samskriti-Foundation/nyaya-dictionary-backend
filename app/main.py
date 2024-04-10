from fastapi import FastAPI
from . import models
from app.database import engine
from app.routers import db_managers, search, upload, auth, words, word_antonyms, word_derivations, word_etymologies, word_synonyms, word_translations, word_examples, word_reference_nyaya_texts, word_meaning
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.logger_middleware import log_database_operations, log_login_operations

models.Base.metadata.create_all(bind=engine)

with open("app/DESCRIPTION.md", "r") as f:
    description = f.read()

app = FastAPI(
    title="Nyaya Khosha",
    description=description,
)

app.add_middleware(BaseHTTPMiddleware, dispatch=log_database_operations)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_login_operations)


origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(db_managers.router)
app.include_router(search.router)
app.include_router(upload.router)
app.include_router(words.router)
app.include_router(word_meaning.router)
app.include_router(word_etymologies.router)
app.include_router(word_derivations.router)
app.include_router(word_translations.router)
app.include_router(word_reference_nyaya_texts.router)
app.include_router(word_examples.router)
app.include_router(word_antonyms.router)
app.include_router(word_synonyms.router)