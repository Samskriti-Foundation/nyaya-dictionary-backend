from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import db_managers, search, upload, auth, word_nyaya_text_references, words, word_antonyms, word_derivations, word_etymologies, word_synonyms, word_translations, word_examples, word_meaning, logs
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

with open("app/DESCRIPTION.md", "r") as f:
    description = f.read()

app = FastAPI(
    title="Nyaya Khosha",
    description=description,
)

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

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(db_managers.router)
app.include_router(search.router)
app.include_router(upload.router)
app.include_router(logs.router)
app.include_router(words.router)
app.include_router(word_meaning.router)
app.include_router(word_etymologies.router)
app.include_router(word_derivations.router)
app.include_router(word_translations.router)
app.include_router(word_nyaya_text_references.router)
app.include_router(word_examples.router)
app.include_router(word_synonyms.router)
app.include_router(word_antonyms.router)