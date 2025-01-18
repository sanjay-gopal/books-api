from fastapi import FastAPI
from app.routers import auth, book, streaming
from app.database.db import Base, engine

app = FastAPI(
    title="Books API",
    description="Books API with CRUD operations",
    version="1.0.0",
    openapi_tags=[{
            "name": "Books API",
            "description": "Book API to add, create, update and delete a book"
        }
    ],
    contact={
        "name": "Sanjay Gopal",
        "email": "sanjay.gopal111@gmail.com"
    }
)

Base.metadata.create_all(bind=engine)

#Including all the routers
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(streaming.router)