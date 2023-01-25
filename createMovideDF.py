import pandas as pd
from user import user
import time

start_time = time.time()

# load the dataframe
file = user()
# df = pd.read_csv("AllFilmsprahladsingh.csv")
# df = pd.read_csv("AllFilmsbluegrace11.csv")
# df = pd.read_csv("AllFilmscloakenswagger.csv")
# df = pd.read_csv("AllFilmszacierka.csv")
# df = pd.read_csv("AllFilmsgr8escape10.csv")
# df = pd.read_csv("AllFilmsgoldfishbrain.csv")
df = pd.read_csv("AllFilmszacierka.csv")

# df = pd.read_csv("Test.csv")

df = df[df["MyRating"].notna()]

movie_df = df

movie_df.insert(0, 'movie_id', range(1, len(movie_df) + 1))
movie_df.insert(0, 'user_id', 1)
# movie_df = movie_df.drop(['MyRating', 'LBRating', 'Difference', 'ReviewDate', 'LengthInHour', 'Country', 'NumberOfReviews'], axis=1)
movie_df['Languages'] = movie_df['Languages'].str.split(',').str[0]
movie_df['Decade'] = (movie_df["ReleaseYear"]//10)*10
movie_df['MovieLength'] = (movie_df["MovieLength"]//10)*10
movie_df= movie_df.rename(columns={"MyRating": "rating", "LBRating": "lb_rating", "Difference": "difference", "MovieLength": "length", "Decade": "decade", "Languages": "language", "Movie": "title", "Director": "director", "Genre": "genres", "NumberOfRatings": "popularity"})

# new_movies_df = pd.read_csv("AllFilmscarmal.csv")
# new_movies_df = pd.read_csv("AllFilmscloakenswagger.csv")
# new_movies_df = pd.read_csv("AllFilmsprahladsingh.csv")
# new_movies_df = pd.read_csv("AllFilmsgoldfishbrain.csv")
new_movies_df = pd.read_csv("AllFilmsbluegrace11.csv")
new_movies_df = new_movies_df[new_movies_df["MyRating"].notna()]
new_movies_df.insert(0, 'movie_id', range(max(movie_df['movie_id'].unique()) + 1, max(movie_df['movie_id'].unique()) + 1 + len(new_movies_df)))
new_movies_df.insert(0, 'user_id', 2)
# new_movies_df = new_movies_df.drop(['MyRating', 'LBRating', 'Difference', 'ReviewDate', 'LengthInHour', 'Country', 'NumberOfReviews'], axis=1)
new_movies_df['Languages'] = new_movies_df['Languages'].str.split(',').str[0]
new_movies_df['Decade'] = (new_movies_df["ReleaseYear"]//10)*10
new_movies_df['MovieLength'] = (new_movies_df["MovieLength"]//10)*10
new_movies_df= new_movies_df.rename(columns={"MyRating": "rating", "LBRating": "lb_rating", "Difference": "difference", "MovieLength": "length", "Decade": "decade", "Languages": "language", "Movie": "title", "Director": "director", "Genre": "genres", "NumberOfRatings": "popularity"})

# split the new dataframe into movies and ratings dataframes
movies_df = movie_df[["movie_id", "title", "length", "language", "genres", "director", "decade", "popularity", "Actors"]]
ratings_df = movie_df[["user_id", "movie_id", "rating", "lb_rating", "difference"]]

# split the new dataframe into movies and ratings dataframes
add_movies_df = new_movies_df[["movie_id", "title", "length", "language", "genres", "director", "decade", "popularity", "Actors"]]
add_ratings_df = new_movies_df[["user_id", "movie_id", "rating", "lb_rating", "difference"]]

# concatenate the new dataframes with the existing dataframes
movieFinal_df = pd.concat([movies_df, add_movies_df], ignore_index=True)
movieFinal_df = movieFinal_df.drop_duplicates(subset=['title', 'director'])
# HOW DO YOU STOP THE MOVIE ID FROM BEING OUT OF SYNC

# merge the ratings dataframe and the movie titles dataframe on the movie_id column
ratings_df = pd.merge(ratings_df, movieFinal_df, on='movie_id', how ='outer')
ratings_df = pd.concat([ratings_df, new_ratings_df], ignore_index=True)

# drop duplicate rows
ratings_df = ratings_df.drop_duplicates()



ratingFinal_df = pd.concat([ratings_df, add_ratings_df], ignore_index=True)
ratingFinal_df = ratingFinal_df.drop_duplicates()
print(len(movies_df))
print()

print(len(df))
print(len(new_movies_df))
print(len(movies_df))
print()
print(movies_df)


movieFinal_df.to_csv('Test.csv', index=False)
ratingFinal_df.to_csv('TestRatings.csv', index=False)