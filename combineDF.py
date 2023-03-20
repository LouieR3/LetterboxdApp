import pandas as pd
import time
import numpy as np
import os
import glob

start_time = time.time()

# df = pd.read_csv("AllFilmszacierka.csv")
# # df = pd.read_csv("AllFilmsprahladsingh.csv")
# # df = pd.read_csv("AllFilmsbluegrace11.csv")
# # df = pd.read_csv("AllFilmscloakenswagger.csv")
# # df = pd.read_csv("AllFilmszacierka.csv")
# # df = pd.read_csv("AllFilmsgr8escape10.csv")
# # df = pd.read_csv("AllFilmsgoldfishbrain.csv")
# frames = []
# total_movies_df = pd.read_csv("random-movie-roulette.csv")
# total_movies_df = total_movies_df[(total_movies_df["MovieLength"] > 60) & (total_movies_df["MovieLength"] < 275)]
# total_movies_df = total_movies_df[total_movies_df['Genre'].notnull()]
# total_movies_df = total_movies_df[total_movies_df['Actors'].notnull()]
# frames.append(total_movies_df)
frames = []
Top1000df = pd.read_csv("random-movie-roulette.csv")
frames.append(Top1000df)

# df = pd.read_csv("oscars.csv")
# frames.append(df)

# result = pd.concat(frames)
# result = result.drop_duplicates(subset=['Movie', 'Director'])
# result.to_csv("TopFilmsNew.csv", index=False)

# frames.append(Top1000df)

extension = 'csv'
csvs = glob.glob('AllFilms*.{}'.format(extension))
for file in csvs:
    df = pd.read_csv(file)
    df = df[(df["MovieLength"] > 60) & (df["MovieLength"] < 275)]
    df = df[df['Genre'].notnull()]
    df = df[df['Actors'].notnull()]
    df = df.drop(["MyRating", "Difference", "ReviewDate"], axis=1)
    frames.append(df)

# print(len(total_movies_df))
result = pd.concat(frames)
print(len(result))
result = result.drop_duplicates(subset=['Movie', 'Director'])
# result.insert(0, 'movie_id', range(1, len(result) + 1))
print(len(result))
result.to_csv("TopFilms2.csv", index=False)

print("--- %s seconds ---" % (time.time() - start_time))