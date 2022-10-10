import streamlit as st
import pandas as pd
# import pydeck as pdk
from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
# from operator import itemgetter
# from urllib.error import URLError
# from streamlit_observable import observable
# import pandas_profiling
# from streamlit_pandas_profiling import st_profile_report
import numpy as np
from ratings import ratings
import director
import actors
# import actors2
import intro
import length
import genre
import country
import decade
import year
import language
import unidecode
import recommender
import recommender2
import fantasyfootball
from espn_api.football import League

st.set_page_config(page_title="Letterboxd Stats", layout="wide")

PAGES = {
    "Intro": intro,
    "Actors": actors,
    # "Actors2": actors2,
    "Directors": director,
    "By Length": length,
    "Genre": genre,
    "Country": country,
    "Decade": decade,
    "Year": year,
    "Language": language,
    "Recommendation": recommender,
    "Recommendation by Top 250": recommender2,
    "Fantasy Football": fantasyfootball
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

# pr = df.profile_report()
# st_profile_report(pr)
