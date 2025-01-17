from fastapi import FastAPI
from app.routers import auth, book
from app.database.db import Base, engine

app = FastAPI(
    title="Books API",
    description="Books API with CRUD operations",
    version="v1"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(book.router)