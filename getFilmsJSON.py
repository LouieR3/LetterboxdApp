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
user = "bluegrace11"
# user = "cloakenswagger"
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
# csv_file = open(list + '.csv', 'w', newline='', encoding='utf-8')

# csv_writer = csv.writer(csv_file)
# csv_writer.writerow(['Movie', 'MyRating', 'LBRating', 'Difference', 'ReviewDate', 'MovieLength', 'LengthInHour',
#                     'Languages', 'Director', 'ReleaseYear', 'Genre', 'Country', 'NumberOfReviews', 'NumberOfRatings', 'Actors'])
userData = {}
url = "https://letterboxd.com"
myUrl = "https://letterboxd.com/" + user
for link in listOfPage:
    source = requests.get(link).text
    soup = BeautifulSoup(source, "lxml")
    for movie in soup.find_all("li", class_="poster-container"):
        quickList = []
        # Movie Name
        name = movie.find("img")
        movieName = name.attrs["alt"]
        # -------------------------------------

        # Movie Rating
        rating = movie.find("span", attrs={"class": "rating"})
        return_unrated = False
        difference = 0
        if not rating:
            rating_val = ""
            difference = ""
        else:
            rating_class = rating['class'][-1]
            rating_val = int(rating_class.split('-')[-1])/2
        # -------------------------------------

        # The View Date
        div = movie.find("div")
        filmLink = div.attrs["data-film-slug"]
        filmURL = url + filmLink
        myFilmUrl = myUrl + filmLink
        myReview = requests.get(myFilmUrl).text
        myFilm = BeautifulSoup(myReview, "lxml")
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
        # -------------------------------------

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
        if finalLen > 60 and finalLen < 500:
            # Languages
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
            # -------------------------------------

            detailsDiv = soupFilm.find(
                "script", type="application/ld+json").string
            start = detailsDiv.find("/* <![CDATA[ */") + len("/* <![CDATA[ */")
            end = detailsDiv.find("/* ]]> */")
            subs = detailsDiv[start:end]
            lttrboxdJSON = json.loads(subs)

            # Director
            director = ""
            try:
                director = lttrboxdJSON["director"][0]["name"]
            except:
                director = ""
            # -------------------------------------

            # GET ONLY CREDITED ACTORS BY A TAG
            actors = ""
            try:
                actors = lttrboxdJSON["actors"]
            except:
                actors = ""
            act1 = ""
            for element in actors:
                del element['@type']
                del element['sameAs']
            limit = 0
            # actorsLen = lttrboxdJSON['actors']
            print(len(actors))
            if len(actors) >= 20 and len(actors) < 27:
                limit = len(actors)*0.6
            elif len(actors) >= 27:
                limit = len(actors)*0.4
            else:
                limit = len(actors)
            limit = round(limit)
            i = len(actors)-1
            while i >= limit:
                del actors[i]
                i -= 1
            # -------------------------------------

            release = lttrboxdJSON["releasedEvent"][0]["startDate"]

            # Genre
            genreString = ""
            genre_in_dict = "genre" in lttrboxdJSON
            if (genre_in_dict):
                genre = lttrboxdJSON["genre"]
                # if len(genre) > 1:
                #     genreString = ','.join(genre)
                # else:
                #     genreString = genre[0]
            else:
                genre = ""
            # -------------------------------------

            # Country
            try:
                country = lttrboxdJSON["countryOfOrigin"][0]["name"]
            except:
                country = "N/A"
            # -------------------------------------

            # Letterboxd Rating
            avgRate = lttrboxdJSON["aggregateRating"]["ratingValue"]
            if difference == 0:
                diff = rating_val - avgRate
                difference = "{:.2f}".format(diff)
            # -------------------------------------

            # Rating and Review Numbers
            numReviews = lttrboxdJSON["aggregateRating"]["reviewCount"]
            numRatings = lttrboxdJSON["aggregateRating"]["ratingCount"]
            # -------------------------------------

            userData['MovieName'] = movieName
            userData['MyRating'] = rating_val
            userData['LBRating'] = avgRate
            userData['Difference'] = difference
            userData['ReviewDate'] = finalDate
            userData['MovieLength'] = finalLen
            userData['LengthInHour'] = lengthInHour
            userData['Languages'] = lanString
            userData['Director'] = director
            userData['ReleaseYear'] = release
            userData['Genre'] = genre
            userData['Country'] = country
            userData['NumberOfReviews'] = numReviews
            userData['NumberOfRatings'] = numRatings
            userData['Actors'] = actors

            # print()
            # csv_writer.writerow(['Movie', 'MyRating', 'LBRating', 'Difference', 'ReviewDate', 'MovieLength', 'LengthInHour',
            #                     'Languages', 'Director', 'ReleaseYear', 'Genre', 'Country', 'NumberOfReviews', 'NumberOfRatings', 'Actors'])
            # csv_writer.writerow([movieName, rating_val, avgRate, difference, finalDate, finalLen, lengthInHour,
            #                     lanString, director, release, genreString, country, numReviews, numRatings, act1])
        else:
            print(name)
print("ALL DONE")
# csv_file.close()
print("--- %s seconds ---" % (time.time() - start_time))
