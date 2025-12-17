import streamlit as st
import pickle
import requests
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ---------------- DOWNLOAD MODEL FILES ----------------
def download_file(url, filename):
    if not os.path.exists(filename):
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

# 🔴 PASTE YOUR REAL LINKS HERE
MOVIE_LIST_URL = "PASTE_MOVIE_LIST_PKL_URL"
SIMILARITY_URL = "PASTE_SIMILARITY_PKL_URL"

download_file(MOVIE_LIST_URL, "movie_list.pkl")
download_file(SIMILARITY_URL, "similarity.pkl")

movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- TMDB API KEY ----------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
