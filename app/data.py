"""Loading the user and catalog CSVs (written by scripts/refresh_data.py) into tidy DataFrames."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st
from unidecode import unidecode

ROOT = Path(__file__).resolve().parent.parent
USERS_DIR = ROOT / "data" / "users"
CATALOG_FILE = ROOT / "data" / "catalog" / "TopFilms2.csv"
DEFAULT_USER = "cloakenswagger"

# Themes contain commas, so the refresh script joins them with "|".
LIST_COLUMNS = {"Genre": ",", "Languages": ",", "Actors": ",", "Themes": "|"}


def list_users() -> list[str]:
    users = sorted(p.stem.removeprefix("AllFilms") for p in USERS_DIR.glob("AllFilms*.csv"))
    if DEFAULT_USER in users:
        users.remove(DEFAULT_USER)
        users.insert(0, DEFAULT_USER)
    return users


def _signature(path: Path) -> float:
    # Passed into cached readers so the cache refreshes when the file changes.
    return path.stat().st_mtime if path.exists() else 0.0


@st.cache_data(show_spinner=False)
def _read(path: str, _mtime: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ("Themes", "Slug", "MyRating", "Difference", "ReviewDate"):
        if col not in df.columns:
            df[col] = pd.NA
    for col, sep in LIST_COLUMNS.items():
        df[col] = df[col].fillna("").astype(str).map(lambda s, sep=sep: [x.strip() for x in s.split(sep) if x.strip()])
    df["Director"] = df["Director"].fillna("").astype(str)
    df["Country"] = df["Country"].fillna("N/A").astype(str)
    df["ReleaseYear"] = pd.to_numeric(df["ReleaseYear"], errors="coerce").astype("Int64")
    df["Decade"] = (df["ReleaseYear"] // 10 * 10).astype("Int64")
    df["MyRating"] = pd.to_numeric(df["MyRating"], errors="coerce")
    df["Difference"] = pd.to_numeric(df["Difference"], errors="coerce")
    df["Watched"] = pd.to_datetime(df["ReviewDate"], format="%m/%d/%Y", errors="coerce")
    # Punctuation-free title + year, so "The Godfather: Part II" matches "The Godfather Part II".
    df["TitleKey"] = df["Movie"].astype(str).map(lambda t: re.sub(r"[^a-z0-9]", "", unidecode(t).lower())) \
        + "|" + df["ReleaseYear"].astype(str)
    df["Language"] = df["Languages"].map(lambda xs: xs[0] if xs else "Unknown")
    return df.reset_index(drop=True)


def load_user(username: str) -> pd.DataFrame:
    path = USERS_DIR / f"AllFilms{username}.csv"
    return _read(str(path), _signature(path))


def load_catalog() -> pd.DataFrame:
    return _read(str(CATALOG_FILE), _signature(CATALOG_FILE))


def data_signature() -> tuple:
    """Changes whenever any data file changes; used as a cache key for derived results."""
    files = sorted(USERS_DIR.glob("AllFilms*.csv")) + [CATALOG_FILE]
    return tuple((p.name, _signature(p)) for p in files)


def name_slug(name: str) -> str:
    s = unidecode(name).lower().replace("'", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def film_url(row) -> str:
    slug = row.get("Slug") if hasattr(row, "get") else None
    if isinstance(slug, str) and slug:
        return f"https://letterboxd.com/film/{slug}/"
    return f"https://letterboxd.com/search/{row['Movie']}/"
