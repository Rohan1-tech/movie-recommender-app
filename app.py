import streamlit as st
import pickle
import requests
import os
import io
from PIL import Image

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

st.markdown("<h1 style='text-align:center;'> Movie Recommendation System</h1>", unsafe_allow_html=True)

# ---------------- TMDB API KEY ----------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# ---------------- DOWNLOAD MODEL FILES ----------------
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
            for chunk in r.iter_content(8192):
                f.write(chunk)

    if not os.path.exists("similarity.pkl"):
        r = requests.get(
            "https://github.com/Rohan1-tech/movie-recommender-app/releases/download/v1/similarity.pkl",
            stream=True,
            timeout=300
        )
        r.raise_for_status()
        with open("similarity.pkl", "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity


movies, similarity = load_models()

# ---------------- POSTER FETCH (LOCAL IMAGE RENDERING) ----------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_title):
    try:
        # 1️ Search movie by title
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": movie_title,
            "include_adult": False
        }
        r = requests.get(search_url, params=params, timeout=10)
        data = r.json()

        if not data.get("results"):
            return None

        poster_path = data["results"][0].get("poster_path")
        if not poster_path:
            return None

        # 2️ Download poster image bytes
        image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        img_response = requests.get(image_url, timeout=10)

        image_bytes = io.BytesIO(img_response.content)
        return Image.open(image_bytes)

    except Exception:
        return None

# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        title = movies.iloc[i[0]]["title"]
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

# ---------------- UI ----------------
selected_movie = st.selectbox(
    "🎥 Select a movie",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            if posters[i] is not None:
                st.image(posters[i], use_container_width=True)
            else:
                st.image(
                    "https://via.placeholder.com/300x450?text=No+Poster",
                    use_container_width=True
                )
            st.caption(names[i])
