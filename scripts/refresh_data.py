"""Refresh the app's Letterboxd data.

Set the CONFIG variables below, then run from the repo root:

    python scripts/refresh_data.py

Outputs
  data/films.csv          The definitive film table: one row per film, with the public data (Letterboxd
                          rating, number of ratings/reviews, runtime, director, cast, genres, themes, ...).
                          It covers every film in TOP_LIST plus every film any user has logged, and is
                          what the app draws stats and recommendations from.
  data/users/<user>.csv   Only what is personal: which films the user logged, their rating and watch date.

How a run works (cheapest steps first)
  1. Users: about 2 requests per user (their RSS feed and the first page of their films) to pick up
     recent activity, merged with the films already in data/users/<user>.csv. An optional Letterboxd
     export (EXPORTS) fills in the complete history.
  2. Top list: the pages of TOP_LIST (about 11 requests for 1,001 films).
  3. Film data: one request per film in (top list + all users' films), skipping films fetched within
     MAX_AGE_DAYS. Each film is fetched once no matter how many users logged it, and every page is
     cached in data/cache/films.jsonl, so an interrupted run picks up where it stopped.

Letterboxd blocks automated access to page 2+ of a member's film lists, so step 1 only sees recent
activity on its own; the export is the way to backfill. The script sends an honest User-Agent, waits
between requests, and stops if Letterboxd starts challenging requests rather than trying to get past it.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import random
import re
import sys
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

# --------------------------------------------------------------------------- CONFIG

COMMAND = "all"  # "all": users + top list + film data | "users": users + their films only | "films": film data only
# The friend group. Everyone here gets a data/users/<user>.csv, and their films go into data/films.csv.
USERS = ["cloakenswagger", "bluegrace11", "carmal", "goldfishbrain", "gr8escape10", "prahladsingh", "zacierka",
         "stephanie216", "rec3", "ganonuptilt"]
REFRESH_USERS = None  # None = refresh everyone in USERS; or a subset, e.g. ["cloakenswagger"]
EXPORTS = {}  # Letterboxd exports (.zip or folder) to backfill full histories, e.g. {"cloakenswagger": "export.zip"}
TOP_LIST = "juliodogpit/list/the-1001-greatest-films-ranked-as-objectively"  # the general films to recommend from
MAX_AGE_DAYS = 30  # re-fetch film pages older than this (0 refreshes everything)
DELAY = 1.0  # seconds between requests

# --------------------------------------------------------------------------- paths

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
USERS_DIR = DATA / "users"
FILMS_FILE = DATA / "films.csv"
TOP_LIST_FILE = DATA / "top_list.csv"
OVERRIDES_FILE = DATA / "slug_overrides.csv"  # hand-fixed title -> slug matches (title, year, slug)
CACHE_DIR = DATA / "cache"
FILMS_CACHE = CACHE_DIR / "films.jsonl"
SLUG_CACHE = CACHE_DIR / "slugs.jsonl"
UNRESOLVED_FILE = CACHE_DIR / "unresolved.csv"

BASE = "https://letterboxd.com"
USER_AGENT = "letterboxd-stats/2.0 (personal stats app; +https://github.com/LouieR3/LetterboxdApp)"

USER_COLUMNS = ["Slug", "Movie", "ReleaseYear", "MyRating", "Watched"]
# Themes contain commas ("Horror, the undead and monster classics"), so they're joined with "|";
# the other list columns are comma-separated.
FILM_COLUMNS = ["Slug", "Movie", "ReleaseYear", "LBRating", "NumberOfRatings", "NumberOfReviews", "MovieLength",
                "Director", "Directors", "Genre", "Themes", "Languages", "Country", "Actors", "TopRank", "FetchedAt"]

log = logging.getLogger("refresh")


# --------------------------------------------------------------------------- HTTP

class Blocked(Exception):
    """Letterboxd is challenging or rate limiting us; stop and resume later."""


class Client:
    def __init__(self, delay: float):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._last = 0.0
        self.requests = 0

    def get(self, url: str) -> requests.Response | None:
        """GET a page politely. Returns None on 404; raises Blocked if Letterboxd pushes back."""
        backoff = 60
        for attempt in range(4):
            wait = self.delay * random.uniform(0.8, 1.3) - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            self.requests += 1
            try:
                r = self.session.get(url, timeout=30)
            except requests.RequestException as e:
                log.warning("Request failed (%s): %s", e.__class__.__name__, url)
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code == 404:
                return None
            challenged = r.status_code == 403 and (r.headers.get("cf-mitigated") or "Just a moment" in r.text)
            if challenged or r.status_code == 429:
                if attempt == 3:
                    raise Blocked(f"HTTP {r.status_code} on {url}")
                pause = int(r.headers.get("Retry-After") or backoff)
                log.warning("Letterboxd is pushing back (HTTP %s); pausing %ss", r.status_code, pause)
                time.sleep(pause)
                backoff *= 2
                continue
            if r.status_code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            return r
        return None


# --------------------------------------------------------------------------- caches

def _load_jsonl(path: Path, key: str) -> dict:
    out = {}
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    out[rec[key]] = rec
    return out


def _append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _compact_jsonl(path: Path, records: dict) -> None:
    """Rewrite a cache with one line per key (appends leave superseded lines behind)."""
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for rec in records.values():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(path)


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8")
    tmp.replace(path)


def _name_key(name: str) -> str:
    """Surname only, so "Alejandro González Iñárritu" matches "Alejandro G. Iñárritu"."""
    parts = unidecode(name).lower().split()
    return re.sub(r"[^a-z0-9]", "", parts[-1]) if parts else ""


def title_key(title: str, year) -> str:
    year = "" if year is None or pd.isna(year) else str(int(float(year)))
    return f"{unidecode(str(title)).strip().lower()}|{year}"


# --------------------------------------------------------------------------- film pages

def parse_film(html: str, slug: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    ld_tag = soup.find("script", type="application/ld+json")
    if not ld_tag or not ld_tag.string:
        return None
    raw = ld_tag.string
    ld = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])

    year = None
    tw = soup.find("meta", attrs={"name": "twitter:title"})
    m = re.search(r"\((\d{4})\)\s*$", tw["content"]) if tw else None
    if m:
        year = int(m.group(1))
    elif ld.get("dateCreated"):
        year = int(ld["dateCreated"][:4])

    minutes = None
    footer = soup.select_one("p.text-footer")
    m = re.search(r"([\d,]+)\s*min", footer.get_text(" ")) if footer else None
    if m:
        minutes = int(m.group(1).replace(",", ""))
    elif ld.get("duration"):
        m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", ld["duration"])
        if m:
            minutes = int(m.group(1) or 0) * 60 + int(m.group(2) or 0)

    def link_texts(prefix: str) -> list[str]:
        seen = []
        for a in soup.select(f'a[href^="{prefix}"]'):
            text = a.get_text(strip=True)
            if text and text not in seen:
                seen.append(text)
        return seen

    rating = ld.get("aggregateRating") or {}
    countries = link_texts("/films/country/") or [c["name"] for c in ld.get("countryOfOrigin", [])]
    return {
        "slug": slug,
        "title": ld.get("name"),
        "year": year,
        "lb_rating": rating.get("ratingValue"),
        "num_ratings": rating.get("ratingCount"),
        "num_reviews": rating.get("reviewCount"),
        "minutes": minutes,
        "languages": link_texts("/films/language/"),
        "directors": [d["name"] for d in ld.get("director", [])],
        "genres": ld.get("genre", []),
        "countries": countries,
        "actors": [a["name"] for a in ld.get("actor", [])][:60],
        # The Genres tab lists up to ~7 themes and mini-themes. The full "Show All" page
        # (/film/<slug>/themes/) is behind Letterboxd's bot check, so it isn't fetched.
        "themes": link_texts("/films/theme/") + link_texts("/films/mini-theme/"),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def slugify(title: str) -> str:
    s = unidecode(str(title)).lower()
    s = re.sub(r"['’.]", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


@dataclass
class Films:
    client: Client
    max_age: timedelta
    films: dict = field(default_factory=lambda: _load_jsonl(FILMS_CACHE, "slug"))
    slugs: dict = field(default_factory=lambda: _load_jsonl(SLUG_CACHE, "key"))
    unresolved: list = field(default_factory=list)
    fetched: int = 0

    def __post_init__(self):
        if OVERRIDES_FILE.exists():
            for row in pd.read_csv(OVERRIDES_FILE).itertuples(index=False):
                self.slugs[title_key(row.title, row.year)] = {"key": title_key(row.title, row.year), "slug": row.slug}

    def is_fresh(self, slug: str) -> bool:
        rec = self.films.get(slug)
        if not rec or "themes" not in rec:  # cached before themes were collected
            return False
        return datetime.now(timezone.utc) - datetime.fromisoformat(rec["fetched_at"]) < self.max_age

    def _store(self, rec: dict) -> dict:
        self.films[rec["slug"]] = rec
        _append_jsonl(FILMS_CACHE, rec)
        self.fetched += 1
        return rec

    def fetch_url(self, url: str) -> dict | None:
        """Fetch a film page (or anything that redirects to one) and cache it under its real slug."""
        r = self.client.get(url)
        if r is None:
            return None
        m = re.search(r"/film/([^/]+)/", r.url)
        if not m:
            return None
        slug = m.group(1)
        if not r.url.startswith(f"{BASE}/film/"):  # e.g. a member's diary entry: follow to the film
            return self.get(slug)
        rec = parse_film(r.text, slug)
        return self._store(rec) if rec else None

    def get(self, slug: str) -> dict | None:
        if not slug:
            return None
        if self.is_fresh(slug):
            return self.films[slug]
        return self.fetch_url(f"{BASE}/film/{slug}/") or self.films.get(slug)

    def resolve(self, title: str, year, director=None) -> str | None:
        """Find the slug for a title + year, by lookup first and then by guessing the URL.

        A guessed page must match the year (within one) and, when we know it, the director:
        same-title films from neighbouring years are common (e.g. two films called The Fighter).
        """
        key = title_key(title, year)
        if key in self.slugs:
            return self.slugs[key]["slug"]
        year_int = None if year is None or pd.isna(year) else int(float(year))
        wanted = _name_key(director) if isinstance(director, str) and director.strip() else None
        base = slugify(title)
        if not base:  # e.g. "$" (1971): nothing to guess from, and /film// gets challenged
            self.unresolved.append({"title": title, "year": year_int, "note": "no match"})
            return None
        candidates = [base] + ([f"{base}-{year_int}"] if year_int else []) + [f"{base}-1"]
        fallback = None
        for candidate in candidates:
            rec = self.get(candidate)
            if not rec:
                continue
            # Placeholder pages (e.g. "-1" slugs) have no year or director; they never count as a match.
            if year_int is not None and (rec["year"] is None or abs(rec["year"] - year_int) > 1):
                continue
            if wanted is None or wanted in map(_name_key, rec["directors"]):
                self._remember(key, rec["slug"])
                return rec["slug"]
            # Director credits drift (co-directors added or dropped), so an exact-year match with a
            # different director is kept as a fallback, and flagged for review.
            if fallback is None and rec["year"] == year_int:
                fallback = rec
        if fallback:
            self.unresolved.append({"title": title, "year": year_int, "note": f"check: matched {fallback['slug']}"})
            self._remember(key, fallback["slug"])
            return fallback["slug"]
        self.unresolved.append({"title": title, "year": year_int, "note": "no match"})
        return None

    def _remember(self, key: str, slug: str) -> None:
        rec = {"key": key, "slug": slug}
        self.slugs[key] = rec
        _append_jsonl(SLUG_CACHE, rec)

    def compact(self) -> None:
        if self.films:
            _compact_jsonl(FILMS_CACHE, self.films)
        if self.slugs:
            _compact_jsonl(SLUG_CACHE, self.slugs)
        if self.unresolved:
            existing = pd.read_csv(UNRESOLVED_FILE) if UNRESOLVED_FILE.exists() else pd.DataFrame()
            df = pd.concat([existing, pd.DataFrame(self.unresolved)]).drop_duplicates()
            _write_csv(df, UNRESOLVED_FILE)


def _progress(label: str, stage: str, i: int, total: int, films: Films) -> None:
    if i % 50 == 0 or i == total:
        log.info("[%s] %s: %d/%d (fetched %d pages so far)", label, stage, i, total, films.fetched)


# --------------------------------------------------------------------------- step 1: users

@dataclass
class Entry:
    title: str | None = None
    year: int | None = None
    rating: float | None = None
    watched: str | None = None  # ISO date


def _merge(entries: dict, slug: str, title=None, year=None, rating=None, watched=None) -> None:
    e = entries.setdefault(slug, Entry())
    e.title = title or e.title
    if year is not None and not pd.isna(year):
        e.year = int(year)
    if rating is not None and not pd.isna(rating):
        e.rating = float(rating)
    if isinstance(watched, str) and watched and (e.watched is None or watched > e.watched):
        e.watched = watched


def _to_iso(date_str) -> str | None:
    if not isinstance(date_str, str) or not date_str.strip():
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date().isoformat()
        except ValueError:
            pass
    return None


def from_saved(username: str, films: Films, entries: dict) -> None:
    """The user's existing file, or (first run only) their pre-2.0 AllFilms<user>.csv, matched to slugs."""
    path = USERS_DIR / f"{username}.csv"
    if path.exists():
        for row in pd.read_csv(path).itertuples(index=False):
            _merge(entries, row.Slug, row.Movie, row.ReleaseYear, row.MyRating, _to_iso(row.Watched))
        return
    legacy = USERS_DIR / f"AllFilms{username}.csv"
    if not legacy.exists():
        return
    df = pd.read_csv(legacy)
    if "Slug" not in df.columns:
        df["Slug"] = None
    log.info("[%s] Migrating %d films from %s", username, len(df), legacy.name)
    for i, row in enumerate(df.itertuples(index=False), 1):
        slug = row.Slug if isinstance(row.Slug, str) else films.resolve(row.Movie, row.ReleaseYear, row.Director)
        if slug:
            _merge(entries, slug, row.Movie, row.ReleaseYear, row.MyRating, _to_iso(row.ReviewDate))
        _progress(username, "migrate", i, len(df), films)


