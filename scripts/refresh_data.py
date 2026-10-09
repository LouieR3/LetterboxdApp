"""Refresh the app's Letterboxd data: user rating histories and film metadata.

Set the COMMAND (and related) variables in the CONFIG section below, then run:

    python scripts/refresh_data.py

Every film page fetched is stored in data/cache/films.jsonl, so a film is fetched once no matter
how many users have seen it, and an interrupted run picks up where it stopped. Films fetched
within MAX_AGE_DAYS (default 30) are not fetched again.

Where a user's films come from (later sources win when they disagree):
  1. Their existing data/users/AllFilms<user>.csv (title + year, resolved to a film page).
  2. A Letterboxd data export (Settings > Data > Export your data), if EXPORT is set.
     This is the only way to get a complete history: Letterboxd blocks automated access to
     page 2+ of a member's film lists, and this script does not try to get around that.
  3. Page 1 of letterboxd.com/<user>/films/ (most recent ~72 films, with ratings).
  4. The member's RSS feed (recent diary entries, with ratings and watch dates).

The script fetches one page at a time with a delay, sends an honest User-Agent, and stops if
Letterboxd starts challenging requests rather than trying to get past the challenge.
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

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
USERS_DIR = DATA / "users"
CATALOG_FILE = DATA / "catalog" / "TopFilms2.csv"
CACHE_DIR = DATA / "cache"
FILMS_CACHE = CACHE_DIR / "films.jsonl"
SLUG_CACHE = CACHE_DIR / "slugs.jsonl"
UNRESOLVED_FILE = CACHE_DIR / "unresolved.csv"

BASE = "https://letterboxd.com"
USER_AGENT = "letterboxd-stats/2.0 (personal stats app; +https://github.com/LouieR3/LetterboxdApp)"

# --------------------------------------------------------------------------- CONFIG
# Set these instead of passing command-line arguments.

COMMAND = "all"  # "user", "users", "catalog", or "all"
USERNAMES = ["cloakenswagger"]  # used only when COMMAND == "user"
EXPORT = None  # Path to a Letterboxd export .zip or extracted folder; goes with "user" + one username
MAX_AGE_DAYS = 30  # re-fetch film pages older than this (0 refreshes everything)
DELAY = 1.0  # seconds between requests

USER_COLUMNS = ["Movie", "MyRating", "LBRating", "Difference", "ReviewDate", "MovieLength", "LengthInHour",
                "Languages", "Director", "ReleaseYear", "Genre", "Country", "NumberOfReviews",
                "NumberOfRatings", "Actors"]
CATALOG_COLUMNS = ["Movie", "LBRating", "MovieLength", "LengthInHour", "Languages", "Director", "ReleaseYear",
                   "Genre", "Country", "NumberOfReviews", "NumberOfRatings", "Actors"]

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
    imdb = soup.select_one('a[data-track-action="IMDb"]')
    tmdb = soup.select_one('a[data-track-action="TMDB"]')
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
        "imdb_url": imdb["href"] if imdb else None,
        "tmdb_url": tmdb["href"] if tmdb else None,
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

    def is_fresh(self, slug: str) -> bool:
        rec = self.films.get(slug)
        if not rec:
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

    def remember_title(self, rec: dict) -> None:
        key = title_key(rec["title"], rec["year"])
        if key not in self.slugs:
            self._remember(key, rec["slug"])

    def compact(self) -> None:
        if self.films:
            _compact_jsonl(FILMS_CACHE, self.films)
        if self.slugs:
            _compact_jsonl(SLUG_CACHE, self.slugs)
        if self.unresolved:
            existing = pd.read_csv(UNRESOLVED_FILE) if UNRESOLVED_FILE.exists() else pd.DataFrame()
            df = pd.concat([existing, pd.DataFrame(self.unresolved)]).drop_duplicates()
            df.to_csv(UNRESOLVED_FILE, index=False)


# --------------------------------------------------------------------------- user sources

@dataclass
class Entry:
    rating: float | None = None
    watched: str | None = None  # ISO date


def _merge(entries: dict, slug: str, rating=None, watched=None) -> None:
    e = entries.setdefault(slug, Entry())
    if rating is not None and not pd.isna(rating):
        e.rating = float(rating)
    if watched and (e.watched is None or watched > e.watched):
        e.watched = watched


def _to_iso(date_str) -> str | None:
    if not isinstance(date_str, str) or not date_str.strip():
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date().isoformat()
        except ValueError:
            pass
    return None


def from_existing_csv(username: str, films: Films, entries: dict) -> pd.DataFrame:
    """Add the user's existing films; returns the rows that couldn't be matched to a film page."""
    path = USERS_DIR / f"AllFilms{username}.csv"
    if not path.exists():
        return pd.DataFrame(columns=USER_COLUMNS)
    df = pd.read_csv(path)
    log.info("[%s] Resolving %d films from the existing CSV", username, len(df))
    unmatched = []
    for i, row in enumerate(df.itertuples(index=False), 1):
        slug = films.resolve(row.Movie, row.ReleaseYear, row.Director)
        if slug:
            _merge(entries, slug, row.MyRating, _to_iso(row.ReviewDate))
        else:
            unmatched.append(i - 1)
        _progress(username, "existing CSV", i, len(df), films)
    return df.iloc[unmatched]


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
            rating = float(r["Rating"]) if r.get("Rating") else None
            _merge(entries, slug, rating, dates.get(key))
        _progress(username, "export", i, len(rows), films)


def from_recent(username: str, films: Films, entries: dict) -> None:
    r = films.client.get(f"{BASE}/{username}/films/")
    if r is not None:
        soup = BeautifulSoup(r.text, "lxml")
        for item in soup.select("li.griditem"):
            poster = item.select_one("[data-item-slug]")
            if not poster:
                continue
            star = item.select_one("span.rating")
            m = re.search(r"rated-(\d+)", " ".join(star["class"])) if star else None
            _merge(entries, poster["data-item-slug"], int(m.group(1)) / 2 if m else None)

    r = films.client.get(f"{BASE}/{username}/rss/")
    if r is None:
        return
    ns = {"letterboxd": "https://letterboxd.com", "tmdb": "https://themoviedb.org"}
    for item in ElementTree.fromstring(r.content).iter("item"):
        if item.find("letterboxd:filmTitle", ns) is None:
            continue  # list posts, not diary entries
        m = re.search(r"/film/([^/]+)/", item.findtext("link", ""))
        if not m:
            continue
        rating = item.findtext("letterboxd:memberRating", None, ns)
        _merge(entries, m.group(1), float(rating) if rating else None,
               item.findtext("letterboxd:watchedDate", None, ns))


def _progress(username: str, stage: str, i: int, total: int, films: Films) -> None:
    if i % 50 == 0 or i == total:
        log.info("[%s] %s: %d/%d (fetched %d pages so far)", username, stage, i, total, films.fetched)


# --------------------------------------------------------------------------- output

def _length_in_hour(minutes: int) -> str:
    return f"{minutes // 60}:{minutes % 60:02d}"


def _billed_actors(actors: list[str]) -> str:
    # Same cut-off as the original scraper, so billing scores stay comparable:
    # big casts are trimmed to the top-billed share.
    n = len(actors)
    limit = round(n * 0.6) if 20 <= n < 27 else round(n * 0.4) if n >= 27 else n
    return ",".join(actors[:limit])


def film_row(rec: dict) -> dict | None:
    """Turn a cached film into the shared catalog columns, or None if the app would skip it."""
    minutes = rec.get("minutes") or 0
    if not (60 < minutes < 500) or rec.get("lb_rating") is None:
        return None
    return {
        "Movie": rec["title"],
        "LBRating": rec["lb_rating"],
        "MovieLength": minutes,
        "LengthInHour": _length_in_hour(minutes),
        "Languages": ",".join(rec["languages"]),
        "Director": rec["directors"][0] if rec["directors"] else "",
        "ReleaseYear": rec["year"],
        "Genre": ",".join(rec["genres"]),
        "Country": rec["countries"][0] if rec["countries"] else "N/A",
        "NumberOfReviews": rec["num_reviews"],
        "NumberOfRatings": rec["num_ratings"],
        "Actors": _billed_actors(rec["actors"]),
    }


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    tmp = path.with_suffix(".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8")
    tmp.replace(path)


def refresh_user(username: str, films: Films, export: Path | None) -> None:
    entries: dict[str, Entry] = {}
    unmatched = from_existing_csv(username, films, entries)
    if export:
        from_export(username, export, films, entries)
    from_recent(username, films, entries)

    log.info("[%s] Fetching film pages for %d films", username, len(entries))
    rows = []
    for i, (slug, e) in enumerate(entries.items(), 1):
        rec = films.get(slug)
        _progress(username, "film pages", i, len(entries), films)
        row = film_row(rec) if rec else None
        if row is None:
            continue
        films.remember_title(rec)
        diff = f"{e.rating - rec['lb_rating']:.2f}" if e.rating is not None else ""
        watched = datetime.fromisoformat(e.watched).strftime("%m/%d/%Y") if e.watched else ""
        rows.append({**row, "MyRating": e.rating, "Difference": diff, "ReviewDate": watched, "_sort": e.watched or ""})

    if not rows:
        log.error("[%s] No films found; leaving the existing CSV alone", username)
        return
    df = pd.DataFrame(rows).sort_values("_sort", ascending=False, kind="stable")[USER_COLUMNS]
    if len(unmatched):
        # Keep films we couldn't find a page for (with their old data) rather than dropping them.
        log.info("[%s] Keeping %d unmatched films from the old CSV as-is", username, len(unmatched))
        df = pd.concat([df, unmatched[USER_COLUMNS]], ignore_index=True)
    _write_csv(df, USERS_DIR / f"AllFilms{username}.csv")
    log.info("[%s] Wrote %d films (%d rated) to data/users/AllFilms%s.csv",
             username, len(df), df["MyRating"].notna().sum(), username)


def refresh_catalog(films: Films) -> None:
    current = pd.read_csv(CATALOG_FILE) if CATALOG_FILE.exists() else pd.DataFrame(columns=CATALOG_COLUMNS)
    slugs: list[str] = []
    log.info("[catalog] Resolving %d existing catalog films", len(current))
    for i, row in enumerate(current.itertuples(index=False), 1):
        slug = films.resolve(row.Movie, row.ReleaseYear, row.Director)
        if slug:
            slugs.append(slug)
        _progress("catalog", "resolve", i, len(current), films)

    # Every film any user has seen also belongs in the catalog.
    for path in sorted(USERS_DIR.glob("AllFilms*.csv")):
        for row in pd.read_csv(path, usecols=["Movie", "ReleaseYear"]).itertuples(index=False):
            key = title_key(row.Movie, row.ReleaseYear)
            if key in films.slugs:
                slugs.append(films.slugs[key]["slug"])

    slugs = list(dict.fromkeys(slugs))
    log.info("[catalog] Refreshing %d film pages", len(slugs))
    rows = []
    for i, slug in enumerate(slugs, 1):
        rec = films.get(slug)
        _progress("catalog", "film pages", i, len(slugs), films)
        row = film_row(rec) if rec else None
        if row and row["MovieLength"] < 275 and row["Genre"] and row["Actors"]:
            rows.append(row)

    df = pd.DataFrame(rows, columns=CATALOG_COLUMNS).drop_duplicates(subset=["Movie", "Director"])
    _write_csv(df, CATALOG_FILE)
    log.info("[catalog] Wrote %d films to data/catalog/TopFilms2.csv", len(df))


# --------------------------------------------------------------------------- CLI

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    if COMMAND not in ("user", "users", "catalog", "all"):
        sys.exit(f"COMMAND must be one of 'user', 'users', 'catalog', 'all' (got {COMMAND!r})")
    if COMMAND == "user" and not USERNAMES:
        sys.exit("set USERNAMES to at least one username")
    if EXPORT and (COMMAND != "user" or len(USERNAMES) != 1):
        sys.exit("EXPORT goes with COMMAND = 'user' and exactly one username")

    usernames = USERNAMES
    if COMMAND in ("users", "all"):
        usernames = sorted(p.stem.removeprefix("AllFilms") for p in USERS_DIR.glob("AllFilms*.csv"))

    client = Client(DELAY)
    films = Films(client, timedelta(days=MAX_AGE_DAYS))
    started = time.monotonic()
    try:
        for username in usernames:
            refresh_user(username, films, EXPORT)
        if COMMAND in ("catalog", "all"):
            refresh_catalog(films)
    except Blocked as e:
        log.error("Stopped: Letterboxd is challenging requests (%s). Progress is saved in data/cache/; "
                  "rerun later (optionally with a larger DELAY) to continue.", e)
        sys.exit(2)
    except KeyboardInterrupt:
        log.warning("Interrupted. Progress is saved in data/cache/; rerun to continue.")
        sys.exit(130)
    finally:
        films.compact()
        log.info("%d requests, %d film pages fetched, %d titles to review, %.0f min",
                 client.requests, films.fetched, len(films.unresolved), (time.monotonic() - started) / 60)
        if films.unresolved:
            log.info("Titles to review are listed in data/cache/unresolved.csv")


if __name__ == "__main__":
    main()
