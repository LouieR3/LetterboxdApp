from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio

# import urllib2 
# import cookielib ## http.cookiejar in python3
# import mechanize
user = "goldfishbrain"
file = "AllFilms" + user + ".csv"
username = file.split(".cs")[0].split("AllFilms")[1]
print(username)

str = "Star Wars: Episode III - Revenge of the Sith"
newStr = str.replace("\xc2\xa0", " ")
print(str)
print(newStr)
print(str == newStr)

# list = "movies-of-2020"
# firstUrl = "https://letterboxd.com/cloakenswagger/films/"
# source = requests.get(firstUrl).text
# soup = BeautifulSoup(source, "lxml")
# listOfPage = []

# page_link = soup.findAll("li", attrs={"class", "paginate-page"})[-1]
# page = str(page_link.a)
# num_pages = int(page_link.find("a").text.replace(',', ''))
# checker = 1
# while num_pages > checker:
#     start = page.find('\"') + len('\"')
#     end = page.find('\">')
#     subs = page[start:end]
#     te = subs.split("page/")[0]
#     ttt = te + "page/" + str(num_pages)+ "/"
#     url = "https://letterboxd.com" + ttt
#     listOfPage.append(url)
#     num_pages -= 1
# listOfPage.append(firstUrl)
# listOfPage.reverse()

# print(listOfPage)
# tt = 127
# mod = tt % 60
# hour = tt / 60
# hour = int(hour)
# finmod = ""
# if mod < 10:
#     finmod = "0"+str(mod)
# print(str(hour) + " hours and " + str(mod) + " minutes")
# print(finmod)

# lanList =['Crime']

# lanString = ""
# if len(lanList) > 1:
#     lanString = ','.join(lanList)
# else:
#     lanString = lanList[0]

# print(lanString)