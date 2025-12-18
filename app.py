import streamlit as st
import pickle
import requests
import os

@st.cache_resource(show_spinner=False)
def load_models():
    with st.spinner("Downloading model files (first run only)..."):
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


# 🚀 LOAD MODELS
movies, similarity = load_models()

# 🎨 UI (THIS WAS MISSING)
st.title("🎬 Movie Recommendation System")
st.success("Models loaded successfully!")

movie_names = movies["title"].values
selected_movie = st.selectbox("Select a movie", movie_names)

if st.button("Recommend"):
    st.write("Recommendations will appear here")
