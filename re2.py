import pandas as pd
from operator import itemgetter
from ratings import ratings
from user import user
from callLength import lenMovies
from callGenre import genreMovies
from callLanguage import langMovies
from callDecade import decadeMovies
import unidecode
from bs4 import BeautifulSoup
import requests
import json
import re

lenList = lenMovies()
genreList = genreMovies()
genreList = pd.DataFrame(genreList)
genreList.columns = ["genre", "average"]
langList = langMovies()
langList = pd.DataFrame(langList)
langList.columns = ["language", "average"]
decList = decadeMovies()
decList = pd.DataFrame(decList)
decList.columns = ["decade", "average"]
file = user()
df = pd.read_csv(file)

pd.options.mode.chained_assignment = None

df2 = pd.read_csv(file)
df250 = pd.read_csv("Top250Films.csv")

cond = df250['Movie'].isin(df2['Movie'])
df250.drop(df250[cond].index, inplace = True)
print(len(df250))
print(df250)