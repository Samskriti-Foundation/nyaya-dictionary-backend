from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
import app.models

client = TestClient(app)
