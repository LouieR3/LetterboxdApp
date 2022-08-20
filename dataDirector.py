from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
import pandas as pd
import time
import os
from operator import itemgetter
from tabulate import tabulate
import unidecode
from ratings import ratings

start_time = time.time()

dataPath = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\LetterboxdApp"
# dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
# user = "goldfishbrain"
# user = "zacierka"
# user = "bluegrace11"
user = "cloakenswagger"
file = "AllFilms" + user + ".csv"
# file = "AllFilmsMike.csv"
fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)

pd.options.mode.chained_assignment = None

# CHECKING FAVORITE GENRE AND RATING BY GENRE\
filmAverage = df["MyRating"].mean()
for i in range(len(df)):
    director = df["Director"].iloc[i]
    df.at[i, "Director"] = director
    rate = df["MyRating"].iloc[i]
# DataFrame for movies with unique genre
finalDF = df.Director.unique()
finList = []
nwList = []
dList = ratings()
for mem in finalDF:
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
        avg = avg * (1 + (tot/100))
        # HIGHEST NUMBER IN LIST * 10 / 2
        finAvg = "{:.2f}".format(avg)

        if avg > filmAverage:
            finList.append(
                [mem, finFloat, avg2, finAvg, tot, diff])

sortList = sorted(finList, key=itemgetter(1), reverse=True)
df = pd.DataFrame(sortList)
df['index'] = range(1, len(df) + 1)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3), reverse=True)
print(tabulate(sortList, headers=[
      'Director', 'Weighted', 'Average', 'Weigthed 2', 'Total', 'Difference', 'Index']))

ndf = pd.read_csv(fullCSV)
df = ndf[ndf["MyRating"].notna()]
df2 = df["MyRating"].mean()
df2 = "{:.2f}".format(df2)
df3 = df["Difference"].mean()
df3 = "{:.2f}".format(df3)
print(len(sortList))

print("Average rating of your reviews: " + str(df2))
print("Average difference between you and Letterboxd in rating: " + str(df3))
# print("Average rating of the top 25 of this list is: " + str(fin2))
# print("Average rating of the middle of this list is: " + str(fin3))

print("--- %s seconds ---" % (time.time() - start_time))