def from_export(username: str, export: Path, films: Films, entries: dict) -> None:
    def read(name: str) -> list[dict]:
        if export.is_dir():
            p = export / name
            return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []
        with zipfile.ZipFile(export) as z:
            if name not in z.namelist():
                return []
            return list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8")))

    watched, ratings, diary = read("watched.csv"), read("ratings.csv"), read("diary.csv")
    if not (watched or ratings):
        sys.exit(f"{export} doesn't look like a Letterboxd export (no watched.csv or ratings.csv)")
    dates: dict[str, str] = {}
    for d in diary:
        key = title_key(d["Name"], d["Year"] or None)
        when = d.get("Watched Date") or d.get("Date")
        if when and when > dates.get(key, ""):
            dates[key] = when

    rows = {title_key(r["Name"], r["Year"] or None): r for r in watched}
    rows.update({title_key(r["Name"], r["Year"] or None): r for r in ratings})  # rated rows carry Rating
    log.info("[%s] Export: %d films (%d rated)", username, len(rows), len(ratings))
    for i, (key, r) in enumerate(rows.items(), 1):
        slug = films.slugs[key]["slug"] if key in films.slugs else None
        if not slug and r.get("Letterboxd URI"):
            rec = films.fetch_url(r["Letterboxd URI"])
            if rec:
                films._remember(key, rec["slug"])
                slug = rec["slug"]
        slug = slug or films.resolve(r["Name"], r["Year"] or None)
        if slug:
            _merge(entries, slug, r["Name"], r["Year"] or None, float(r["Rating"]) if r.get("Rating") else None,
                   dates.get(key))
        _progress(username, "export", i, len(rows), films)


