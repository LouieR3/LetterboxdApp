"""Taste profiles and the recommendation model.

Affinity: for any "item" (a director, actor, genre, theme, decade, ...) a user's affinity is how far
above or below their own average they rate films with that item, shrunk toward 0 when it's based
on only a few films:  affinity = sum(rating - user_mean) / (n_films + SHRINK).

Prediction: user_mean + sum over feature groups of weight * (mean affinity of the film's items),
plus terms for the film's Letterboxd rating and popularity. The weights are fitted with ridge
regression on every user's ratings, using leave-one-out affinities so a film never explains itself.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from app import data

SHRINK = 3.0
RIDGE = 10.0

GROUPS = {
    "Director": lambda df: df["Director"].map(lambda d: [d] if d else []),
    "Actors": lambda df: df["Actors"].map(lambda xs: xs[:6]),  # top-billed only
    "Genres": lambda df: df["Genre"],
    "Themes": lambda df: df["Themes"],
    "Decade": lambda df: df["Decade"].map(lambda d: [] if pd.isna(d) else [f"{int(d)}s"]),
    "Runtime": lambda df: df["MovieLength"].map(runtime_bucket).map(lambda b: [b]),
    "Language": lambda df: df["Language"].map(lambda x: [x]),
    "Country": lambda df: df["Country"].map(lambda x: [x]),
}
FEATURES = list(GROUPS) + ["Letterboxd rating", "Popularity"]


def runtime_bucket(minutes) -> str:
    if pd.isna(minutes):
        return "Unknown"
    m = int(minutes)
    if m < 90:
        return "Under 90 min"
    if m >= 180:
        return "3 h +"
    lo = m // 15 * 15
    return f"{lo // 60}h{lo % 60:02d}–{(lo + 15) // 60}h{(lo + 15) % 60:02d}"


def _explode(df: pd.DataFrame, group: str) -> pd.DataFrame:
    s = GROUPS[group](df).explode().dropna()
    s = s[s.astype(str) != ""]
    return pd.DataFrame({"film": s.index.to_numpy(), "item": s.to_numpy()})


def rated(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["MyRating"].notna()].reset_index(drop=True)


# --------------------------------------------------------------------------- taste tables

def affinity_table(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """One row per item: films seen, average rating, taste score and gap to Letterboxd."""
    r = rated(df)
    if r.empty:
        return pd.DataFrame(columns=["Item", "Films", "Avg rating", "Taste score", "vs Letterboxd", "Examples"])
    mu = r["MyRating"].mean()
    long = _explode(r, group)
    long["rating"] = r["MyRating"].to_numpy()[long["film"]]
    long["diff"] = r["Difference"].to_numpy()[long["film"]]
    long["title"] = r["Movie"].to_numpy()[long["film"]]
    long = long.sort_values("rating", ascending=False)
    out = long.groupby("item").agg(
        Films=("rating", "size"),
        **{"Avg rating": ("rating", "mean"), "vs Letterboxd": ("diff", "mean"), "_sum": ("rating", "sum")},
        Examples=("title", lambda t: ", ".join(t[:3])),
    )
    out["Taste score"] = (out["_sum"] - mu * out["Films"]) / (out["Films"] + SHRINK)
    out = out.drop(columns="_sum").reset_index().rename(columns={"item": "Item"})
    return out.sort_values("Taste score", ascending=False, ignore_index=True)


# --------------------------------------------------------------------------- features

def features(train: pd.DataFrame, target: pd.DataFrame, loo: bool) -> pd.DataFrame:
    """Feature matrix for `target` films from the taste profile in `train` (rated films).

    With loo=True, target must be train itself and each film's own rating is left out of its features.
    """
    mu = train["MyRating"].mean()
    res = (train["MyRating"] - mu).to_numpy()
    X = pd.DataFrame(index=range(len(target)))
    for group in GROUPS:
        lt = _explode(train, group)
        lt["res"] = res[lt["film"]]
        stats = lt.groupby("item")["res"].agg(["sum", "count"])
        tt = _explode(target, group).join(stats, on="item")
        tt[["sum", "count"]] = tt[["sum", "count"]].fillna(0)
        if loo:
            tt["sum"] -= res[tt["film"]]
            tt["count"] -= 1
        tt["aff"] = tt["sum"] / (tt["count"] + SHRINK)
        X[group] = tt.groupby("film")["aff"].mean().reindex(X.index, fill_value=0.0)
    lb_mean = train["LBRating"].mean()
    pop_mean = np.log10(train["NumberOfRatings"].fillna(0) + 1).mean()
    X["Letterboxd rating"] = (target["LBRating"] - lb_mean).fillna(0).to_numpy()
    X["Popularity"] = (np.log10(target["NumberOfRatings"].fillna(0) + 1) - pop_mean).to_numpy()
    return X[FEATURES]


def _ridge(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.linalg.solve(X.T @ X + RIDGE * np.eye(X.shape[1]), X.T @ y)


@st.cache_data(show_spinner="Training the taste model…")
def fit(_signature: tuple) -> tuple[pd.Series, pd.DataFrame]:
    """Fit shared weights on all users. Accuracy for each user uses weights fitted on the *other* users."""
    per_user = {}
    for u in data.list_users():
        r = rated(data.load_user(u))
        if len(r) >= 20:
            X = features(r, r, loo=True)
            per_user[u] = (X.to_numpy(), (r["MyRating"] - r["MyRating"].mean()).to_numpy(), r)
    if not per_user:
        return pd.Series(0.0, index=FEATURES), pd.DataFrame()

    weights = _ridge(np.vstack([v[0] for v in per_user.values()]), np.concatenate([v[1] for v in per_user.values()]))
    rows = []
    for u, (X, y, r) in per_user.items():
        others = [v for k, v in per_user.items() if k != u]
        w = _ridge(np.vstack([o[0] for o in others]), np.concatenate([o[1] for o in others])) if others else weights
        pred = np.clip(r["MyRating"].mean() + X @ w, 0.5, 5)
        lb = r["LBRating"] - r["LBRating"].mean() + r["MyRating"].mean()
        rows.append({
            "User": u, "Rated films": len(r),
            "Model error": np.abs(pred - r["MyRating"]).mean(),
            "Letterboxd-average error": np.abs(lb.clip(0.5, 5) - r["MyRating"]).mean(),
            "Your-average error": np.abs(r["MyRating"].mean() - r["MyRating"]).mean(),
        })
    return pd.Series(weights, index=FEATURES), pd.DataFrame(rows)


def predict(train: pd.DataFrame, target: pd.DataFrame, weights: pd.Series, loo: bool = False) -> pd.DataFrame:
    """Predicted stars for target films plus each feature group's contribution."""
    X = features(train, target, loo)
    contrib = X * weights
    out = target.reset_index(drop=True).copy()
    out["Predicted"] = np.clip(train["MyRating"].mean() + contrib.sum(axis=1), 0.5, 5)
    for col in contrib.columns:
        out[f"c_{col}"] = contrib[col].to_numpy()
    return out


def reasons(train: pd.DataFrame, films: pd.DataFrame, limit: int = 3) -> list[str]:
    """Short "because you like…" text: the film's best-liked director/actors/themes/genres."""
    maps = {g: affinity_table(train, g).set_index("Item")["Taste score"] for g in ("Director", "Actors", "Themes", "Genres")}
    out = []
    for _, film in films.iterrows():
        hits = []
        for g, aff in maps.items():
            items = GROUPS[g](film.to_frame().T).iloc[0]
            for item in items:
                score = aff.get(item)
                if score is not None and score > 0.15:
                    hits.append((score, item))
        hits.sort(reverse=True)
        out.append(", ".join(item for _, item in hits[:limit]))
    return out


def unseen(catalog: pd.DataFrame, user_df: pd.DataFrame) -> pd.DataFrame:
    seen_slugs = set(user_df["Slug"].dropna())
    seen_titles = set(user_df["TitleKey"])
    mask = ~(catalog["Slug"].isin(seen_slugs) | catalog["TitleKey"].isin(seen_titles))
    return catalog[mask].reset_index(drop=True)
