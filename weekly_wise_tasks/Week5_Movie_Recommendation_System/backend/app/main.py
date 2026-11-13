
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import get_db
from .models import Movie
from .schemas import MovieResponse
from .routes.movies import router as movies_router
from .routes.ratings import router as ratings_router
from .routes.recommendations import router as recommendations_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="Movie Recommendation System API",
    description="Backend API for the Movie Recommendation System",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(movies_router)
app.include_router(ratings_router)
app.include_router(recommendations_router)
@app.get("/")
def home():
    return {"message": "Movie Recommendation API is running"}


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    database_name = db.execute(
        text("SELECT current_database()")
    ).scalar()

    return {
        "status": "connected",
        "database": database_name
    }


@app.get("/movies", response_model=list[MovieResponse])
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).limit(20).all()