def from_recent(username: str, films: Films, entries: dict) -> None:
    """Page 1 of the member's films (latest ~72, with ratings) and their RSS feed (diary entries with dates)."""
    r = films.client.get(f"{BASE}/{username}/films/")
    if r is not None:
        soup = BeautifulSoup(r.text, "lxml")
        for item in soup.select("li.griditem"):
            poster = item.select_one("[data-item-slug]")
            if not poster:
                continue
            star = item.select_one("span.rating")
            m = re.search(r"rated-(\d+)", " ".join(star["class"])) if star else None
            name = poster.get("data-item-full-display-name") or poster.get("data-item-name") or ""
            ym = re.search(r"\((\d{4})\)$", name)
            _merge(entries, poster["data-item-slug"], re.sub(r"\s*\(\d{4}\)$", "", name) or None,
                   int(ym.group(1)) if ym else None, int(m.group(1)) / 2 if m else None)

    r = films.client.get(f"{BASE}/{username}/rss/")
    if r is None:
        return
    ns = {"letterboxd": "https://letterboxd.com", "tmdb": "https://themoviedb.org"}
    for item in ElementTree.fromstring(r.content).iter("item"):
        title = item.findtext("letterboxd:filmTitle", None, ns)
        if title is None:
            continue  # list posts, not diary entries
        m = re.search(r"/film/([^/]+)/", item.findtext("link", ""))
        if not m:
            continue
        rating = item.findtext("letterboxd:memberRating", None, ns)
        _merge(entries, m.group(1), title, item.findtext("letterboxd:filmYear", None, ns),
               float(rating) if rating else None, item.findtext("letterboxd:watchedDate", None, ns))


