# Create tables
import app.database as _database
import app.schemas as _schemas
import app.models as _models
import app.queries as _queries

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
    
# Add new employees
async def create_employees(
    employees: List[_schemas.EmployeesCreate], db: Session
) -> _schemas.Employees:
    employee_objects = [_models.Employees(**employee.model_dump()) for employee in employees]
    db.add_all(employee_objects)
    db.commit()    
    
    # Refresh each individual object to update its state from the database
    for employee in employee_objects:
        db.refresh(employee)
    
    return [_schemas.Employees.model_validate(employee, from_attributes=True) for employee in employee_objects]

# Add new departments
async def create_departments(
    departments: List[_schemas.DepartmentCreate], db: Session
) -> _schemas.Department:
    departments_objects = [_models.Departments(**department.model_dump()) for department in departments]
    db.add_all(departments_objects)
    db.commit()    
    
    # Refresh each individual object to update its state from the database
    for department in departments_objects:
        db.refresh(department)
    
    return [_schemas.Department.model_validate(department, from_attributes=True) for department in departments_objects]

# Add new jobs
async def create_jobs(
    jobs: List[_schemas.JobCreate], db: Session
) -> _schemas.Department:
    jobs_objects = [_models.Jobs(**job.model_dump()) for job in jobs]
    db.add_all(jobs_objects)
    db.commit()    
    
    # Refresh each individual object to update its state from the database
    for job in jobs_objects:
        db.refresh(job)
    
    return [_schemas.Job.model_validate(job, from_attributes=True) for job in jobs_objects]

async def metric1(db: Session):
    sql_query = _queries.METRIC1_QUERY
    #result = await connection.fetch(query)
    data = db.execute(sql_query).fetchall()
    # Convert data into a list of dictionaries
    report_list = []
    for row in data:
        row_dict = {
            'department': row[0],
            'job': row[1],
            'Q1': row[2],
            'Q2': row[3],
            'Q3': row[4],
            'Q4': row[5]
        }
        report_list.append(row_dict)

    return report_list

async def metric2(db: Session):
    sql_query = _queries.METRIC2_QUERY
    #result = await connection.fetch(query)
    data = db.execute(sql_query).fetchall()
    # Convert data into a list of dictionaries
    report_list = []
    for row in data:
        row_dict = {
            'id': row[0],
            'department': row[1],
            'hired': row[2]
        }
        report_list.append(row_dict)

    return report_list