import pandas as pd
from user import user
import time

start_time = time.time()

# load the dataframe
file = user()
df = pd.read_csv(file)
df['MyRating'] = (df["MyRating"]*2)

# group the dataframe by user and genre
user_genre_group = df.groupby(["Director"])

# calculate the total number of movies seen by each user
user_total_movies = len(df)

# calculate the sum of ratings for each genre seen by each user
genre_sum_ratings = user_genre_group["MyRating"].sum()

# calculate the total number of movies seen by each user for each genre
genre_total_movies = user_genre_group["Movie"].count()

# calculate the average rating for each genre seen by each user
genre_avg_ratings = genre_sum_ratings / genre_total_movies

# create a dataframe with the average rating for each genre seen by each user
genre_ratings = pd.DataFrame({"avg_rating": genre_avg_ratings, "total_movies": genre_total_movies})

# calculate the percentage of movies seen for each genre by each user
genre_ratings["percentage"] = (genre_ratings["total_movies"] / len(df)) * 100



# find the favorite genre for each user
# favorite_genre = genre_ratings.loc[genre_ratings.groupby("user_id")["percentage"].idxmax()]

# define the weighting factor
weight = 0.75

# create a new column with the weighted sum of ratings and total_movies
genre_ratings['weighted_sum'] = genre_ratings['avg_rating']*weight + genre_ratings['total_movies']*(1-weight)

# find the favorite genre for each user
# favorite_genre = genre_ratings.loc[genre_ratings.groupby("user_id")["weighted_sum"].idxmax()]

# print the favorite genre for user 1
genre_ratings= genre_ratings.sort_values(by=['weighted_sum'], ascending=False)
print(genre_ratings)

print("--- %s seconds ---" % (time.time() - start_time))