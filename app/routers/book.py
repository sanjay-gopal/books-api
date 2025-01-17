from pydantic import BaseModel
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi import status

from sqlalchemy.orm import Session
from app.database.db import get_db

from app.models.book import Book
from app.routers.auth import get_current_user
from datetime import date
from typing import Annotated

router = APIRouter(prefix="/books", tags=["Books"])
user_dependency = Annotated[str, Depends(get_current_user)]
class BookCreate(BaseModel):
    title: str
    author: str
    published_date: date
    summary: str
    genre: str

class BookResponse(BookCreate):
    id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookResponse])
def get_books(skip: int = Query(0, alias="page", ge=0), limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books

@router.get("/{id}", response_model=BookResponse)
def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{id}", response_model=BookResponse)
def update_book(id: int, updated_book: BookCreate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in updated_book.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{id}")
def delete_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}
