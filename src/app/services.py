# Create tables
import app.database as _database
import app.schemas as _schemas
import app.models as _models
from sqlalchemy.orm import Session
from typing import List

def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)

# Database Session
def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()