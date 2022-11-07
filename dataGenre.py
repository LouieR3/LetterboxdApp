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

start_time = time.time()

dataPath = "C:\\Users\\louie\\Desktop\\repo\\LetterboxdApp"
# dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
# user = "goldfishbrain"
# user = "zacierka"
# user = "bluegrace11"
user = "cloakenswagger"
file = "AllFilms" + user + ".csv"
fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)

pd.options.mode.chained_assignment = None

# PERCENTAGE OF EACH RATING DISTRIBUTION
# DataFrame for movies with unique rating
lenDF = df.MyRating.unique()
sortList = sorted(lenDF, reverse=True)
dList = []
pnt = 1
for i in sortList:
    if pd.notna(i):
        num = df["MyRating"].value_counts(normalize=True)[i]
        numFloat = "{:.4f}".format(num)
        pct = float(numFloat)
        pnt -= pct
        numFloat2 = "{:.4f}".format(pnt)
        pnt = float(numFloat2)
        if pnt <= 0:
            pnt = 0.004
        fin = 0.5 + pnt
        if i == 4:
            fin -= 0.1

        # fin = pnt
        forOne = fin * i
        dList.append([i, fin, forOne])

lenDF = df[df["Genre"].notna()]
print(len(lenDF))
finList = []
# For each index in our final DataFrame
for i in range(len(lenDF)):
    # actor is a list of every actor in the current film
    genre = lenDF["Genre"].iloc[i].split(",")
    # for each actor in this film
    for a in genre:
        x = False
        if len(finList) > 0:
            for i in range(len(finList)):
                y = a in finList[i]
                if y == True:
                    x = True
        if x == True:
            break
        else:
            tot = 0
            avg = 0
            mid = a
            sub_df = lenDF[lenDF['Genre'].str.contains(mid, na=False)]
            if len(sub_df) > 3:
                diff = sub_df["Difference"].mean()
                diff = "{:.2f}".format(diff)
                cnt = 0
                finWeight = 0
                tot = 0
                for rate in dList:
                    rateLen = len(sub_df[(sub_df["MyRating"] == rate[0])])
                    finWeight = (rateLen*rate[0]) * rate[1]
                    cnt += finWeight
                    tot += rateLen
                if tot > 0:
                    fin = cnt / tot
                    fin += (float(diff)/2)
                    fin = fin * (1 + (tot/1000))
                    finFloat = "{:.2f}".format(fin)

                    avg1 = sub_df["MyRating"].mean()
                    avg2 = "{:.2f}".format(avg1)
                    avg = avg1
                    avg += (float(diff)/2)
                    avg = avg * (1 + (tot/2500))
                    finAvg = "{:.2f}".format(avg)

                    finList.append([a, finFloat, avg2, finAvg, tot, diff])

sortList = sorted(finList, key=itemgetter(1), reverse=True)
df = pd.DataFrame(sortList)
df['index'] = range(1, len(df) + 1)
# df.index += 1 
print(df)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3))

print(tabulate(sortList, headers=[
      'Genre', 'Weighted', 'Average', 'Weigthed 2', 'Total', 'Difference', 'Index']))

# THIS OPTION?
# https://letterboxd.com/cloakenswagger/films/ratings/with/actor/saoirse-ronan/by/entry-rating/

print("--- %s seconds ---" % (time.time() - start_time))
