from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi import status, Request, Query
from pydantic import ValidationError

from app.database.db import db_dependency
from app.models.book import Book
from app.routers.auth import get_current_user

from typing import Annotated, Optional
from app.scheme.Book import BookCreateRequest, BookResponse, BookQueryParams
from app.routers.streaming import emit_book_event
router = APIRouter(prefix="/v1", tags=["Book APIs"])

user_dependency = Annotated[dict, Depends(get_current_user)]

async def validate_query_params(request: Request):
    book_query_params = dict(request.query_params)
    try:
        return BookQueryParams(**book_query_params)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())
    
@router.post("/book", summary="Create a new book", description="Create a new book by providing Title, Author, Published Date, Summary, and Genere", 
             response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(user: user_dependency, db: db_dependency, book: BookCreateRequest):
    """
    Create a new book with the below fields by passing it in the request body
    title:          Title of the book
    author:         Author of the book
    published_date: Published date of the book
    summary:        Summary of the book
    genre:          Genere of the book
    """
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        await emit_book_event("New book was created.")
        return db_book
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while processing the request. Please try again later.")

@router.get("/books", summary="Retrieve books", description="Retrieve books by providing limit",
            response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_books(user: user_dependency, db: db_dependency, book_query_params: BookQueryParams = Depends(validate_query_params), 
                    page: int = Query(1, description="This query param is page start number and should be of type integer. "), 
                    page_limit: int = Query(10, description="This query param is for page limit and should be of type integer. ")):
    """
    Retrieve the books based on below query parameter
    page: value should greater than or equal to 0
    limit: defalted to 10 and can be less than or equal to 100
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    try:
        page = book_query_params.page or 1
        page_limit = book_query_params.page_limit or 10
        start = (page - 1) * page_limit

        books = db.query(Book).offset(start).limit(page_limit).all()
        await emit_book_event("Books was retrieved")
        return books
    
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= str(e))
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while retrieving the books. Please try again later.")

@router.get("/book/{id}", summary="Retrieve a book", description="Retrieve a book by the book id", 
            response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book_by_id(user: user_dependency, db: db_dependency, id: int):
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
        await emit_book_event(f"Book was retrieved, Book ID: {id}")
        return book
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while retrieving the books by ID. Please try again later.")

@router.put("/book/{id}", summary="Update a book", description="Update a book by it's book id with Title, Author, Published Date, Summary, or Genere", 
            response_model=BookResponse, status_code=status.HTTP_200_OK)
async def update_book_by_id(user: user_dependency, db: db_dependency, id: int, updated_book: BookCreateRequest):
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
        await emit_book_event(f"Book with book id {id} was updated")
        return book
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while updating the book. Please try again later.")

@router.delete("/book/{id}", summary="Delete a book", description="Delete a book by book id", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(user: user_dependency, db: db_dependency, id: int):
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
        await emit_book_event(f"Book was deleted, Book ID: {id}")
        return {
                "message": "Book was deleted successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while deleting the book. Please try again later.")

