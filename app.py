import streamlit as st
import pickle
import requests
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ---------------- NETFLIX DARK UI ----------------
st.markdown("""
<style>
body {
    background-color: #0f0f0f;
    color: white;
}
.stApp {
    background-color: #0f0f0f;
}
h1, h2, h3, h4, h5 {
    color: white;
}
.stButton > button {
    background-color: #e50914;
    color: white;
    border-radius: 6px;
    font-size: 16px;
    padding: 0.6em 1.4em;
    border: none;
}
.stSelectbox label {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    "<h1 style='text-align:center;'>  Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

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

# ---------------- POSTER FUNCTION ----------------
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": TMDB_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"
    except:
        return "https://via.placeholder.com/300x450?text=No+Poster"

# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]]["id"]
        names.append(movies.iloc[i[0]]["title"])
        posters.append(fetch_poster(movie_id))

    return names, posters

# ---------------- UI ----------------
selected_movie = st.selectbox(
    " Select a movie",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    st.markdown("<h2>Recommended Movies</h2>", unsafe_allow_html=True)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.caption(names[i])
