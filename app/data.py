"""Loading data/films.csv and data/users/<user>.csv (written by scripts/refresh_data.py)."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st
from unidecode import unidecode

ROOT = Path(__file__).resolve().parent.parent
USERS_DIR = ROOT / "data" / "users"
FILMS_FILE = ROOT / "data" / "films.csv"
DEFAULT_USER = "cloakenswagger"
MIN_RUNTIME = 60  # shorts are left out of stats and recommendations

# Themes contain commas, so the refresh script joins them with "|".
LIST_COLUMNS = {"Genre": ",", "Languages": ",", "Actors": ",", "Themes": "|", "Directors": ","}


def _user_files() -> list[Path]:
    # Pre-2.0 files (AllFilms<user>.csv, Watchlist<user>.csv) are ignored once migrated.
    return sorted(p for p in USERS_DIR.glob("*.csv") if not p.stem.startswith(("AllFilms", "Watchlist")))


def list_users() -> list[str]:
    users = [p.stem for p in _user_files()]
    if DEFAULT_USER in users:
        users.remove(DEFAULT_USER)
        users.insert(0, DEFAULT_USER)
    return users


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def data_signature() -> tuple:
    """Changes whenever any data file changes; passed to cached functions as their cache key."""
    return tuple((p.name, _mtime(p)) for p in [*_user_files(), FILMS_FILE])


@st.cache_data(show_spinner=False)
def _films(_mtime_key: float) -> pd.DataFrame:
    df = pd.read_csv(FILMS_FILE)
    for col, sep in LIST_COLUMNS.items():
        df[col] = df[col].fillna("").astype(str).map(lambda s, sep=sep: [x.strip() for x in s.split(sep) if x.strip()])
    df["Director"] = df["Director"].fillna("").astype(str)
    df["Country"] = df["Country"].fillna("").replace("", "Unknown").astype(str)
    df["ReleaseYear"] = pd.to_numeric(df["ReleaseYear"], errors="coerce").astype("Int64")
    df["Decade"] = (df["ReleaseYear"] // 10 * 10).astype("Int64")
    df["Language"] = df["Languages"].map(lambda xs: xs[0] if xs else "Unknown")
    # Punctuation-free title + year: a fallback match key for films without a slug.
    df["TitleKey"] = df["Movie"].astype(str).map(lambda t: re.sub(r"[^a-z0-9]", "", unidecode(t).lower())) \
        + "|" + df["ReleaseYear"].astype(str)
    return df


def load_films() -> pd.DataFrame:
    """Every film in the definitive film table."""
    return _films(_mtime(FILMS_FILE))


@st.cache_data(show_spinner=False)
def _user(username: str, _sig: tuple) -> pd.DataFrame:
    own = pd.read_csv(USERS_DIR / f"{username}.csv", usecols=["Slug", "MyRating", "Watched"])
    df = own.merge(load_films(), on="Slug", how="inner")  # films not fetched yet are left out
    df = df[df["MovieLength"].fillna(0) >= MIN_RUNTIME]
    df["MyRating"] = pd.to_numeric(df["MyRating"], errors="coerce")
    df["Difference"] = df["MyRating"] - df["LBRating"]
    df["Watched"] = pd.to_datetime(df["Watched"], errors="coerce")
    return df.reset_index(drop=True)


def load_user(username: str) -> pd.DataFrame:
    """A user's logged films joined with the film data."""
    return _user(username, data_signature())


def load_catalog() -> pd.DataFrame:
    """The pool recommendations are drawn from: feature films with a Letterboxd rating and genres."""
    df = load_films()
    ok = df["LBRating"].notna() & df["MovieLength"].between(MIN_RUNTIME, 275) & df["Genre"].map(bool)
    return df[ok].reset_index(drop=True)


def name_slug(name: str) -> str:
    s = unidecode(name).lower().replace("'", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def film_url(row) -> str:
    slug = row.get("Slug") if hasattr(row, "get") else None
    if isinstance(slug, str) and slug:
        return f"https://letterboxd.com/film/{slug}/"
    return f"https://letterboxd.com/search/{row['Movie']}/"
