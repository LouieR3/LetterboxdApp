from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio

# import urllib2 
# import cookielib ## http.cookiejar in python3
# import mechanize

import time
start_time = time.time()

# list = "movies-of-2022"
# firstUrl = "https://letterboxd.com/cloakenswagger/list/" + list + "/"
firstUrl = "https://letterboxd.com/cloakenswagger/films/"
list = "AllFilms"
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
        te = subs.split("page/")[0]
        ttt = te + "page/" + str(num_pages)+ "/"
        url = "https://letterboxd.com" + ttt
        listOfPage.append(url)
        num_pages -= 1
except:
    page_link = ""

listOfPage.append(firstUrl)
listOfPage.reverse()
csv_file = open(list + '.csv', 'w', newline='', encoding='utf-8')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Movie', 'MyRating', 'LBRating', 'Difference', 'ReviewDate', 'MovieLength', 'LengthInHour', 'Languages', 'Director', 'ReleaseYear', 'Genre', 'Country', 'NumberOfReviews', 'NumberOfRatings'])
bigList = []
url = "https://letterboxd.com"
myUrl = "https://letterboxd.com/cloakenswagger"
for link in listOfPage:
    source = requests.get(link).text
    soup = BeautifulSoup(source, "lxml")
    for movie in soup.find_all("li", class_="poster-container"):
        place = movie.find("p").text
        # print(place)
        name = movie.find("img")
        movieName = name.attrs["alt"]
        print(movieName)
        rating = movie.attrs["data-owner-rating"]
        print(rating)
        rate = int(rating) / 2
        diff = rate - avgRate
        format_float = "{:.2f}".format(diff)
        # print("My rating is: " + rate)
        div = movie.find("div")
        filmLink = div.attrs["data-film-slug"]
        # print(filmLink)
        filmURL = url + filmLink
        # print(filmURL)
        myFilmUrl = myUrl + filmLink
        myReview = requests.get(myFilmUrl).text
        myFilm = BeautifulSoup(myReview, "lxml")
        viewDate = "N/A"
        vv=""
        TheDate=""
        yr=""
        rest=""
        finalDate=""
        try:
            viewDate = myFilm.find("p", class_="view-date").find("a").next_sibling.next_element
            # print(viewDate)
            vv = str(viewDate)
            TheDate = vv[41:-9]
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
            finalLen = "N/A"
        # print("Number of minutes: " + str(lengthOfMovie))
        languages = soupFilm.find("div", id="tab-details")
        lan = languages.find_all("a", href=re.compile("language"))
        # print("Languages:")
        lanList = []
        lanString = ""
        for item in lan:
            lanList.append(item.text.strip())
        if len(lanList) > 1:
            lanString = ','.join(lanList)
        else:
            lanString = lanList[0]
        
        # print("----")
        detailsDiv = soupFilm.find("script", type="application/ld+json").string
        start = detailsDiv.find("/* <![CDATA[ */") + len("/* <![CDATA[ */")
        end = detailsDiv.find("/* ]]> */")
        subs = detailsDiv[start:end]
        y = json.loads(subs)
        director = ""
        try:
            director = y["director"][0]["name"]
        except:
            director = ""
        # print(director)
        release = y["releasedEvent"][0]["startDate"]
        # print(release)
        genre = y["genre"]
        genreString = ""

        if len(genre) > 1:
            genreString = ','.join(genre)
        else:
            genreString = genre[0]
        # print(genre)
        try:
            country = y["countryOfOrigin"][0]["name"]
        except:
            country = "N/A"
        # print(country)
        # print("My rating is: " + str(rate))
        avgRate = y["aggregateRating"]["ratingValue"]
        # print(avgRate)
        numReviews = y["aggregateRating"]["reviewCount"]
        # print("Number of reviews: " + str(numReviews))
        numRatings = y["aggregateRating"]["ratingCount"]
        # print("Number of ratings: " + str(numRatings))
        
        # print(subs)
        # detailsDiv = soupFilm.find("div", {"id": "tab-details"}).text
        # print(detailsDiv)
        # print(movie)
        # headline = movie.h2.a.text
        # print(headline)

        # print()
        # bigList.append([movieName, rate, avgRate, format_float, finalDate, finalLen, lengthInHour, lanList, director, release, genre, country, numReviews, numRatings])
        csv_writer.writerow([movieName, rate, avgRate, format_float, finalDate, finalLen, lengthInHour, lanString, director, release, genreString, country, numReviews, numRatings])
# print(bigList)

count = 0
for mem in bigList:
    num = mem[1]
    if num != "N/A":
        count += num
fin = count / len(bigList)

count2 = 0
ccc = 0
hardStop=25
while count2 < hardStop:
    num = bigList[count2][1]
    if num != "N/A":
        ccc += num
    count2 += 1
fin2 = ccc / hardStop

percent = len(bigList)*0.05
count3 = 0
ccc = 0
total = len(bigList) - (percent*2)
while count3 + percent < len(bigList) - percent:
    num = bigList[count3][1]
    if num != "N/A":
        ccc += num
    count3 += 1
fin3 = ccc / total
print("Average rating of this list is: " + str(fin))
print("Average rating of the top 25 of this list is: " + str(fin2))
print("Average rating of the middle of this list is: " + str(fin3))
print("--- %s seconds ---" % (time.time() - start_time))
csv_file.close()
