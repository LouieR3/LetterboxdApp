"""Letterboxd Stats: entry point (Streamlit Community Cloud runs this file)."""
import streamlit as st

from app import ui

st.set_page_config(page_title="Letterboxd Stats", page_icon="🎬", layout="wide")

pages = {
    "Your taste": [
        st.Page("app/views/overview.py", title="Overview", icon=":material/insights:", default=True),
        st.Page("app/views/people.py", title="Directors & actors", icon=":material/groups:"),
        st.Page("app/views/genres.py", title="Genres & themes", icon=":material/category:"),
        st.Page("app/views/eras.py", title="Eras, runtimes & languages", icon=":material/schedule:"),
        st.Page("app/views/films.py", title="All films", icon=":material/movie:"),
    ],
    "Discover": [
        st.Page("app/views/recommend.py", title="Recommendations", icon=":material/auto_awesome:"),
        st.Page("app/views/friends.py", title="Friends", icon=":material/diversity_3:"),
    ],
}

nav = st.navigation(pages)
ui.sidebar()
nav.run()
