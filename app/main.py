from fastapi import FastAPI
from app.routers import auth, book
from app.database.db import Base, engine

app = FastAPI(
    title="Books API",
    description="Books API with CRUD operations",
    version="1.0.0",
    openapi_tags=[
        {
            'name': "Books API",
            'description': 'Book API to add, create, update and delete a book'
        }
    ]
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(book.router)