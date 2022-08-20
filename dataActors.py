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

dataPath = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\LetterboxdApp"
# dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
# user = "goldfishbrain"
# user = "zacierka"
# user = "bluegrace11"
# user = "gr8escape10"
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

filmAverage = df["MyRating"].mean()
# DataFrame for movies within our length with a rating
lenDF = df[df["Actors"].notna()]
print(len(lenDF))
lenDF = lenDF[lenDF["Genre"].str.contains("Documentary") == False]
print(len(lenDF))
finList = []
# For each index in our final DataFrame
for i in range(len(lenDF)):
    # actor is a list of every actor in the current film
    actors = lenDF["Actors"].iloc[i].split(",")
    # for each actor in this film
    for a in actors:
        inList = False
        # if the list isn't empty
        if len(finList) > 0:
            # for each list in the list
            for i in range(len(finList)):
                # check if actor is in that list already and if true set the checker to true
                y = a in finList[i]
                if y == True:
                    inList = True
        if inList != True and (" " in a):
            tot = 0
            avg = 0
            mid = a + ","
            sub_df = lenDF[lenDF["Actors"].str.contains(mid, na=False)]
            if len(sub_df) > 2:
                totalCount = 0
                for i in range(len(sub_df)):
                    subActor = sub_df["Actors"].iloc[i].split(",")
                    count = 1
                    for actor in subActor:
                        if a == actor:
                            totalCount += count
                            break
                        count += 1
                try:
                    # finMult = (len(sub_df) / totalCount)*2
                    finMult = len(sub_df) / totalCount
                except:
                    finMult = 0
                if finMult < 0.1:
                    break
                diff = sub_df["Difference"].mean()
                diff = "{:.2f}".format(diff)
                cnt = 0
                finWeight = 0
                tot = 0
                for rate in dList:
                    rateLen = len(sub_df[(sub_df["MyRating"] == rate[0])])
                    finWeight = (rateLen * rate[0]) * rate[1]
                    cnt += finWeight
                    tot += rateLen
                if tot > 0:
                    fin = cnt / tot
                    fin += float(diff) / 2
                    fin = max(fin, 0.5)
                    fin = fin * (1 + (tot / 100))
                    # finFloat += finMult
                    fin *= 1 + finMult
                    finFloat = fin / 1.75
                    finFloatStr = "{:.2f}".format(finFloat)

                    avg1 = sub_df["MyRating"].mean()
                    avg2 = "{:.2f}".format(avg1)
                    avg = avg1
                    avg += float(diff)
                    avg = avg * (1 + (tot / 50))
                    # HIGHEST NUMBER IN LIST * 10 / 2
                    avg *= 1 + finMult
                    finAv1 = avg / 1.75
                    finAvg = "{:.2f}".format(finAv1)

                    if finAv1 > 2.8:
                        finList.append(
                            [a, finFloatStr, avg2, finAvg, avg, tot, diff, finMult]
                        )
                    # if finFloat > filmAverage:
                    #     finList.append(
                    #         [a, finFloatStr, avg2, finAvg, tot, diff, finMult])
sortList = sorted(finList, key=itemgetter(1), reverse=True)
df = pd.DataFrame(sortList)
df["index"] = range(1, len(df) + 1)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3), reverse=True)
print(
    tabulate(
        sortList,
        headers=[
            "Actor",
            "Weighted",
            "Average",
            "Weigthed 2",
            "Without Divide",
            "Total",
            "Difference",
            "Billing Score",
            "Index",
        ],
    )
)
print(len(sortList))
# THIS OPTION?
# https://letterboxd.com/cloakenswagger/films/ratings/with/actor/saoirse-ronan/by/entry-rating/

# NEED TO ACCOUNT FOR % OF FILMS WATCHED OF ACTOR

print("--- %s seconds ---" % (time.time() - start_time))
