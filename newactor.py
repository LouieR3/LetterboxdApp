import pandas as pd
from user import user
import time

start_time = time.time()

# load the dataframe
file = user()
df = pd.read_csv(file)
df = df[df["Actors"].notna()]
print(len(df))
df = df[df["Genre"].str.contains("Documentary") == False]
df['MyRating'] = (df["MyRating"]*2)
# create a sample dataframe
# df = pd.DataFrame({"movie_id": [1, 2, 3], "movie_title": ["Movie 1", "Movie 2", "Movie 3"], "genres": ["Action, Adventure, Sci-Fi", "Comedy, Romance", "Drama, History"]})

# split the genres column into multiple rows
split_df = df["Actors"].str.split(",").apply(pd.Series)
# split_df = split_df.drop([4, 5], axis=1)
# print(split_df)

# join the split dataframe back to the original dataframe
df = df.join(split_df)
print(split_df.columns)

# ReviewDate,MovieLength,LengthInHour,Languages,Director,ReleaseYear
df = df.drop(['LBRating', 'Difference', 'ReviewDate', 'MovieLength', 'LengthInHour', 'Languages', 'Director', 'ReleaseYear', 'Country', 'NumberOfReviews', 'NumberOfRatings', 'Actors'], axis=1)

# rename the columns
df.columns = ["Movie", "MyRating", "Actors", "genre_1", "genre_2", "genre_3", "genre_4"]

# # drop the original genres column
# df = df.drop(["Genre"], axis=1)
key = 15
actorList = []
for i in range(len(key)):
    str = "actor_" + str(i+1)
    actorList.append(str)
actors_list = df[actorList].stack().unique()


# MAKE LIST WITH THOSE NUMS PLUS THE WEIGHTED AND THEN MAKE DF OF THAT LIST AFTER
checkList = []
for actor in actors_list:
    # create a boolean mask to select the rows where the genre is contained in the genres column
    mask = df["Genre"].str.contains(actor)

    # calculate the average rating for the selected rows
    avg_rating = df.loc[mask, "MyRating"].mean()
    total_movies = df.loc[mask, "MyRating"].count()

    # print the average rating
    checkList.append([actor, avg_rating, total_movies])

# create a dataframe with the average rating for each genre seen by each user
genre_ratings = pd.DataFrame(checkList, columns =['Genre', 'avg_rating', 'Total']).set_index('Genre')

# calculate the percentage of movies seen for each genre by each user
genre_ratings["percentage"] = (genre_ratings["Total"] / len(df)) * 100

# define the weighting factor
weight = 0.995

# create a new column with the weighted sum of ratings and total_movies
genre_ratings['weighted_sum'] = genre_ratings['avg_rating']*weight + genre_ratings['Total']*(1-weight)

# find the favorite genre for each user
# favorite_genre = genre_ratings.loc[genre_ratings.groupby("user_id")["weighted_sum"].idxmax()]

# print the favorite genre for user 1
genre_ratings= genre_ratings.sort_values(by=['weighted_sum'], ascending=False)
# print the dataframe
print(genre_ratings)