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

start_time = time.time()

dataPath = "C:\\Users\\louie\\Desktop\\repo\\LetterboxdApp"
# dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
file = "AllFilms.csv"
fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)

pd.options.mode.chained_assignment = None

# PERCENTAGE OF EACH RATING DISTRIBUTION
# DataFrame for movies with unique rating
lenDF = df.MyRating.unique()
ratingList = []
for i in lenDF:
    if pd.notna(i):
        num = df["MyRating"].value_counts(normalize=True)[i] * 100
        numFloat = "{:.2f}".format(num)
        pct = (10 * i) - float(numFloat)
        forOne = pct * i
        ratingList.append([i, pct, forOne])
        # print(str(i) + " " + str(numFloat) + " " + str(pct))
sortList = sorted(ratingList, key=itemgetter(0))
for x in sortList:
    print(str(x[0]) + " : " + str(x[1]) + " : " + str(x[2]))

# CHECKING FAVORITE RELEASE YEAR / FAVORITE DECADE / NUMBERS BY YEAR / AVERAGE YEAR
cnt = 0
start = 60
limit = 500
# DataFrame for movies within our length
lenDF = df[(df["MovieLength"] >= start) & (df["MovieLength"] < limit)]
for i in range(len(df)):
    if pd.notna(df["Genre"].iloc[i]):
        year = df["ReleaseYear"].iloc[i]
        lenDF.at[i, "ReleaseYear"] = year
        rate = df["MyRating"].iloc[i]
# DataFrame for movies with unique genre
finalDF = lenDF.ReleaseYear.unique()
print("=========")
finList = []
nwList = []
for mem in finalDF:
    # print(mem)
    cnt = 0
    finWeight = 0
    tot = 0
    # DataFrame for movies of just the current iteration genre
    # Weighted average is too high for bad movies like 2.0 Uncle Boonme
    xdf = lenDF.loc[lenDF["ReleaseYear"] == mem]
    for rate in ratingList:
        rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
        finWeight = rateLen * rate[1]
        cnt += finWeight
        tot += rateLen
    if tot > 0:
        fin = cnt / tot
        finFloat = "{:.2f}".format(fin)
        finFloat = (float(finFloat) * rate[0] * 0.075) / 2
        finFloat = "{:.2f}".format(finFloat)
        finList.append([mem, finFloat, tot])
    count = 0
    total = 0
    for i in range(len(xdf)):
        rate = xdf["MyRating"].iloc[i]
        if pd.notna(rate):
            count += 1
            total += rate
    # print(xdf["MyRating"].value_counts())
    if count > 0:
        fin = total / count
        finFloat = "{:.2f}".format(fin)
        nwList.append([mem, finFloat, count])
    # print("---------")
sortList = sorted(nwList, key=itemgetter(1))
count = 0
for set in sortList:
    for x in finList:
        if set[0] == x[0]:
            print(
                str(set[0])[:4]
                + " movies weighted average: "
                + str(x[1])
                + " non-weight average: "
                + str(set[1])
                + " | # of movies: "
                + str(set[2])
            )
            count += set[2]
    # i = 0
    # while i < len(nwList):
    #     if set[0]


# CHECKING FAVORITE LANGUAGE AND RATING BY LANGUAGE
start = 60
limit = 500
# DataFrame for movies within our length
lenDF = df[(df["MovieLength"] >= start) & (df["MovieLength"] < limit)]
for i in range(len(df)):
    if df["Languages"].iloc[i] != "No spoken language":
        language = df["Languages"].iloc[i].split(",")[0]
        lenDF.at[i, "Languages"] = language
        rate = df["MyRating"].iloc[i]
# DataFrame for movies with unique language
finalDF = lenDF.Languages.unique()
print("=========")
finList = []
nwList = []
for mem in finalDF:
    # print(mem)
    cnt = 0
    finWeight = 0
    tot = 0
    # DataFrame for movies of just the current iteration language
    # Weighted average is too high for bad movies like 2.0 Uncle Boonme
    xdf = lenDF.loc[lenDF["Languages"] == mem]
    for rate in ratingList:
        rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
        finWeight = rateLen * rate[1]
        cnt += finWeight
        tot += rateLen
    if tot > 0:
        fin = cnt / tot
        finFloat = "{:.2f}".format(fin)
        finFloat = (float(finFloat) * rate[0] * 0.075) / 2
        finFloat = "{:.2f}".format(finFloat)
        finList.append([mem, finFloat, tot])
    else:
        print("There were no movies in : " + str(mem))
    count = 0
    total = 0
    for i in range(len(xdf)):
        rate = xdf["MyRating"].iloc[i]
        if pd.notna(rate):
            count += 1
            total += rate
    # print(xdf["MyRating"].value_counts())
    if count > 0:
        fin = total / count
        finFloat = "{:.2f}".format(fin)
        nwList.append([mem, finFloat, count])
    # print("---------")
sortList = sorted(finList, key=itemgetter(1))
# for set in sortList:
#     for x in nwList:
#         if set[0] == x[0]:
#             print(
#                 str(set[0])
#                 + " movies weighted average: "
#                 + str(set[1])
#                 + " non-weight average: "
#                 + str(x[1])
#                 + " | # of movies: "
#                 + str(set[2])
#             )
# i = 0
# while i < len(nwList):
#     if set[0]

# CHECKING FAVORITE GENRE AND RATING BY GENRE
start = 60
limit = 500
# DataFrame for movies within our length
lenDF = df[(df["MovieLength"] >= start) & (df["MovieLength"] < limit)]
for i in range(len(df)):
    if pd.notna(df["Genre"].iloc[i]):
        genre = df["Genre"].iloc[i].split(",")[0]
        lenDF.at[i, "Genre"] = genre
        rate = df["MyRating"].iloc[i]
# DataFrame for movies with unique genre
finalDF = lenDF.Genre.unique()
print("=========")
finList = []
nwList = []
for mem in finalDF:
    # print(mem)
    cnt = 0
    finWeight = 0
    tot = 0
    # DataFrame for movies of just the current iteration genre
    # Weighted average is too high for bad movies like 2.0 Uncle Boonme
    xdf = lenDF.loc[lenDF["Genre"] == mem]
    for rate in ratingList:
        rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
        finWeight = rateLen * rate[1]
        cnt += finWeight
        tot += rateLen
    if tot > 0:
        fin = cnt / tot
        finFloat = "{:.2f}".format(fin)
        finFloat = (float(finFloat) * 0.1) / 2
        finFloat = "{:.2f}".format(finFloat)
        finList.append([mem, finFloat, tot])
    count = 0
    total = 0
    for i in range(len(xdf)):
        rate = xdf["MyRating"].iloc[i]
        if pd.notna(rate):
            count += 1
            total += rate
    # print(xdf["MyRating"].value_counts())
    if count > 0:
        fin = total / count
        finFloat = "{:.2f}".format(fin)
        nwList.append([mem, finFloat, count])
    # print("---------")
sortList = sorted(nwList, key=itemgetter(1))
count = 0
for set in sortList:
    for x in finList:
        if set[0] == x[0]:
            # print(
            #     str(set[0])
            #     + " movies weighted average: "
            #     + str(x[1])
            #     + " non-weight average: "
            #     + str(set[1])
            #     + " | # of movies: "
            #     + str(set[2])
            # )
            count += set[2]
    # i = 0
    # while i < len(nwList):
    #     if set[0]

print("--- %s seconds ---" % (time.time() - start_time))
