import streamlit as st
import pickle
import requests

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= NETFLIX STYLE CSS =================
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
    h1, h2, h3 {
        color: white;
    }
    .stButton > button {
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

st.markdown(
    "<h1 style='text-align:center;'> Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

# ================= TMDB API KEY =================
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# ================= LOAD MODEL FILES =================
@st.cache_resource(show_spinner=True)
def load_models():
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_models()

# ================= FETCH POSTER =================
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}"
        params = {"api_key": TMDB_API_KEY}

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"
    except Exception:
        return "https://via.placeholder.com/300x450?text=Error"

# ================= RECOMMEND FUNCTION =================
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]]["id"]  # TMDB ID
        recommended_movies.append(movies.iloc[i[0]]["title"])
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# ================= UI =================
selected_movie = st.selectbox(
    " Select a movie",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.caption(names[i])