def refresh_user(username: str, films: Films) -> None:
    entries: dict[str, Entry] = {}
    from_saved(username, films, entries)
    if username in EXPORTS:
        from_export(username, Path(EXPORTS[username]), films, entries)
    from_recent(username, films, entries)
    if not entries:
        log.error("[%s] No films found (is the profile public?); skipping", username)
        return
    df = pd.DataFrame([{"Slug": slug, "Movie": e.title, "ReleaseYear": e.year, "MyRating": e.rating,
                        "Watched": e.watched} for slug, e in entries.items()])
    df["ReleaseYear"] = df["ReleaseYear"].astype("Int64")
    df = df.sort_values("Watched", ascending=False, na_position="last", kind="stable")[USER_COLUMNS]
    _write_csv(df, USERS_DIR / f"{username}.csv")
    log.info("[%s] %d films (%d rated) -> data/users/%s.csv", username, len(df), df["MyRating"].notna().sum(), username)


def user_slugs(usernames: list[str]) -> list[str]:
    slugs = []
    for u in usernames:
        path = USERS_DIR / f"{u}.csv"
        if path.exists():
            slugs += pd.read_csv(path, usecols=["Slug"])["Slug"].dropna().tolist()
    return slugs


# --------------------------------------------------------------------------- step 2: top list

