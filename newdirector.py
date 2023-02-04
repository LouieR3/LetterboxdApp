import pandas as pd
from user import user
import time

start_time = time.time()

# load the dataframe
file = user("cloakenswagger")
df = pd.read_csv(file)
df = df[df["Genre"].str.contains("Documentary") == False]
df['MyRating'] = (df["MyRating"]*2)

# group the dataframe by user and director
user_director_group = df.groupby(["Director"])

# calculate the total number of movies seen by each user
user_total_movies = len(df)

# calculate the sum of ratings for each director seen by each user
director_sum_ratings = user_director_group["MyRating"].sum()
director_diff_avg = user_director_group["Difference"].mean()

# calculate the total number of movies seen by each user for each director
director_total_movies = user_director_group["Movie"].count()

# calculate the average rating for each director seen by each user
director_avg_ratings = director_sum_ratings / director_total_movies

# create a dataframe with the average rating for each director seen by each user
director_ratings = pd.DataFrame({"avg_rating": director_avg_ratings, "total_movies": director_total_movies, "Difference": director_diff_avg})

# create a new column with the weighted sum of ratings and total_movies
director_ratings['weighted_sum'] = director_ratings['avg_rating']*0.9 + ((director_ratings['total_movies'] + director_ratings['Difference'])*0.2)

# print the favorite director for user 1
director_ratings= director_ratings.sort_values(by=['weighted_sum'], ascending=False)
director_ratings = director_ratings[:50]
print(director_ratings)

print("--- %s seconds ---" % (time.time() - start_time))