import pandas as pd
from user import user
import time

start_time = time.time()

# load the dataframe
file = user("cloakenswagger")
df = pd.read_csv(file)
df['MyRating'] = (df["MyRating"]*2)
df = df[df["Languages"].notna()]
df['language'] = df['Languages'].str.split(',').str[0]
# group the dataframe by user and language
user_language_group = df.groupby(["language"])

# calculate the total number of movies seen by each user
user_total_movies = len(df)

# calculate the sum of ratings for each language seen by each user
language_sum_ratings = user_language_group["MyRating"].sum()

# calculate the total number of movies seen by each user for each language
language_total_movies = user_language_group["Movie"].count()

# calculate the average rating for each language seen by each user
language_avg_ratings = language_sum_ratings / language_total_movies

difference = user_language_group["Difference"].mean()

# create a dataframe with the average rating for each language seen by each user
language_ratings = pd.DataFrame({"Average Rating": language_avg_ratings, "Total Movies": language_total_movies, "Difference": difference})

# calculate the percentage of movies seen for each language by each user
language_ratings["Percentage"] = (language_ratings["Total Movies"] / len(df)) * 100

# define the weighting factor
weight = 0.95

# create a new column with the weighted sum of ratings and Total Movies
language_ratings['Weighted Average'] = language_ratings['Average Rating']*weight + language_ratings['Total Movies']*(1-weight) + language_ratings['Difference']

# print the favorite language for user 1
language_ratings= language_ratings.sort_values(by=['Weighted Average'], ascending=False)
print(language_ratings)

print("--- %s seconds ---" % (time.time() - start_time))