def refresh_top_list(films: Films) -> None:
    rows, page = [], 1
    while True:
        r = films.client.get(f"{BASE}/{TOP_LIST}/page/{page}/" if page > 1 else f"{BASE}/{TOP_LIST}/")
        if r is None:
            break
        soup = BeautifulSoup(r.text, "lxml")
        found = [p for p in soup.select("[data-item-slug]")]
        if not found:
            break
        for p in found:
            rows.append({"TopRank": len(rows) + 1, "Slug": p["data-item-slug"],
                         "Movie": p.get("data-item-full-display-name") or p.get("data-item-name")})
        if not soup.select_one("a.next"):
            break
        page += 1
    if rows:
        _write_csv(pd.DataFrame(rows).drop_duplicates("Slug"), TOP_LIST_FILE)
        log.info("[top list] %d films from %s", len(rows), TOP_LIST)
    else:
        log.warning("[top list] Couldn't read %s; keeping the previous data/top_list.csv", TOP_LIST)


# --------------------------------------------------------------------------- step 3: film data

def _billed_actors(actors: list[str]) -> str:
    # Same cut-off as the original scraper, so billing scores stay comparable:
    # big casts are trimmed to the top-billed share.
    n = len(actors)
    limit = round(n * 0.6) if 20 <= n < 27 else round(n * 0.4) if n >= 27 else n
    return ",".join(actors[:limit])


