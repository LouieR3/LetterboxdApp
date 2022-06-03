from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
import pandas as pd
import time
start_time = time.time()

start = 15
end = 21
while start <= end:
    dataPath = "movies-of-20"
    file = dataPath + str(start) + ".csv"
    print("The list: " + dataPath + str(start))
    # print("Let's see your favorite length of movie...")
    count = 0
    total = 0
    totalLength = 0
    lenCount = 0
    df = pd.read_csv(file)
    for i in range(len(df)):
        rate = df["MyRating"].iloc[i]
        length = df["MovieLength"].iloc[i]
        if pd.notna(rate):
            myRate = float(rate)
            total += myRate
            count += 1
        if pd.notna(length):
            totalLength += length
            lenCount += 1

    mod = totalLength % 60
    hour = totalLength / 60
    hour = int(hour)
    finmod = ""
    if mod < 10:
        finmod = "0"+str(mod)
    else:
        finmod = str(mod)
    lenFloat = finmod[:2]
    lengthInHour = str(hour) + ":" + lenFloat

    finLen = totalLength / lenCount
    mod2 = finLen % 60
    hour2 = finLen / 60
    hour2 = int(hour2)
    finmod2 = ""
    if mod2 < 10:
        finmod2 = "0"+str(mod2)
    else:
        finmod2 = str(mod2)
    lenFloat2 = finmod2[:2]
    lengthInHour2 = str(hour2) + ":" + lenFloat2

    fin = total / count
    finFloat = "{:.2f}".format(fin)
    print("Average rating of this list is: " + str(finFloat))
    print("Total length of this list is: " + lengthInHour)
    print("Average movie length of this list is: " + str(lengthInHour2))
    print()
    start += 1