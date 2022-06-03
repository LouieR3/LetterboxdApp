from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
import pandas as pd
import os
from datetime import date

import time

start_time = time.time()

# dataPath = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\DeltekMap\\DeltekMapScirpts\\LBCode"
dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
file = "AllFilms.csv"
fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)


df["ReviewDate"] = pd.to_datetime(df["ReviewDate"], format="%m/%d/%Y")
df.to_csv(fullCSV, index=False)