def film_row(rec: dict, top_rank) -> dict:
    return {
        "Slug": rec["slug"],
        "Movie": rec["title"],
        "ReleaseYear": rec["year"],
        "LBRating": rec["lb_rating"],
        "NumberOfRatings": rec["num_ratings"],
        "NumberOfReviews": rec["num_reviews"],
        "MovieLength": rec["minutes"],
        "Director": rec["directors"][0] if rec["directors"] else "",
        "Directors": ",".join(rec["directors"]),
        "Genre": ",".join(rec["genres"]),
        "Themes": "|".join(rec.get("themes", [])),
        "Languages": ",".join(rec["languages"]),
        "Country": rec["countries"][0] if rec["countries"] else "",
        "Actors": _billed_actors(rec["actors"]),
        "TopRank": top_rank,
        "FetchedAt": rec["fetched_at"],
    }


def refresh_films(films: Films, fetch: set[str]) -> None:
    """Write data/films.csv for (top list + every user's films), fetching the stale films in `fetch`."""
    top = pd.read_csv(TOP_LIST_FILE) if TOP_LIST_FILE.exists() else pd.DataFrame(columns=["TopRank", "Slug"])
    rank = dict(zip(top["Slug"], top["TopRank"]))
    members = list(dict.fromkeys(list(top["Slug"]) + user_slugs(USERS)))
    todo = [s for s in members if s in fetch and not films.is_fresh(s)]
    log.info("[films] %d films in the catalog; %d need fetching", len(members), len(todo))
    try:
        for i, slug in enumerate(todo, 1):
            films.get(slug)
            _progress("films", "film pages", i, len(todo), films)
    finally:  # write whatever we have, even if the run is interrupted
        rows = [film_row(films.films[s], rank.get(s)) for s in members if s in films.films]
        df = pd.DataFrame(rows, columns=FILM_COLUMNS)
        df["TopRank"] = df["TopRank"].astype("Int64")
        df["ReleaseYear"] = df["ReleaseYear"].astype("Int64")
        _write_csv(df, FILMS_FILE)
        missing = len(members) - len(df)
        log.info("[films] Wrote %d films to data/films.csv%s", len(df),
                 f" ({missing} not fetched yet)" if missing else "")


# --------------------------------------------------------------------------- main

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    if COMMAND not in ("all", "users", "films"):
        sys.exit(f"COMMAND must be 'all', 'users' or 'films' (got {COMMAND!r})")
    refresh = USERS if REFRESH_USERS is None else REFRESH_USERS
    unknown = set(refresh) - set(USERS)
    if unknown:
        sys.exit(f"REFRESH_USERS has names not in USERS: {sorted(unknown)}")

    client = Client(DELAY)
    films = Films(client, timedelta(days=MAX_AGE_DAYS))
    started = time.monotonic()
    try:
        if COMMAND in ("all", "users"):
            for username in refresh:
                refresh_user(username, films)
        if COMMAND == "all":
            refresh_top_list(films)
        # "users" only fetches those users' films; the rest of the catalog is rewritten from the cache.
        fetch = set(user_slugs(refresh)) if COMMAND == "users" else {*user_slugs(USERS), *(
            pd.read_csv(TOP_LIST_FILE)["Slug"] if TOP_LIST_FILE.exists() else [])}
        refresh_films(films, fetch)
    except Blocked as e:
        log.error("Stopped: Letterboxd is challenging requests (%s). Progress is saved; "
                  "rerun later (optionally with a larger DELAY) to continue.", e)
        sys.exit(2)
    except KeyboardInterrupt:
        log.warning("Interrupted. Progress is saved; rerun to continue.")
        sys.exit(130)
    finally:
        films.compact()
        log.info("%d requests, %d film pages fetched, %d titles to review, %.0f min",
                 client.requests, films.fetched, len(films.unresolved), (time.monotonic() - started) / 60)
        if films.unresolved:
            log.info("Titles to review are listed in data/cache/unresolved.csv "
                     "(fix them in data/slug_overrides.csv: title,year,slug)")


if __name__ == "__main__":
    main()
