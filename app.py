import streamlit as st
import pickle
import pandas as pd
import requests

# ─────────────────────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch — AI Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# TMDB poster helper
# ─────────────────────────────────────────────────────────────
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"  # public demo key


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """Fetch a movie poster URL from TMDB API."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception:
        pass
    return None


@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    """Fetch movie details from TMDB API."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "poster": f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}" if data.get('poster_path') else None,
            "rating": data.get("vote_average", 0),
            "year": data.get("release_date", "")[:4] if data.get("release_date") else "N/A",
            "genres": [g["name"] for g in data.get("genres", [])],
            "overview": data.get("overview", ""),
            "runtime": data.get("runtime", 0),
        }
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Load model artefacts
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity


movies_df, similarity = load_data()

# ─────────────────────────────────────────────────────────────
# Recommendation logic
# ─────────────────────────────────────────────────────────────

def recommend(movie, n=5):
    """Return top-n recommended movie titles and IDs."""
    idx = movies_df[movies_df["title"] == movie].index[0]
    distances = similarity[idx]
    movie_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1 : n + 1]

    titles, movie_ids = [], []
    for i in movie_list:
        titles.append(movies_df.iloc[i[0]].title)
        movie_ids.append(movies_df.iloc[i[0]].movie_id)
    return titles, movie_ids


# ─────────────────────────────────────────────────────────────
# Custom CSS — Premium Dark Theme
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Import Google Font ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global ────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: #e0e0e0;
}

/* ── Hide default Streamlit elements ───────────────────── */
#MainMenu, footer, header {visibility: hidden;}

/* ── Hero section ──────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 2rem 1rem 1rem 1rem;
}

.hero h1 {
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin-bottom: 0.3rem;
    animation: fadeInDown 0.8s ease-out;
}

.hero p {
    font-size: 1.1rem;
    color: #a0a0c0;
    font-weight: 300;
    max-width: 600px;
    margin: 0 auto;
    animation: fadeInUp 0.8s ease-out 0.2s both;
}

.hero .emoji-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 0.5rem;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Selectbox & Button ────────────────────────────────── */
div[data-baseweb="select"] {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    backdrop-filter: blur(12px);
}

div[data-baseweb="select"] > div {
    background: transparent !important;
    color: #fff !important;
    font-size: 1rem !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.75rem 2rem;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.35);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.55);
}

.stButton > button:active {
    transform: translateY(0);
}

/* ── Movie Card ────────────────────────────────────────── */
.movie-card {
    background: rgba(255,255,255,0.05);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    backdrop-filter: blur(10px);
    height: 100%;
}

.movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.25);
    border-color: rgba(102, 126, 234, 0.4);
}

.movie-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
}

.movie-card .card-body {
    padding: 1rem;
}

.movie-card .card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.4rem;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.movie-card .card-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.movie-card .card-year {
    font-size: 0.8rem;
    color: #a0a0c0;
    font-weight: 400;
}

.movie-card .card-rating {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    background: rgba(255, 193, 7, 0.15);
    color: #ffc107;
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
}

.movie-card .card-genres {
    margin-top: 0.5rem;
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
}

.genre-tag {
    font-size: 0.65rem;
    background: rgba(102, 126, 234, 0.2);
    color: #a0b4f7;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── No-poster placeholder ─────────────────────────────── */
.no-poster {
    width: 100%;
    aspect-ratio: 2/3;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
}

/* ── Section header ────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2.5rem 0 1.5rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.section-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

/* ── Stats bar ─────────────────────────────────────────── */
.stats-bar {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    padding: 1rem 0 0.5rem 0;
    animation: fadeInUp 0.8s ease-out 0.4s both;
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 0.75rem;
    color: #7a7a9a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 500;
}

/* ── Divider ───────────────────────────────────────────── */
.glow-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #667eea, #764ba2, #f093fb, transparent);
    border: none;
    margin: 1rem 0 1.5rem 0;
    border-radius: 2px;
}

/* ── Footer ────────────────────────────────────────────── */
.app-footer {
    text-align: center;
    padding: 3rem 0 2rem 0;
    color: #555;
    font-size: 0.8rem;
}

.app-footer a {
    color: #667eea;
    text-decoration: none;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Hero section
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
    <span class="emoji-icon">🎬</span>
    <h1>CineMatch</h1>
    <p>AI-powered movie recommendations. Pick a movie you love and discover your next obsession.</p>
</div>
""",
    unsafe_allow_html=True,
)

# Stats bar
st.markdown(
    f"""
<div class="stats-bar">
    <div class="stat-item">
        <div class="stat-value">{len(movies_df):,}</div>
        <div class="stat-label">Movies</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">5</div>
        <div class="stat-label">Recommendations</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">AI</div>
        <div class="stat-label">Powered</div>
    </div>
</div>
<div class="glow-divider"></div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Search section
# ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1], gap="medium")

with col1:
    selected_movie = st.selectbox(
        "🔍  Search for a movie",
        movies_df["title"].values,
        index=None,
        placeholder="Type a movie title...",
        label_visibility="collapsed",
    )

with col2:
    search_clicked = st.button("✨ Recommend", use_container_width=True)

# ─────────────────────────────────────────────────────────────
# Recommendations
# ─────────────────────────────────────────────────────────────
if search_clicked and selected_movie:
    with st.spinner("🎯 Finding your perfect matches..."):
        names, ids = recommend(selected_movie)

        # Fetch details for all recommended movies
        all_details = []
        for name, mid in zip(names, ids):
            details = fetch_movie_details(mid)
            all_details.append(details)

    # Section header
    st.markdown(
        """
    <div class="section-header">
        <h2>🍿 Because you liked """ + f'"{selected_movie}"' + """</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Display cards in 5 columns
    cols = st.columns(5, gap="medium")

    for col, name, mid, details in zip(cols, names, ids, all_details):
        with col:
            poster_url = details.get("poster") if details else None
            rating = details.get("rating", 0) if details else 0
            year = details.get("year", "N/A") if details else "N/A"
            genres = details.get("genres", []) if details else []

            poster_html = (
                f'<img src="{poster_url}" alt="{name}">'
                if poster_url
                else '<div class="no-poster">🎞️</div>'
            )

            genre_tags = "".join(
                [f'<span class="genre-tag">{g}</span>' for g in genres[:3]]
            )

            rating_stars = "⭐" if rating > 0 else ""
            rating_html = f"<span class='card-rating'>{rating_stars} {round(rating, 1)}</span>" if rating > 0 else ""
            card_html = f"""<div class="movie-card">
    {poster_html}
    <div class="card-body">
        <div class="card-title">{name}</div>
        <div class="card-meta">
            <span class="card-year">{year}</span>
            {rating_html}
        </div>
        <div class="card-genres">{genre_tags}</div>
    </div>
</div>"""
            st.markdown(card_html, unsafe_allow_html=True)

elif search_clicked and not selected_movie:
    st.warning("⚠️ Please select a movie first!")

# ─────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="app-footer">
    Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a> &
    <a href="https://www.themoviedb.org" target="_blank">TMDB</a> ·
    Content-Based Filtering with Cosine Similarity
</div>
""",
    unsafe_allow_html=True,
)
