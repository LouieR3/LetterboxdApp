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

# dataPath = "C:\\Users\\louie\\Desktop\\repo\\LetterboxdApp"
# dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
user = "goldfishbrain"
# user = "carmal"
# user = "cloakenswagger"
# user = "gr8escape10"
# user = "seanfennessey"
# user = "zacierka"
# user = "bluegrace11"
file = "AllFilms" + user + ".csv"
fullCSV = "AllFilms" + user + ".csv"
# fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)

# file2 = "AllFilmActors.csv"
# fullCSV2 = os.path.join(dataPath, file2)
# df3 = pd.read_csv(fullCSV2)

firstUrl = "https://letterboxd.com/" + user + "/films/by/rated-date/"
source = requests.get(firstUrl).text
soup = BeautifulSoup(source, "lxml")

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
        # print("My rating is: " + rate)
        div = movie.find("div")
        filmLink = div.attrs["data-film-slug"]
        filmURL = url + "/film/" + filmLink
        # print(filmURL)
        myFilmUrl = myUrl + filmLink
        myReview = requests.get(myFilmUrl).text
        myFilm = BeautifulSoup(myReview, "lxml")
        viewDate = "N/A"
        vd = ""
        TheDate = ""
        yr = ""
        rest = ""
        finalDate = ""
        try:
            viewDate = (
                myFilm.find(
                    "p", class_="view-date").find("a").next_sibling.next_element
            )
            vd = str(viewDate).split("for")[1]
            TheDate = vd[41:-9]
            yr = vd[1:5]
            rest = vd[6:11]
            finalDate = rest + "/" + yr
        except:
            viewDate = ""
        sourceFilm = requests.get(filmURL).text
        soupFilm = BeautifulSoup(sourceFilm, "lxml")
        length = soupFilm.find("p", class_="text-link").text
        lengthOfMovie = length[12:15]
        lenNum = [int(s) for s in lengthOfMovie.split() if s.isdigit()]
        try:
            finalLen = lenNum[0]
            mod = finalLen % 60
            hour = finalLen / 60
            hour = int(hour)
            finmod = ""
            if mod < 10:
                finmod = "0" + str(mod)
            else:
                finmod = str(mod)
            lengthInHour = str(hour) + ":" + finmod
        except:
            finalLen = 0
        if finalLen > 60 and finalLen < 500:
            # print(movieName)
            languages = soupFilm.find("div", id="tab-details")
            lan = languages.find_all("a", href=re.compile("language"))
            lanList = []
            lanString = ""
            for item in lan:
                lanList.append(item.text.strip())
            if len(lanList) > 1:
                lanString = ",".join(lanList)
                lanString = str(lanString.split(',', 1)[1])
            else:
                lanString = lanList[0]
            detailsDiv = soupFilm.find(
                "script", type="application/ld+json").string
            start = detailsDiv.find("/* <![CDATA[ */") + len("/* <![CDATA[ */")
            end = detailsDiv.find("/* ]]> */")
            subs = detailsDiv[start:end]
            y = json.loads(subs)
            director = ""
            try:
                director = y["director"][0]["name"]
            except:
                director = ""
            release = y["releasedEvent"][0]["startDate"]

            actors = ""
            try:
                actors = y["actors"]
            except:
                actors = ""
            act1 = ""
            limit = 0
            if len(actors) > 20 and len(actors) < 27:
                limit = len(actors)*0.6
            elif len(actors) >= 27:
                limit = len(actors)*0.4
            else:
                limit = len(actors)
            limit = round(limit)
            for act in range(limit):
                if act == 0:
                    act1 = act1 + actors[act]["name"]
                else:
                    act1 = act1 + "," + actors[act]["name"]

            genreString = ""
            genre_in_dict = "genre" in y
            if genre_in_dict:
                genre = y["genre"]
                if len(genre) > 1:
                    genreString = ",".join(genre)
                else:
                    genreString = genre[0]
            else:
                genre = ""
            try:
                country = y["countryOfOrigin"][0]["name"]
            except:
                country = ""

            try:
                avgRate = y["aggregateRating"]["ratingValue"]
            except:
                avgRate = 0
            if format_float == 0:
                diff = rating_val - avgRate
                format_float = "{:.2f}".format(diff)

            try:
                numReviews = y["aggregateRating"]["reviewCount"]
            except:
                numReviews = 0
            try:
                numRatings = y["aggregateRating"]["ratingCount"]
            except:
                numRatings = 0

            bigList.append(
                [
                    movieName,
                    rating_val,
                    avgRate,
                    format_float,
                    finalDate,
                    finalLen,
                    lengthInHour,
                    lanString,
                    director,
                    release,
                    genreString,
                    country,
                    numReviews,
                    numRatings,
                    act1
                ]
            )
        count += 1
if count == 50:
    print("need to go to next page")
if len(bigList) > 0:
    print(bigList)
    df2 = pd.DataFrame(bigList)
    export_csv = df2.to_csv(fullCSV, mode="a", index=False, header=False)
    print("All new films added")
else:
    print("No new films to add")

data = pd.read_csv(fullCSV)
# dropping ALL duplicte values
data.drop_duplicates(subset="Movie", keep="last", inplace=True)
# remake the csv without duplicates
data.to_csv(fullCSV, index=False)


# export_csv = df.to_csv(fullCSV, mode="a", index=False, header=False)
