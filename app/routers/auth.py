from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from sqlalchemy.orm import Mapped

from sqlalchemy.orm import Session
from app.database.db import get_db, db_dependency

from app.models.user import User

from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from typing import Annotated
import app.core.settings as config

from datetime import datetime, timedelta
from starlette import status

router = APIRouter(prefix="/auth", tags=["Auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRequest(BaseModel):
    username: str
    password: str

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(password, hashed_password):
    return crypt_context.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, create_user_request: UserRequest):
    create_user = User(
        username=create_user_request.username,
        password_hash=crypt_context.hash(create_user_request.password)
    )
    db.add(create_user)
    db.commit()

@router.post("/token", response_model=Token)
def login_to_access(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_user(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials were given")
    access_token = create_access_token(
            data={
                "sub": user.username
            }
        )
    return {
            "access_token": access_token, 
            "token_type": "bearer"
        }

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        current_user = payload.get('sub')
        print("This is current user")
        print(current_user)
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to validate user")
        return {
            'username': current_user
        }
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to validate user")
    
# @router.post('/token', response_model=Token)
# def login_for_access(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
#     user = auth_user(form_data.username, form_data.password, db)
#     if not user:




# def auth_user(username, password, db):
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         return False
#     verify_user = crypt_context.verify(password, user.password_hash)
#     print("----------Verify User---------------")
#     print(verify_user)
#     if not verify_user:
#         return False
#     return user
