
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movie
from ..schemas import MovieResponse

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=list[MovieResponse])
def get_movies(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Movie)

    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))

    return query.order_by(Movie.title).limit(100).all()


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(
        Movie.movie_id == movie_id
    ).first()

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return movie
