from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
import pandas as pd
import os
from datetime import date

import time

start_time = time.time()

fullCSV = "TopFilms2.csv"
# fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)

user = "cloakenswagger"
# firstUrl = "https://letterboxd.com/dave/list/official-top-250-narrative-feature-films/"
# firstUrl = "https://letterboxd.com/crew/list/2023-oscars-all-nominated-films/"
firstUrl = "https://letterboxd.com/tobiasandersen2/list/random-movie-roulette/"
# list = "AllFilmActors"
list = "random-movie-roulette"
source = requests.get(firstUrl).text
soup = BeautifulSoup(source, "lxml")
listOfPage = []
# lastDate = pd.to_datetime(df["ReviewDate"]).max()
# print(lastDate)
# today = date.today()
# d3 = today.strftime("%m/%d/%y")
# d4 = today.strftime("%Y-%m-%d %H:%M:%S")
# print(d3)
# print(d4)

bigList = []
url = "https://letterboxd.com"
myUrl = "https://letterboxd.com/" + user
count = 0
for movie in soup.find_all("li", class_="poster-container"):
    place = movie.find("p").text
    name = movie.find("img")
    movieName = name.attrs["alt"].replace(u'\xa0', u' ')
    rating = movie.find("span", attrs={"class": "rating"})
    format_float = 0
    if not rating:
        rating_val = ""
        format_float = ""
    else:
        rating_class = rating["class"][-1]
        rating_val = int(rating_class.split("-")[-1]) / 2
    # print(movieName)
    # if the current movie is exactly equal to anything in the Movie column
    movieAlreadyInList = df["Movie"].eq(movieName).any()
    # if true then check if the rating is now different
    if movieAlreadyInList == True:
        temp = df.loc[df['Movie'] == movieName]
        temp = temp.reset_index()
        currentRating = temp.at[0, "MyRating"]
    # if this is a unique record or updated movie, add it
    if movieAlreadyInList == False or float(currentRating) != rating_val: