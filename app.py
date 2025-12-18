import streamlit as st
import pickle
import requests
import os
import pandas as pd

# -------------------- PAGE CONFIG (Netflix-style) --------------------
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide",
    
)

# -------------------- CUSTOM CSS (Netflix Dark UI) --------------------
st.markdown(
    """
    <style>
    body {
        background-color: #0f0f0f;
        color: white;
    }
    .stApp {
        background-color: #0f0f0f;
    }
    h1, h2, h3, h4 {
        color: white;
    }
    .stButton>button {
        background-color: #e50914;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.6em 1.2em;
        font-size: 16px;
    }
    .stSelectbox label {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- TMDB API KEY --------------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# -------------------- DOWNLOAD MODEL FILES (GitHub Release) --------------------
@st.cache_resource(show_spinner=True)
def load_models():
    if not os.path.exists("movie_list.pkl"):
        r = requests.get(
            "https://github.com/Rohan1-tech/movie-recommender-app/releases/download/v1/movie_list.pkl",
            stream=True,
            timeout=300
        )
        r.raise_for_status()
        with open("movie_list.pkl", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    if not os.path.exists("similarity.pkl"):
        r = requests.get(
            "https://github.com/Rohan1-tech/movie-recommender-app/releases/download/v1/similarity.pkl",
            stream=True,
            timeout=300
        )
        r.raise_for_status()
        with open("similarity.pkl", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))

    return movies, similarity


movies, similarity = load_models()

# -------------------- TMDB POSTER FUNCTION --------------------
def fetch_poster(movie_id):
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={TMDB_API_KEY}&language=en-US"
    )
    data = requests.get(url).json()

    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
    return "https://via.placeholder.com/300x450?text=No+Image"

# -------------------- RECOMMEND FUNCTION (FIXED) --------------------
def recommend(movie_title):
    index = movies[movies["title"] == movie_title].index[0]
    distances = similarity[index]
    movie_indices = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in movie_indices:
        movie_id = movies.iloc[i[0]]["movie_id"]  # FIXED
        names.append(movies.iloc[i[0]]["title"])
        posters.append(fetch_poster(movie_id))

    return names, posters

# -------------------- UI --------------------
st.markdown("<h1 style='text-align:center;'> Movie Recommendation System</h1>", unsafe_allow_html=True)

movie_list = movies["title"].values
selected_movie = st.selectbox("🎥 Select a movie", movie_list)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    st.markdown("<h2>Recommended Movies</h2>", unsafe_allow_html=True)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.caption(names[i])
