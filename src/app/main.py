from fastapi import FastAPI, Depends, status, UploadFile,File
import app.services as _services
import app.auth as _auth
import app.models as _models
import app.schemas as _schemas
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from typing import List
from sqlalchemy.orm import Session

app = FastAPI()

# Create tables
_services._add_tables()

@app.post('/api/auth/token', response_model=_schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(_services.get_db)):
    user = db.query(_models.User).filter(
        _models.User.email == user_credentials.username).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not _auth.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = _auth.create_access_token(data={"user_id": user.email})

    return {"access_token": access_token}

# Move historical data to hired_employees table
@app.post("/api/batch")
async def upload_file(
    file: UploadFile = File(...), 
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    return await _services.upload_csv_to_database(file=file, db=db)

# Add new data to hired_employees table
@app.post("/api/employees/", response_model=List[_schemas.Employees])
async def create_employees(
    employees: List[_schemas.EmployeesCreate],
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    if len(employees) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_employees(employees=employees, db=db)

# Add new data to department table
@app.post("/api/department/", response_model=List[_schemas.Department])
async def create_department(
    departments: List[_schemas.DepartmentCreate],
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    if len(departments) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_departments(departments=departments, db=db)

# Add new data to jobs table
@app.post("/api/jobs/", response_model=List[_schemas.Job])
async def create_jobs(
    jobs: List[_schemas.JobCreate],
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    if len(jobs) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_jobs(jobs=jobs, db=db)