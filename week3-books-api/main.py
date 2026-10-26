from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
from database import engine, get_db

import schemas

# Create the database tables when the app starts.
# This uses the Course model from models.py.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message":"Books API is running"}

@app.get("/books", response_model=list[schemas.BooksResponse])
def get_books(db: Session = Depends(get_db)):
    # response_model tells FastAPI to return a list of CourseResponse objects.
    # Read all courses from the database.
    books = db.query(models.Books).all()
    return books


@app.get("/books/{books_id}", response_model=schemas.BooksResponse)
def get_books(books_id: int, db: Session = Depends(get_db)):
    # Find one course by primary key.
    books = db.query(models.Books).filter(models.Books.id == books_id).first()

    if books is None:
        raise HTTPException(status_code=404, detail="Books not found")

    return books


@app.post("/books", response_model=schemas.BooksResponse, status_code=201)
def create_books(books_data: schemas.BooksCreate, db: Session = Depends(get_db)):
    # course_data has already been checked by Pydantic.
    # We can use dot notation because course_data is a CourseCreate object.
    books = models.Books(
        title=books_data.title,
        author=books_data.author,
        year=books_data.year
    )

    try:
        db.add(books)
        db.commit()
        db.refresh(books)
        return books

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Books title already exists")
