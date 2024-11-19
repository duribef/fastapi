# Create tables
import app.database as _database
import app.schemas as _schemas
import app.models as _models
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from sqlalchemy import text

from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import HTTPException

def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)

# Database Session
def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Batch upload
async def upload_csv_to_database(file, db: Session):
    table_name = file.filename.replace('.csv','')
    try:
        # Get column names
        if table_name == 'hired_employees':
            model = _models.Employees()
        elif table_name == 'jobs':
            model = _models.Jobs()
        elif table_name == 'departments':
            model = _models.Departments()

        column_names = [column.name for column in model.__table__.columns]
        
        # Read CSV data into a DataFrame
        df = pd.read_csv(file.file, header=None)
        df.columns = column_names
        
        db.begin()
        # Upload data into the database
        df.to_sql(table_name, db.get_bind(), if_exists="append", index=False)
        # Commit the transaction
        db.execute(text(f"SELECT setval('{table_name}_id_seq', max(id)) FROM {table_name};"))
        db.commit()
        return {"message": f"Table {table_name} uploaded successfully"}
        
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="IntegrityError: Duplicate entry")