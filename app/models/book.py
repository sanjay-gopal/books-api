from sqlalchemy import Column, Integer, String, Date
from app.database.db import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    published_date = Column(Date, nullable=False)
    summary = Column(String, nullable=False)
    genre = Column(String, nullable=False)