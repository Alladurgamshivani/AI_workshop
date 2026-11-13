
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from .models import Rating, Movie


def get_user_recommendations(
    db: Session,
    user_id: int,
    limit: int = 10
):
    # Fetch all ratings from the database
    ratings = db.query(Rating).all()

    if not ratings:
        return []

    # Convert ratings into a NumPy array
    user_ids = np.array([r.user_id for r in ratings])
    movie_ids = np.array([r.movie_id for r in ratings])
    scores = np.array([r.rating for r in ratings], dtype=float)

    # Create index mappings
    unique_users = np.unique(user_ids)
    unique_movies = np.unique(movie_ids)

    if user_id not in unique_users:
        return []

    user_index = {uid: i for i, uid in enumerate(unique_users)}
    movie_index = {mid: i for i, mid in enumerate(unique_movies)}

    # Build sparse user-movie matrix
    row_indices = np.array([user_index[uid] for uid in user_ids])
    col_indices = np.array([movie_index[mid] for mid in movie_ids])

    user_movie_matrix = csr_matrix(
        (scores, (row_indices, col_indices)),
        shape=(len(unique_users), len(unique_movies))
    )

    # Calculate cosine similarity between users
    similarities = cosine_similarity(
        user_movie_matrix,
        dense_output=True
    )

    target_index = user_index[user_id]
    user_similarities = similarities[target_index].copy()

    # Exclude the target user
    user_similarities[target_index] = 0

    # Select the 20 most similar users
    similar_user_indices = np.argsort(user_similarities)[::-1][:20]

    # Find movies already rated by the target user
    rated_movie_ids = {
        r.movie_id
        for r in ratings
        if r.user_id == user_id
    }

    # Calculate weighted recommendation scores
    recommendation_scores = {}

    for similar_index in similar_user_indices:
        similarity = user_similarities[similar_index]

        if similarity <= 0:
            continue

        similar_user_id = unique_users[similar_index]

        for r in ratings:
            if (
                r.user_id == similar_user_id
                and r.movie_id not in rated_movie_ids
            ):
                if r.movie_id not in recommendation_scores:
                    recommendation_scores[r.movie_id] = [0.0, 0.0]

                recommendation_scores[r.movie_id][0] += (
                    similarity * r.rating
                )
                recommendation_scores[r.movie_id][1] += similarity

    # Sort movies by weighted average score
    ranked_movies = sorted(
        recommendation_scores.items(),
        key=lambda item: item[1][0] / item[1][1],
        reverse=True
    )

    results = []

    for movie_id, (weighted_sum, similarity_sum) in ranked_movies[:limit]:
        movie = db.query(Movie).filter(
            Movie.movie_id == movie_id
        ).first()

        if movie:
            results.append({
                "movie_id": movie.movie_id,
                "title": movie.title,
                "genres": movie.genres,
                "predicted_rating": round(
                    weighted_sum / similarity_sum, 2
                )
            })

    return results
