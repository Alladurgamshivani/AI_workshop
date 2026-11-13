
from pydantic import BaseModel, ConfigDict, Field


class MovieResponse(BaseModel):
    movie_id: int
    title: str
    genres: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RatingCreate(BaseModel):
    user_id: int
    movie_id: int
    rating: float = Field(ge=0.5, le=5.0)


class RatingResponse(BaseModel):
    rating_id: int
    user_id: int
    movie_id: int
    rating: float

    model_config = ConfigDict(from_attributes=True)
