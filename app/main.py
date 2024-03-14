from fastapi import FastAPI
import app.models
from app.database import engine
from app.routers import search, upload, words, auth, admins

app.models.Base.metadata.create_all(bind=engine)


with open("app/DESCRIPTION.md", "r") as f:
    description = f.read()

app = FastAPI(
    title="Nyaya Dictionary",
    description=description,
)

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(search.router)
app.include_router(upload.router)
app.include_router(words.router)