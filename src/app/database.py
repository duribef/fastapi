import os
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import sqlalchemy.ext.declarative as _declarative
from google.cloud.sql.connector import Connector
from sqlalchemy.engine import Engine

def init_connection_engine() -> Engine:
    env = os.getenv("APP_ENV", "dev")  # Default to development if not set
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS", "")
    db_name = os.getenv("DB_NAME")
    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")

    # Use Cloud SQL Connector
    connector = Connector()
    
    def getconn():
        return connector.connect(
            instance_connection_name,
            "pg8000",
            user=user,
            password=password,
            db=db_name
        )

    database_url = "postgresql+pg8000://"
    engine = _sql.create_engine(database_url, creator=getconn)

    return engine


engine = init_connection_engine()
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = _declarative.declarative_base()