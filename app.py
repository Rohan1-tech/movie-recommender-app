import streamlit as st
import pickle
import requests
import os

# ---------------- DOWNLOAD MODEL FILES ----------------
def download_file(url, filename):
    if not os.path.exists(filename):
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

MOVIE_LIST_URL = "https://github.com/Rohan1-tech/movie-recommender-app/releases/download/v1/movie_list.pkl"
SIMILARITY_URL = "https://github.com/Rohan1-tech/movie-recommender-app/releases/download/v1/similarity.pkl"

download_file(MOVIE_LIST_URL, "movie_list.pkl")
download_file(SIMILARITY_URL, "similarity.pkl")

movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))
