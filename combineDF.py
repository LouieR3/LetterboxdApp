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
frames = []
total_movies_df = pd.read_csv("random-movie-roulette.csv")

frames.append(total_movies_df)

extension = 'csv'
csvs = glob.glob('AllFilms*.{}'.format(extension))
for file in csvs:
    df = pd.read_csv(file)
    df = df.drop(["MyRating", "Difference", "ReviewDate"], axis=1)
    frames.append(df)

print(len(total_movies_df))
total_movies_df = total_movies_df[(total_movies_df["MovieLength"] > 60) & (total_movies_df["MovieLength"] < 275)]
print(len(total_movies_df))
result = pd.concat(frames)
print(len(result))
result = result.drop_duplicates(subset=['Movie', 'Director'])
print(len(result))

print("--- %s seconds ---" % (time.time() - start_time))