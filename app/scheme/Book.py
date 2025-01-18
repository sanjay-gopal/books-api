from pydantic import BaseModel, Field
from datetime import date

class BookCreate(BaseModel):
    title: str = Field(..., description="Title of the book")
    author: str = Field(..., description="Author of the book")
    published_date: date = Field(..., description="Published date of the book")
    summary: str = Field(..., description="Summary of the book")
    genre: str = Field(..., description="Genere of the book")

class BookResponse(BookCreate):
    id: int

    class Config:
        form_attribute = True