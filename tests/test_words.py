from fastapi.testclient import TestClient
from main import app
from database import get_db
import models

client = TestClient(app)
