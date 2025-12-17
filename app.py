import streamlit as st
import pickle
import requests

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


# ---------------- LOAD DATA ----------------
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- TMDB API KEY ----------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# ---------------- POSTER FETCH (FAST + CACHED) ----------------
@st.cache_data(ttl=86400, show_spinner=False)  # cache for 24 hours
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": TMDB_API_KEY}
        response = requests.get(url, params=params, timeout=3)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None

    except requests.exceptions.RequestException:
        return None

# ---------------- RECOMMENDATION LOGIC ----------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]

    movie_list = sorted(
        enumerate(distances),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []
    for i, _ in movie_list:
        row = movies.iloc[i]
        movie_id = row["id"]      # change if needed
        title = row["title"]
        poster = fetch_poster(movie_id)
        recommendations.append((title, poster))

    return recommendations


# ---------------- UI ----------------
st.markdown(
    "<h1 style='text-align:center;'>  Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

st.write("")

selected_movie = st.selectbox(
    "Choose a movie",
    movies["title"].values
)

if st.button("Recommend"):
    with st.spinner("Finding similar movies..."):
        results = recommend(selected_movie)

    cols = st.columns(5)

    for idx, (title, poster) in enumerate(results):
        with cols[idx]:
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
