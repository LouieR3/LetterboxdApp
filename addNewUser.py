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

user = "seanfennessey"
# https://letterboxd.com/seanfennessey/
firstUrl = "https://letterboxd.com/" + user + "/films/ratings/"
# list = "AllFilmActors"
list = "AllFilms" + user
source = requests.get(firstUrl).text
soup = BeautifulSoup(source, "lxml")
listOfPage = []

try:
    page_link = soup.findAll("li", attrs={"class", "paginate-page"})[-1]
    page = str(page_link.a)
    num_pages = int(page_link.find("a").text.replace(',', ''))
    checker = 1
    while num_pages > checker:
        start = page.find('\"') + len('\"')
        end = page.find('\">')
        subs = page[start:end]
        urlPart = subs.split("page/")[0]
        fullURL = urlPart + "page/" + str(num_pages) + "/"
        url = "https://letterboxd.com" + fullURL
        listOfPage.append(url)
        num_pages -= 1
except:
    page_link = ""

listOfPage.append(firstUrl)
listOfPage.reverse()
csv_file = open(list + '.csv', 'w', newline='', encoding='utf-8')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Movie', 'userRating', 'LBRating', 'Difference', 'ReviewDate', 'MovieLength', 'LengthInHour',
                    'Languages', 'Director', 'ReleaseYear', 'Genre', 'Country', 'NumberOfReviews', 'NumberOfRatings', 'Actors'])
bigList = []
url = "https://letterboxd.com"
userUrl = "https://letterboxd.com/" + user
# userUrl = "https://letterboxd.com/cloakenswagger"
for link in listOfPage:
    source = requests.get(link).text
    soup = BeautifulSoup(source, "lxml")
    for movie in soup.find_all("li", class_="poster-container"):
        # place = movie.find("p").text
        # print(place)
        name = movie.find("img")
        # print(name)
        movieName = name.attrs["alt"]
        # print(movieName)

        # print(movie.find("span", class_="rating").text)

        rating = movie.find("span", attrs={"class": "rating"})
        return_unrated = False
        format_float = 0
        if not rating:
            rating_val = ""
            format_float = ""
        else:
            rating_class = rating['class'][-1]
            rating_val = int(rating_class.split('-')[-1])/2

        # print("user rating is: " + rate)
        div = movie.find("div")
        filmLink = div.attrs["data-film-slug"]
        # print(filmLink)
        filmURL = url + filmLink
        userFilmUrl = userUrl + filmLink
        userReview = requests.get(userFilmUrl).text
        userFilm = BeautifulSoup(userReview, "lxml")
        viewDate = "N/A"
        viewDateStr = ""
        TheDate = ""
        year = ""
        monthDay = ""
        finalDate = ""
        try:
            viewDate = userFilm.find(
                "p", class_="view-date").find("a").next_sibling.next_element
            viewDateStr = str(viewDate)
            lenToUse = len(user)+27
            TheDate = viewDateStr[lenToUse:-9]
            year = TheDate[:4]
            monthDay = TheDate[5:]
            finalDate = monthDay + "/" + year
        except:
            viewDate = "N/A"
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
        avgRate = -1
        
        if finalLen > 60 and finalLen < 500:
            languages = soupFilm.find("div", id="tab-details")
            lan = languages.find_all("a", href=re.compile("language"))
            lanList = []
            lanString = ""
            for item in lan:
                lanList.append(item.text.strip())
            if len(lanList) > 1:
                lanString = ','.join(lanList)
                lanString = str(lanString.split(',',1)[1])
            else:
                lanString = lanList[0]

            # print("----")
            detailsDiv = soupFilm.find(
                "script", type="application/ld+json").string
            start = detailsDiv.find("/* <![CDATA[ */") + len("/* <![CDATA[ */")
            end = detailsDiv.find("/* ]]> */")
            subs = detailsDiv[start:end]
            lttrboxdJSON = json.loads(subs)
            director = ""
            try:
                director = lttrboxdJSON["director"][0]["name"]
            except:
                director = ""
            
            try:
                avgRate = lttrboxdJSON["aggregateRating"]["ratingValue"]
            except:
                print(filmURL)
            
            if avgRate != -1:
                # GET ONLY CREDITED ACTORS BY A TAG
                actors = ""
                try:
                    actors = lttrboxdJSON["actors"]
                except:
                    actors = ""
                act1 = ""
                limit = 0
                if len(actors) >= 20 and len(actors) < 27:
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
                if format_float == 0:
                    diff = rating_val - avgRate
                    format_float = "{:.2f}".format(diff)
                numReviews = lttrboxdJSON["aggregateRating"]["reviewCount"]
                numRatings = lttrboxdJSON["aggregateRating"]["ratingCount"]

                # print()
                bigList.append([movieName, rating_val, avgRate, format_float, finalDate, finalLen,
                                lengthInHour, lanList, director, release, genre, country, numReviews, numRatings, act1])
                csv_writer.writerow([movieName, rating_val, avgRate, format_float, finalDate, finalLen, lengthInHour,
                                    lanString, director, release, genreString, country, numReviews, numRatings, act1])
        else:
            print(name)
# print(bigList)
print("ALL DONE")
csv_file.close()
print("--- %s seconds ---" % (time.time() - start_time))