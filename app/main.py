from fastapi import FastAPI
import app.models
from app.database import engine
from app.routers import search, upload, words, auth, admins
from fastapi.middleware.cors import CORSMiddleware

app.models.Base.metadata.create_all(bind=engine)


with open("app/DESCRIPTION.md", "r") as f:
    description = f.read()

app = FastAPI(
    title="Nyaya Dictionary",
    description=description,
)


origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(search.router)
app.include_router(upload.router)
app.include_router(words.router)