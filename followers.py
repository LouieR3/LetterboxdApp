from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
import pandas as pd
import time

start_time = time.time()
user = "zac_"
firstUrl = "https://letterboxd.com/" + user + "/"
# followURL = "https://letterboxd.com/cloakenswagger/following/"
source = requests.get(firstUrl).text
soup = BeautifulSoup(source, "lxml")
followList = []
followerList = []

following = 0
followers = 0
followingNum = soup.findAll("h4", attrs={"class", "statistic"})[
    3
].next_element.next_element.text
print(followingNum)
followingPages = int(followingNum) / 25
followingPages = int(followingPages)
print(str(followingPages))
followersNum = soup.findAll("h4", attrs={"class", "statistic"})[
    4
].next_element.next_element.text
followersNum = followersNum.replace(",", "")
print(followersNum)
followerPages = int(followersNum) / 25
followerPages = int(followerPages) + 1
print(str(followerPages))

count = 0
followURL = "https://letterboxd.com/" + user + "/following/"
source = requests.get(followURL).text
soup = BeautifulSoup(source, "lxml")
if followingPages == 0:
    page_link = soup.find("div", attrs={"class", "pagination"})

elif followingPages == 1:
    page_link = soup.find("div", attrs={"class", "pagination"})
    page = soup.find("a", attrs={"class", "next"})["href"]
    print(page)
    url = "https://letterboxd.com" + page
else:
    while count < followingPages:
        # page_link = soup.find("div", attrs={"class", "pagination"})
        # page = soup.find("a", attrs={"class", "next"})["href"]
        url = "https://letterboxd.com/" + user + "/following/page/" + str(count) + "/"
        # source = requests.get(url).text
        # soup = BeautifulSoup(source, "lxml")
        print(url)
        count += 1

# try:
#     page_link = soup.find("div", attrs={"class", "pagination"})
#     if soup.find("a", attrs={"class", "next"}):
#         page = str(page_link.a)
#         start = page.find('"/') + len('"')
#         end = page.find('">')
#         subs = page[start:end]
#         print(subs)
#         url = "https://letterboxd.com" + subs
# except:
#     page_link = ""

print("--- %s seconds ---" % (time.time() - start_time))
