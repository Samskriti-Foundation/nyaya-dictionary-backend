from fastapi import FastAPI
from . import models
from app.database import engine
from app.routers import db_managers, search, upload, words, auth
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