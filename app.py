import streamlit as st
import pandas as pd
import requests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ---------------- NETFLIX DARK THEME ----------------
st.markdown("""
<style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        color: white !important;
    }
    button {
        background-color: #e50914 !important;
        color: white !important;
        border-radius: 6px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA (NO PICKLE) ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("movies.csv")  # MUST EXIST
    tfidf = TfidfVectorizer(stop_words="english")
    vectors = tfidf.fit_transform(df["tags"])
    similarity = cosine_similarity(vectors)
    return df, similarity

movies, similarity = load_data()

# ---------------- TMDB API KEY ----------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# ---------------- POSTER FETCH (CACHED) ----------------
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": TMDB_API_KEY}
        res = requests.get(url, params=params, timeout=3)
        res.raise_for_status()
        data = res.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
        return None
    except:
        return None

# ---------------- RECOMMENDATION LOGIC ----------------
def recommend(movie_title):
    idx = movies[movies["title"] == movie_title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]

    results = []
    for i, _ in scores:
        row = movies.iloc[i]
        poster = fetch_poster(row["id"])
        results.append((row["title"], poster))
    return results

# ---------------- UI ----------------
st.markdown(
    "<h1 style='text-align:center;'> Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

st.write("")

selected_movie = st.selectbox(
    "Choose a movie",
    movies["title"].values
)

if st.button("Recommend"):
    with st.spinner("Finding similar movies..."):
        recommendations = recommend(selected_movie)

    cols = st.columns(5)
    for i, (title, poster) in enumerate(recommendations):
        with cols[i]:
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.image(
                    "https://via.placeholder.com/300x450?text=No+Poster",
                    use_container_width=True
                )
            st.markdown(
                f"<p style='text-align:center; font-weight:600;'>{title}</p>",
                unsafe_allow_html=True
            )
