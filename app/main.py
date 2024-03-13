from fastapi import FastAPI
import models
from database import engine
from routers import search, upload, words, auth, admins

models.Base.metadata.create_all(bind=engine)


with open("DESCRIPTION.md", "r") as f:
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