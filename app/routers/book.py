from pydantic import BaseModel
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi import status

from app.database.db import db_dependency, get_db
from app.models.book import Book
from app.routers.auth import get_current_user
from sqlalchemy.orm import Session

from datetime import date
from typing import Annotated

router = APIRouter(prefix="/books", tags=["Books"])
user_dependency = Annotated[dict, Depends(get_current_user)]

class BookCreate(BaseModel):
    title: str
    author: str
    published_date: date
    summary: str
    genre: str

class BookResponse(BookCreate):
    id: int

    class Config:
        form_attribute = True

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(user: user_dependency, db: db_dependency, book: BookCreate):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
def get_books(user: user_dependency, db: db_dependency, skip: int = Query(0, alias="page", ge=0), limit: int = Query(10, le=100)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    books = db.query(Book).offset(skip).limit(limit).all()
    return books

@router.get("/{id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def get_book(user: user_dependency, db: db_dependency, id: int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.put("/{id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def update_book(user: user_dependency, db: db_dependency, id: int, updated_book: BookCreate):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    for key, value in updated_book.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_book(user: user_dependency, db: db_dependency, id: int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    db.delete(book)
    db.commit()
    return {
            "message": "Book was deleted successfully"
        }
