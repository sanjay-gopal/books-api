from sqlalchemy import create_engine
from fastapi import Depends, HTTPException
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from sqlalchemy.exc import OperationalError, DisconnectionError
from starlette import status

DATABASE_URL = "sqlite:///./app/database/books.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db

    except OperationalError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while connecting to the daatabase. Please try again later")
    
    except DisconnectionError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lost database connection. Please try again later.")
    
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]