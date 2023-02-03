import pandas as pd
from operator import itemgetter
import streamlit as st
from ratings import ratings
from user import user
from callLength import lenMovies
from callGenre import genreMovies
from callLanguage import langMovies
from callDirector import directorMovies
from callDecade import decadeMovies
from callActors import actorMovies
import time

start_time = time.time()

# load the dataframe
file = user()

df250 = pd.read_csv("Top1001Films.csv")
df = pd.read_csv(file)
cond = df250['Movie'].isin(df['Movie'])
df250.drop(df250[cond].index, inplace = True)
df250 = df250.reset_index(drop=True)

# define weighting factors for each attribute
weights = {"genre": 0.4, "decade": 0.2, "length": 0.1, "language": 0.1, "director": 0.1, "rating":0.1}

# create a function to calculate the recommendation score
def recommend(movie, user, ratings_df):
    score = 0
    for attribute in weights:
        # get the user's favorite value for the attribute
        if attribute == 'rating':
            user_preference = ratings_df[ratings_df['user_id'] == user['user_id']]['rating'].mean()
        else:
            user_preference = user[attribute]
        # get the movie's value for the attribute
        movie_value = movie[attribute]
        # calculate the similarity score between the user's preference and the movie's value
        similarity = calculate_similarity(user_preference, movie_value)
        # update the score
        score += weights[attribute] * similarity
    return score

# define a function to calculate the similarity score between two values
def calculate_similarity(user_preference, movie_value):
    # example implementation: return 1 if the values match, 0 otherwise
    return 1 if user_preference == movie_value else 0

# create a sample user with favorite genres, decade of movie, length of movie, language, and director
user = {"user_id": 1, "genre": "Action", "decade": "2010s", "length": "120", "language": "English", "director": "Christopher Nolan"}

# create a sample movie with genres, decade of movie, length of movie, language, and director
movie = {"genre": "Action", "decade": "2010s", "length": "120", "language": "English", "director": "Christopher Nolan"}

# calculate the recommendation score for the movie
score = recommend(movie, user)

# check if the score is high enough to recommend the movie
if score > 0.5:
    print("Recommend this movie to the user")
else:
    print("Do not recommend this movie to the user")