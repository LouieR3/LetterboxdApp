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
file = "AllFilmscloakenswagger.csv"
fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)

pd.options.mode.chained_assignment = None

highest = df.sort_values(by=['Difference'])
high = highest.iloc[:15][['Movie', 'MyRating', 'LBRating', 'Difference']]
print(high)
print()
lowest = df.sort_values(by='Difference', ascending=False)
low = lowest.iloc[:15][['Movie', 'MyRating', 'LBRating', 'Difference']]
print(low)

print("--- %s seconds ---" % (time.time() - start_time))
