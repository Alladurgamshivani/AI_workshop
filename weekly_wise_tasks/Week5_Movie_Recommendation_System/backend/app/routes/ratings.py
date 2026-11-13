
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Rating, User, Movie
from ..schemas import RatingCreate, RatingResponse

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/", response_model=RatingResponse, status_code=201)
def create_rating(
    rating_data: RatingCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.user_id == rating_data.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    movie = db.query(Movie).filter(
        Movie.movie_id == rating_data.movie_id
    ).first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    existing_rating = db.query(Rating).filter(
        Rating.user_id == rating_data.user_id,
        Rating.movie_id == rating_data.movie_id
    ).first()

    if existing_rating:
        raise HTTPException(
            status_code=409,
            detail="User has already rated this movie"
        )

    new_rating = Rating(**rating_data.model_dump())

    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating


@router.get("/user/{user_id}", response_model=list[RatingResponse])
def get_user_ratings(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(Rating).filter(
        Rating.user_id == user_id
    ).all()
