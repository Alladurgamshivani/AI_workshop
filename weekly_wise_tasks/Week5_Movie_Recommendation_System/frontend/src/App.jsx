
import { useEffect, useState } from "react";
import api from "./api";
import "./App.css";

function App() {
  const [movies, setMovies] = useState([]);
  const [search, setSearch] = useState("");
  const [userId, setUserId] = useState("1");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchMovies = async (query = "") => {
    try {
      setError("");
      const response = await api.get("/movies/", {
        params: query ? { search: query } : {},
      });
      setMovies(response.data);
    } catch (err) {
      setError("Unable to load movies. Check whether the backend is running.");
    }
  };

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/recommendations/${userId}`,
        { params: { limit: 10 } }
      );

      setRecommendations(response.data.recommendations);
    } catch (err) {
      setError("Unable to load recommendations. Check the user ID.");
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchMovies(search);
  };

  return (
    <div className="app">
      <header className="navbar">
        <h2>Movie<span>Mate</span></h2>
        <nav>
          <a href="#home">Home</a>
          <a href="#movies">Movies</a>
          <a href="#recommendations">Recommendations</a>
        </nav>
      </header>

      <main>
        <section className="hero" id="home">
          <p className="eyebrow">YOUR PERSONAL MOVIE GUIDE</p>
          <h1>Discover movies<br />you'll love.</h1>
          <p>
            Explore movies and discover personalized recommendations
            powered by collaborative filtering.
          </p>
          <a href="#movies" className="hero-button">Explore Movies</a>
        </section>

        {error && <p className="error">{error}</p>}

        <section className="section" id="movies">
          <div className="section-heading">
            <div>
              <p className="eyebrow">EXPLORE THE COLLECTION</p>
              <h2>Popular Movie Catalog</h2>
            </div>
            <span>{movies.length} movies displayed</span>
          </div>

          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Search movies by title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button type="submit">Search</button>
          </form>

          <div className="movie-grid">
            {movies.map((movie) => (
              <article className="movie-card" key={movie.movie_id}>
                <div className="movie-icon">🎬</div>
                <h3>{movie.title}</h3>
                <p>{movie.genres || "Genre not available"}</p>
                <small>Movie ID: {movie.movie_id}</small>
              </article>
            ))}
          </div>

          {movies.length === 0 && !error && (
            <p className="empty">No movies found.</p>
          )}
        </section>

        <section className="section recommendations" id="recommendations">
          <p className="eyebrow">POWERED BY COLLABORATIVE FILTERING</p>
          <h2>Made for your taste</h2>
          <p>Enter a MovieLens user ID to discover personalized movies.</p>

          <div className="recommendation-form">
            <input
              type="number"
              min="1"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter user ID"
            />
            <button onClick={fetchRecommendations}>
              Get Recommendations
            </button>
          </div>

          {loading && <p>Finding your recommendations...</p>}

          <div className="movie-grid">
            {recommendations.map((movie) => (
              <article className="movie-card recommended" key={movie.movie_id}>
                <div className="movie-icon">⭐</div>
                <h3>{movie.title}</h3>
                <p>{movie.genres}</p>
                <strong>Predicted rating: {movie.predicted_rating}/5</strong>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer>
        MovieMate — Personalized Movie Recommendation System
      </footer>
    </div>
  );
}

export default App;
