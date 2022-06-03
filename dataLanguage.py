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

dataPath = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\DeltekMap\\DeltekMapScirpts\\LBCode"
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
        # if i == 4.5:
        #     fin -= 0.2
        # if i == 5:
        #     fin -= 0.2
        forOne = fin * i
        dList.append([i, fin, forOne])

lenDF = df[~df["Languages"].str.contains("No spoken language")]
for i in range(len(df)):
    language = df["Languages"].iloc[i].split(",")[0]
    lenDF.at[i, "Languages"] = language
    rate = df["MyRating"].iloc[i]
# DataFrame for movies with unique language
finalDF = lenDF.Languages.unique()
finList = []
nwList = []
highest = 0
for mem in finalDF:
    # print(mem)
    cnt = 0
    finWeight = 0
    tot = 0
    # DataFrame for movies of just the current iteration language
    # Weighted average is too high for bad movies like 2.0 Uncle Boonme
    xdf = lenDF.loc[lenDF["Languages"] == mem]
    diff = xdf["Difference"].mean()
    diff = "{:.2f}".format(diff)
    for rate in dList:
        rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
        finWeight = (rateLen*rate[0]) * rate[1]
        cnt += finWeight
        tot += rateLen
    if tot > 0:
        fin = cnt / tot
        fin += (float(diff)/2)
        fin = fin * (1 + (tot/1000))
        fin = max(fin, 0.5)
        finFloat = "{:.2f}".format(fin)
        avg1 = xdf["MyRating"].mean()
        avg2 = "{:.2f}".format(avg1)
        avg = avg1
        avg += (float(diff)/2)
        avg = avg * (1 + (tot/4700))
        # HIGHEST NUMBER IN LIST * 10 / 2
        finAvg = "{:.2f}".format(avg)
        finList.append([mem, finFloat, avg2, finAvg, tot, diff])
    # print("---------")
sortList = sorted(finList, key=itemgetter(1), reverse=True)
df = pd.DataFrame(sortList)
df['index'] = range(1, len(df) + 1)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3))
print(tabulate(sortList, headers=[
      'Language', 'Weighted', 'Average', 'Weigthed 2', 'Total', 'Difference', 'Index']))


print("--- %s seconds ---" % (time.time() - start_time))
