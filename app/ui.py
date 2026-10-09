"""Shared look and feel: colours, the user picker, headers, and small chart helpers."""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from app import data

GREEN, ORANGE, BLUE = "#00E054", "#FF8000", "#40BCF4"
MUTED = "#8899AA"
DIVERGING = alt.Scale(scheme="redyellowgreen", domainMid=0)

CSS = """
<style>
  .block-container {padding-top: 2rem; max-width: 1400px;}
  [data-testid="stMetric"] {background: var(--secondary-background-color); border-radius: 10px; padding: 14px 16px;}
  [data-testid="stMetricLabel"] p {font-size: 0.8rem; text-transform: uppercase; letter-spacing: .06em; opacity: .75;}
  .lb-sub {opacity: .7; margin-top: -0.6rem; margin-bottom: 1.2rem;}
  .lb-tag {display:inline-block; padding:2px 10px; margin:2px 4px 2px 0; border-radius:999px;
           background: var(--secondary-background-color); font-size: .85rem;}
</style>
"""


def setup() -> str:
    """Called at the top of every page: shared styling; returns the selected username."""
    st.markdown(CSS, unsafe_allow_html=True)
    return st.session_state.user


def sidebar() -> None:
    """The user picker. Lives in the entry script so the choice persists across pages."""
    users = data.list_users()
    if st.session_state.get("user") not in users:
        wanted = st.query_params.get("user")
        st.session_state.user = wanted if wanted in users else users[0]
    with st.sidebar:
        st.selectbox("Whose films?", users, key="user")
        st.query_params["user"] = st.session_state.user
        df = data.load_user(st.session_state.user)
        st.caption(f"{len(df):,} films · {df['MyRating'].notna().sum():,} rated")
        st.link_button("Open on Letterboxd ↗", f"https://letterboxd.com/{st.session_state.user}/",
                       use_container_width=True)


def header(title: str, subtitle: str) -> None:
    st.title(title)
    st.markdown(f"<p class='lb-sub'>{subtitle}</p>", unsafe_allow_html=True)


def stars(x) -> str:
    return "–" if pd.isna(x) else f"★ {x:.1f}"


def tags(items) -> None:
    st.markdown("".join(f"<span class='lb-tag'>{i}</span>" for i in items), unsafe_allow_html=True)


def needs_ratings(df: pd.DataFrame, minimum: int = 5) -> bool:
    if df["MyRating"].notna().sum() < minimum:
        st.info("Not enough rated films for this view yet.")
        return False
    return True


def taste_bar(table: pd.DataFrame, label: str, n: int = 20, height: int | None = None) -> alt.Chart:
    """Horizontal bars of taste score, coloured by average rating."""
    t = table.head(n)
    return alt.Chart(t).mark_bar(cornerRadiusEnd=3).encode(
        x=alt.X("Taste score:Q", title="Taste score (★ vs your average)"),
        y=alt.Y("Item:N", sort="-x", title=None),
        color=alt.Color("Avg rating:Q", scale=alt.Scale(scheme="viridis", domain=[2.5, 5]), title="Avg ★"),
        tooltip=[alt.Tooltip("Item:N", title=label), "Films:Q", alt.Tooltip("Avg rating:Q", format=".2f"),
                 alt.Tooltip("Taste score:Q", format="+.2f"), alt.Tooltip("vs Letterboxd:Q", format="+.2f"),
                 "Examples:N"],
    ).properties(height=height or max(220, 22 * len(t)))


TASTE_COLUMNS = {
    "Films": st.column_config.NumberColumn("Films", format="%d"),
    "Avg rating": st.column_config.NumberColumn("Avg ★", format="%.2f"),
    "Taste score": st.column_config.ProgressColumn("Taste score", format="%+.2f", min_value=-1.5, max_value=1.5),
    "vs Letterboxd": st.column_config.NumberColumn("vs Letterboxd", format="%+.2f"),
    "Examples": st.column_config.TextColumn("Your top-rated", width="large"),
}
