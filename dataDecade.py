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

finalDF = df.ReleaseYear.unique()
decList = []
for mem in finalDF:
    y = str(mem)
    x = y[:3]
    if x not in decList:
        decList.append(x)
finList = []
nwList = []

for mem in decList:
    df['ReleaseYear'] = df['ReleaseYear'].astype("string")
    cnt = 0
    finWeight = 0
    tot = 0
    otherTOT = 0
    # DataFrame for movies of just the current iteration genre
    xdf = df.loc[df["ReleaseYear"].str.startswith(mem, na=False)]
    diff = xdf["Difference"].mean()
    diff = "{:.2f}".format(diff)
    for rate in dList:
        rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
        finWeight = (rateLen*rate[0]) * rate[1]
        cnt += finWeight
        tot += rateLen
    if tot > 0:
        fin = cnt / tot
        fin = fin * (1 + (tot/1000))
        fin += (float(diff)/2)
        finFloat = "{:.2f}".format(fin)
        s = mem + "0's"

        avg1 = xdf["MyRating"].mean()
        avg2 = "{:.2f}".format(avg1)
        avg = avg1
        avg += (float(diff)/2)
        avg = avg * (1 + (tot/1700))
        # HIGHEST NUMBER IN LIST * 10 / 2
        finAvg = "{:.2f}".format(avg)

        finList.append([s, finFloat, avg2, finAvg, tot, diff])

sortList = sorted(finList, key=itemgetter(1), reverse=True)
df = pd.DataFrame(sortList)
df['index'] = range(1, len(df) + 1)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3))
print(tabulate(sortList, headers=[
      'Decade', 'Weighted', 'Average', 'Weigthed 2', 'Total', 'Difference', 'Index']))

print("--- %s seconds ---" % (time.time() - start_time))
