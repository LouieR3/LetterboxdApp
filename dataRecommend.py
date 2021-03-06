import pandas as pd
from operator import itemgetter
from ratings import ratings
from user import user
import unidecode
from bs4 import BeautifulSoup
import requests
import json
import re
import time
from tabulate import tabulate

start_time = time.time()

file = user()
df = pd.read_csv(file)

pd.options.mode.chained_assignment = None

# CHECKING FAVORITE GENRE AND RATING BY GENRE\
filmAverage = df["MyRating"].mean()
for i in range(len(df)):
    director = df["Director"].iloc[i]
    df.at[i, "Director"] = director
    rate = df["MyRating"].iloc[i]
# DataFrame for movies with unique genre
finalDF = df.Director.unique()
# print("=========")
finList = []
dList = ratings()
for mem in finalDF:
    # print(mem)
    cnt = 0
    finWeight = 0
    tot = 0
    # DataFrame for movies of just the current iteration genre
    xdf = df.loc[df["Director"] == mem]
    diff = xdf["Difference"].mean()
    diff = "{:.2f}".format(diff)
    for rate in dList:
        rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
        finWeight = (rateLen*rate[0]) * rate[1]
        cnt += finWeight
        tot += rateLen
    if tot > 1:
        fin = cnt / tot
        fin += (float(diff)/2)
        fin = fin * (1 + (tot/100))
        # ^ THIS SHOULD BE TOTAL WATCHED / TOTAL FILMS THEY HAVE THAT ARE DECENTLY WATCHED AND ACCOUNT FOR BAD RATINGS
        # higher total should mean difference is more legit and factored in more
        finFloat = "{:.2f}".format(fin)

        avg1 = xdf["MyRating"].mean()
        avg2 = "{:.2f}".format(avg1)
        avg = avg1
        avg += (float(diff)/2)
        avg = avg * (1 + (tot/50))
        # HIGHEST NUMBER IN LIST * 10 / 2
        finAvg = "{:.2f}".format(avg)

        if avg > filmAverage:
            finList.append(
                [mem, finFloat, avg2, finAvg, tot, diff])

sortList = sorted(finList, key=itemgetter(1), reverse=True)
df = pd.DataFrame(sortList)
df['Ranking'] = range(1, len(df) + 1)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3), reverse=True)

url = "https://letterboxd.com"
first20 = sortList[0:20]
recommendList = []
df2 = pd.read_csv(file)
for director in range(len(first20)):
    director = first20[director][0]
    unaccented_string = unidecode.unidecode(director)
    directorSplit = unaccented_string.replace(' ', '-').lower()
    directorSplit = directorSplit.replace('.', '').replace(',', '')
    urlTemp = "https://letterboxd.com/director/" + directorSplit + "/"
    source = requests.get(urlTemp).text
    soup = BeautifulSoup(source, "lxml")
    for movie in soup.find_all("li", class_="poster-container"):
        name = movie.find("img")
        movieName = name.attrs["alt"]

        div = movie.find("div")
        filmLink = div.attrs["data-film-slug"]
        filmURL = url + filmLink
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
                finmod = "0"+str(mod)
            else:
                finmod = str(mod)
            lengthInHour = str(hour) + ":" + finmod
        except:
            print(name)
            finalLen = 0
        detailsDiv = soupFilm.find(
            "script", type="application/ld+json").string
        start = detailsDiv.find("/* <![CDATA[ */") + len("/* <![CDATA[ */")
        end = detailsDiv.find("/* ]]> */")
        subs = detailsDiv[start:end]
        lttrboxdJSON = json.loads(subs)
        try:
            lbRating = lttrboxdJSON["aggregateRating"]["ratingValue"]
        except:
            lbRating = 0
        # print(lbRating)

        if "aggregateRating" in lttrboxdJSON:
            numReviews = lttrboxdJSON["aggregateRating"]["reviewCount"]
            numRatings = lttrboxdJSON["aggregateRating"]["ratingCount"]
        else:
            numReviews = 0
            numRatings = 0
        movieBool = df2["Movie"].eq(movieName).any()
        if finalLen > 60 and finalLen < 500 and lbRating > 3.0 and numRatings > 10000 and movieBool == False:
            languages = soupFilm.find("div", id="tab-details")
            lan = languages.find_all("a", href=re.compile("language"))
            lanList = []
            languageStr = ""
            for item in lan:
                lanList.append(item.text.strip())
            if len(lanList) > 1:
                languageStr = ','.join(lanList)
            else:
                languageStr = lanList[0]

            director = ""
            try:
                director = lttrboxdJSON["director"][0]["name"]
            except:
                director = ""

            release = lttrboxdJSON["releasedEvent"][0]["startDate"]

            genreString = ""
            genre_in_dict = "genre" in lttrboxdJSON
            if (genre_in_dict):
                genre = lttrboxdJSON["genre"]
                if len(genre) > 1:
                    genreString = ','.join(genre)
                else:
                    genreString = genre[0]
            else:
                genre = ""

            try:
                country = lttrboxdJSON["countryOfOrigin"][0]["name"]
            except:
                country = "N/A"

            recommendList.append([movieName, lbRating, finalLen, lengthInHour,
                                  languageStr, director, release, genreString, country, numReviews, numRatings])
sortList = sorted(recommendList, key=itemgetter(1), reverse=True)
df = pd.DataFrame(sortList)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3), reverse=True)
print(tabulate(sortList, headers=[
      "Movie",
      "Rating",
      "Length",
      "Length in hours",
      "Languages",
      "Director",
      'Release Year',
      'Genre',
      'Country',
      'Number of Reviews',
      'Number of Ratings']))

print("--- %s seconds ---" % (time.time() - start_time))
