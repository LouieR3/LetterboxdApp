from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio

import time
start_time = time.time()
# user = "goldfishbrain"
# user = "zacierka"
# user = "bluegrace11"
user = "cloakenswagger"
firstUrl = "https://letterboxd.com/" + user + "/watchlist/"
# list = "AllFilmActors"
list = "Watchlist" + user
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
csv_writer.writerow(['Movie', 'MyRating', 'LBRating', 'Difference', 'ReviewDate', 'MovieLength', 'LengthInHour',
                    'Languages', 'Director', 'ReleaseYear', 'Genre', 'Country', 'NumberOfReviews', 'NumberOfRatings', 'Actors'])
bigList = []
url = "https://letterboxd.com"
myUrl = "https://letterboxd.com/" + user
# myUrl = "https://letterboxd.com/cloakenswagger"
for link in listOfPage:
    source = requests.get(link).text
    soup = BeautifulSoup(source, "lxml")
    for movie in soup.find_all("li", class_="poster-container"):

        name = movie.find("img")
        movieName = name.attrs["alt"]

        div = movie.find("div")
        filmLink = div.attrs["data-film-slug"]
        filmURL = url + filmLink
        myFilmUrl = myUrl + filmLink
        myReview = requests.get(myFilmUrl).text
        myFilm = BeautifulSoup(myReview, "lxml")
        viewDate = "N/A"
        vv = ""
        TheDate = ""
        yr = ""
        rest = ""
        finalDate = ""
        try:
            viewDate = myFilm.find(
                "p", class_="view-date").find("a").next_sibling.next_element
            vv = str(viewDate)
            lenToUse = len(user)+27
            TheDate = vv[lenToUse:-9]
            yr = TheDate[:4]
            rest = TheDate[5:]
            finalDate = rest + "/" + yr
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
        detailsDiv = soupFilm.find(
            "script", type="application/ld+json").string
        start = detailsDiv.find("/* <![CDATA[ */") + len("/* <![CDATA[ */")
        end = detailsDiv.find("/* ]]> */")
        subs = detailsDiv[start:end]
        lttrboxdJSON = json.loads(subs)
        try:
            avgRate = lttrboxdJSON["aggregateRating"]["ratingValue"]
        except:
            avgRate = 0
        # print(avgRate)
        if finalLen > 60 and finalLen < 500 and avgRate > 0:
            languages = soupFilm.find("div", id="tab-details")
            lan = languages.find_all("a", href=re.compile("language"))
            lanList = []
            lanString = ""
            for item in lan:
                lanList.append(item.text.strip())
            if len(lanList) > 1:
                lanString = ','.join(lanList)
            else:
                lanString = lanList[0]

            director = ""
            try:
                director = lttrboxdJSON["director"][0]["name"]
            except:
                director = ""

            # GET ONLY CREDITED ACTORS BY A TAG
            actor = ""
            try:
                actor = lttrboxdJSON["actors"]
            except:
                actor = ""
            act1 = ""
            for act in range(len(actor)):
                if act == 0:
                    act1 = act1 + actor[act]["name"]
                else:
                    act1 = act1 + "," + actor[act]["name"]

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

            if "aggregateRating" in lttrboxdJSON:
                numReviews = lttrboxdJSON["aggregateRating"]["reviewCount"]
                numRatings = lttrboxdJSON["aggregateRating"]["ratingCount"]
            else:
                numReviews = 0
                numRatings = 0
            bigList.append([movieName, avgRate, finalDate, finalLen,
                            lengthInHour, lanList, director, release, genre, country, numReviews, numRatings, act1])
            csv_writer.writerow([movieName, avgRate, finalDate, finalLen, lengthInHour,
                                lanString, director, release, genreString, country, numReviews, numRatings, act1])
# print(bigList)
print("ALL DONE")
csv_file.close()
print("--- %s seconds ---" % (time.time() - start_time))
