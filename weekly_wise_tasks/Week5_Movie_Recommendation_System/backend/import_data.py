
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"

# Load Neon connection
load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

engine = create_engine(DATABASE_URL)

# Read CSV files
movies = pd.read_csv(DATASET_DIR / "movies.csv")
ratings = pd.read_csv(DATASET_DIR / "ratings.csv")

# Prepare movies
movies = movies.rename(columns={"movieId": "movie_id"})
movies = movies[["movie_id", "title", "genres"]]

# Prepare users from MovieLens user IDs
users = pd.DataFrame({
    "user_id": sorted(ratings["userId"].unique())
})

users["username"] = users["user_id"].apply(
    lambda x: f"movielens_user_{x}"
)
users["email"] = users["user_id"].apply(
    lambda x: f"movielens_user_{x}@example.invalid"
)
users["password_hash"] = "NOT_FOR_LOGIN"

# Prepare ratings
ratings = ratings.rename(columns={
    "userId": "user_id",
    "movieId": "movie_id"
})

ratings["timestamp"] = pd.to_datetime(
    ratings["timestamp"],
    unit="s",
    utc=True
).dt.tz_convert(None)

ratings = ratings[
    ["user_id", "movie_id", "rating", "timestamp"]
]

# Import in one transaction
with engine.begin() as connection:

    users.to_sql(
        "users", connection,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    movies.to_sql(
        "movies", connection,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    ratings.to_sql(
        "ratings", connection,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi"
    )

    # Update auto-generated user ID sequence
    connection.execute(text("""
        SELECT setval(
            pg_get_serial_sequence('users', 'user_id'),
            (SELECT MAX(user_id) FROM users),
            true
        )
    """))

print("MovieLens dataset imported successfully!")
print("Movies:", len(movies))
print("Users:", len(users))
print("Ratings:", len(ratings))
