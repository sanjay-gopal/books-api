from pydantic import BaseModel, Field
from fastapi import Query
from datetime import date
from typing import Optional
    
class BookCreateRequest(BaseModel):
    title: str = Field(..., description="Title of the book")
    author: str = Field(..., description="Author of the book")
    published_date: date = Field(..., description="Published date of the book")
    summary: str = Field(..., description="Summary of the book")
    genre: str = Field(..., description="Genere of the book")

class BookResponse(BookCreateRequest):
    id: int

    class Config:
        form_attribute = True

class BookQueryParams(BaseModel):
    page: int = Query(1, gt=0, description="This query param is page start number and should be of type integer. ")
    page_limit: int = Query(10, gt=0, le=100, description="This query param is for page limit and should be of type integer. ")

    class Config:
        extra = "forbid"