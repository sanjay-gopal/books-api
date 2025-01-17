from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi import status

from app.database.db import db_dependency
from app.models.book import Book
from app.routers.auth import get_current_user

from typing import Annotated
from app.scheme.Book import BookCreate, BookResponse

events_queue: List[str] = []

router = APIRouter(prefix="/books", tags=["Books"])

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/", summary="Create a new book", description="Create a new book by providing Title, Author, Published Date, Summary, and Genere", 
             response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(user: user_dependency, db: db_dependency, book: BookCreate):
    """
    Create a new book with the below fields by passing it in the request body
    title:          Title of the book
    author:         Author of the book
    published_date: Published date of the book
    summary:        Summary of the book
    genre:          Genere of the book
    """
    try:
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        events_queue.append(f"New book was created")
        return db_book
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while processing the request. Please try again later.")

@router.get("/", summary="Retrieve books", description="Retrieve books by providing limit",
            response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_books(user: user_dependency, db: db_dependency, skip: int = Query(0, alias="page", ge=0), limit: int = Query(10, le=100)):
    """
    Retrieve the books based on below query parameter
    page: value should greater than or equal to 0
    limit: defalted to 10 and can be less than or equal to 100
    """
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        books = db.query(Book).offset(skip).limit(limit).all()
        events_queue.append(f"Book was retrieved")
        return books
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while retrieving the books. Please try again later.")

@router.get("/{id}", summary="Retrieve a book", description="Retrieve a book by the book id", 
            response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(user: user_dependency, db: db_dependency, id: int):
    """
    Retrieve the books by book id
    Accepts a path parameter id, to retrieve the book with id
    """
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        events_queue.append(f"Book was retrieved, BookID: {id}")
        return book
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while retrieving the books by ID. Please try again later.")

@router.put("/{id}", summary="Update a book", description="Update a book by it's book id with Title, Author, Published Date, Summary, or Genere", 
            response_model=BookResponse, status_code=status.HTTP_200_OK)
async def update_book(user: user_dependency, db: db_dependency, id: int, updated_book: BookCreate):
    """
    Update a new book with the below fields by passing it in the request body
    title:          Title of the book
    author:         Author of the book
    published_date: Published date of the book
    summary:        Summary of the book
    genre:          Genere of the book
    """
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        for key, value in updated_book.dict().items():
            setattr(book, key, value)
        db.commit()
        db.refresh(book)
        events_queue.append(f"Book was updated, {updated_book.dict().items()}")
        return book
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while updating the book. Please try again later.")

@router.delete("/{id}", summary="Delete a book", description="Delete a book by it's book id",
               status_code=status.HTTP_200_OK)
async def delete_book(user: user_dependency, db: db_dependency, id: int):
    """
    Deletes a book based on book id
    Accepts a path parameter id, to delete the book of the given id
    """
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        db.delete(book)
        db.commit()
        events_queue.append(f"Book was deleted, BookID: {id}")
        return {
                "message": "Book was deleted successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while deleting the book. Please try again later.")

