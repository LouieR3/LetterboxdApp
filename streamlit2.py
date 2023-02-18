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



st.set_page_config(page_title="Letterboxd Stats", layout="wide")

PAGES = {
    "Home": intro,
    "Your Favorite Actors": actors,
    "Your Favorite Directors": director,
    "Your Favorite Movies By Length": length,
    "Your Favorite Genres": genre,
    "Your Favorite Decades": decade,
    "Your Favorite Languages": language,
    # "Your Favorite Country": country,
    # "Your Favorite Year": year,
    "Recommendations All": recommender,
    "Recommendations": recommender2
}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

# pr = df.profile_report()
# st_profile_report(pr)
