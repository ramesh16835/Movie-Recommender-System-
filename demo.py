import streamlit as st
import pickle
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Fetch Movie Poster

def fetch_poster(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": st.secrets["TMDB_API_KEY"]
    }

    for attempt in range(3):

        try:
            response = requests.get(
                url,
                params=params,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            response.raise_for_status()

            data = response.json()

            poster_path = data.get("poster_path")

            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path

            return None

        except requests.exceptions.RequestException as e:

            print(f"Attempt {attempt + 1} failed: {e}")

            if attempt < 2:
                time.sleep(1)

    return None

# Recommendation Function

def recommend(movie):

    movie_index = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    movie_ids = []

    for i in movies_list:

        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(
            movies.iloc[i[0]].title
        )

        movie_ids.append(movie_id)

    # Fetch all posters at the same time
    with ThreadPoolExecutor(max_workers=5) as executor:

        recommended_movies_posters = list(
            executor.map(fetch_poster, movie_ids)
        )

    return recommended_movies, recommended_movies_posters


# Load Data

movies_dict = pickle.load(
    open("movie_dict.pkl", "rb")
)

movies = pd.DataFrame(movies_dict)

similarity = pickle.load(
    open("similarity.pkl", "rb")
)

# Streamlit UI

st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie",
    movies["title"].values
)

# Recommend Button

if st.button("Recommend"):

    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for i in range(5):

        with cols[i]:

            st.text(names[i])

            if posters[i]:
                st.image(posters[i])
            else:
                st.write("Poster unavailable")