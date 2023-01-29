import pandas as pd
from user import user
import time
import numpy as np
start_time = time.time()

movies_df = pd.read_csv("Test.csv")
ratings_df = pd.read_csv("TestRatings.csv")

# define weighting factors for each attribute
weights = {"genre": 0.1, "decade": 0.3, "length": 0.4, "language": 0.1, "director": 0.5, "previous_ratings": 0.1, "popularity": 0.3}

# create a function to calculate the recommendation score
def recommend(movie, user, ratings_df):
    score = 0
    for attribute in weights:
        # get the user's favorite value for the attribute
        if attribute == 'previous_ratings':
            user_preference = get_user_preference_on_ratings(ratings_df, user)
        else:
            user_preference = user[attribute]
        # get the movie's value for the attribute
        movie_value = movie[attribute]
        # calculate the similarity score between the user's preference and the movie's value
        if attribute == 'previous_ratings':
            similarity = calculate_similarity_on_ratings(user_preference, movie_value)
        else:
            similarity = calculate_similarity(user_preference, movie_value)
        # update the score
        score += weights[attribute] * similarity
    return score

# define a function to calculate the similarity score between two values
def calculate_similarity(user_preference, movie_value):
    # example implementation: return 1 if the values match, 0 otherwise
    return 1 if user_preference == movie_value else 0

#define function to get the user's preference based on ratings
def get_user_preference_on_ratings(ratings_df, user):
    user_ratings = ratings_df[ratings_df['user_id'] == user['user_id']]
    user_mean_rating = user_ratings['rating'].mean()
    return user_mean_rating

def calculate_similarity_on_ratings(user_preference, movie_rating):
    # Example implementation: return 1 - the absolute difference between the two ratings
    return 1 - abs(user_preference - movie_rating)

# create a list of movies to recommend
movies_to_recommend = []

# create a sample user with favorite genres, decade of movie, length of movie, language, and director
user = {"user_id": 1, "genre": "Action", "decade": "2010s", "length": "120", "language": "English", "director": "Christopher Nolan"}

# create a sample movie with genres, decade of movie, length of movie, language, and director
movie = {"genre": "Action", "decade": "2010s", "length": "120", "language": "English", "director": "Christopher Nolan"}

# iterate through all the movies in your dataset
for index, movie in movies_df.iterrows():
    # calculate the recommendation score for the current movie
    score = recommend(movie, user, ratings_df)
    # add the movie and its score to the list
    movies_to_recommend.append((movie, score))

# sort the list of movies by score in descending order
movies_to_recommend.sort(key=lambda x: x[1], reverse=True)

# select the top N movies to recommend
top_n_movies = movies_to_recommend[:20]

# print the recommended movies
for movie, score in top_n_movies:
    print("Movie: ", movie["title"])
    print("Recommendation Score: ", score)