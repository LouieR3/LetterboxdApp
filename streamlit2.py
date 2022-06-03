import streamlit as st
import pandas as pd
import pydeck as pdk
from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
import time
import os
from operator import itemgetter
from urllib.error import URLError
from streamlit_observable import observable
import time
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
import numpy as np
from ratings import ratings
import director
import actors
import intro
import length
import genre

st.set_page_config(page_title="Letterboxd Stats", layout="wide")

PAGES = {
    "Intro": intro,
    "Actors": actors,
    "Directors": director,
    "By Length": length,
    "Genre": genre
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

# pr = df.profile_report()
# st_profile_report(pr)
