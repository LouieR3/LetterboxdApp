# Letterboxd Stats

A Streamlit app that breaks down a Letterboxd user's ratings — favorite actors, directors, genres, decades, languages and runtimes — and ranks movies they haven't seen yet as recommendations.

**Live app:** https://louier3-letterboxd-stats.streamlit.app/ (Streamlit Community Cloud; it sleeps when idle, so the first load can take a minute)

## Run it locally

Requires Python 3.9+.

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit2.py
```

Run commands from the repo root: the app and scripts read `data/` with relative paths.

## Using the app

1. On **Home**, choose a user and click **Change User**. The other pages use that selection.
2. Pick a page from the sidebar:

| Page | What it shows |
|---|---|
| Home | Every rated film for the user, plus their average rating |
| Your Favorite Actors / Directors | People ranked by a weighted score (your average rating, how many of their films you've seen, how far you rate them above or below Letterboxd, and billing position for actors) |
| Your Favorite Movies By Length / Genres / Decades / Languages | The same weighted score, grouped by bucket |
| Recommendations | Films from the catalog you **haven't** seen (Letterboxd rating > 3.0, > 500 ratings), ranked by predicted fit |
| Recommendations All | The whole catalog, seen and unseen, ranked by the same model, next to your actual rating where you have one |

User data is a snapshot that was scraped ahead of time. The app does not call Letterboxd while it runs.

## Repo layout

```
streamlit2.py          App entry point (the Streamlit Cloud main file — don't rename without updating the deployment)
intro.py               Home page
actors.py director.py genre.py decade.py language.py length.py
                       Stats pages, each with an app() function
recommender.py         "Recommendations All" page
recommender2.py        "Recommendations" page
call*.py               Score tables (favorite genres, actors, …) that the recommenders use
user.py                Holds the selected user's CSV path in st.session_state
ratings.py country.py year.py
                       Imported but not currently shown in navigation

data/
  users/               AllFilms<username>.csv — one per user, scraped from their Letterboxd ratings
                       Watchlist<username>.csv — a scraped watchlist (not used by the app yet)
  catalog/             TopFilms2.csv — the recommendation catalog (~9.3k films)
                       random-movie-roulette.csv, TopFilms.csv, Top1001Films.csv — source and older catalogs
  lists/               movies-of-YYYY.csv, my-favorite-movies-of-all-time.csv — scraped Letterboxd lists

  cache/               Scraper cache (git-ignored): films.jsonl, slugs.jsonl, unresolved.csv

scripts/refresh_data.py
                       Refreshes user histories and film data from Letterboxd (see below)
```

## Data format

Each `data/users/AllFilms<username>.csv` has these columns:

`Movie, MyRating, LBRating, Difference, ReviewDate, MovieLength, LengthInHour, Languages, Director, ReleaseYear, Genre, Country, NumberOfReviews, NumberOfRatings, Actors`

- `MyRating` and `LBRating` use a 0.5–5 star scale. `Difference` = `MyRating − LBRating`.
- `Languages`, `Genre` and `Actors` are comma-separated. Actors are in billing order.
- A blank `MyRating` means the film was logged but not rated.

Catalog files use the same columns minus the user-specific ones (`MyRating`, `Difference`, `ReviewDate`).

## Refreshing data

`scripts/refresh_data.py` rebuilds the user CSVs and the catalog from Letterboxd. Set the CONFIG variables near the top of the script, then run it from the repo root:

```bash
python scripts/refresh_data.py
```

| Setting | Meaning |
|---|---|
| `COMMAND` | `"user"` refreshes the users listed in `USERNAMES`. `"users"` refreshes every `data/users/AllFilms*.csv`. `"catalog"` refreshes `data/catalog/TopFilms2.csv` (every film in it, plus every film any user has seen). `"all"` does users, then the catalog. |
| `USERNAMES` | Used with `"user"`, for example `["cloakenswagger"]` |
| `EXPORT` | Path to a Letterboxd export `.zip` or folder. Use it with `"user"` and a single username. |
| `MAX_AGE_DAYS` | Film pages older than this are fetched again. Default 30; `0` refetches everything. |
| `DELAY` | Seconds between requests. Default 1.0. |

**How it works**

- Each film page (`letterboxd.com/film/<slug>/`) is fetched once and cached in `data/cache/films.jsonl`. That includes the rating, number of ratings and reviews, runtime, languages, director, genres, country and billed cast. Films fetched within `MAX_AGE_DAYS` are skipped.
- The script runs one request at a time, about 1 per second (`DELAY`), and identifies itself honestly in its User-Agent. If Letterboxd starts challenging requests, the script pauses, then stops. Progress is saved, so rerunning continues where it left off.
- Old CSVs only have titles, so each title is matched to its film page by trying `/film/<title>/` and `/film/<title>-<year>/` and checking the year. A match also has to agree on the director (by surname) when it's known. Titles it can't match, or only matched on year with a different director, are listed in `data/cache/unresolved.csv` for review. Unmatched films are kept unchanged in the output.

**Where a user's films come from**

Letterboxd blocks automated access to page 2 and beyond of a member's film lists, so the script can only see a user's recent activity on its own. The full list comes from:

1. The user's existing CSV.
2. **Their Letterboxd data export, if provided.** This is the only way to get a complete, current history. The user downloads it from letterboxd.com → Settings → Data → Export your data, and you run:
   Set `COMMAND = "user"`, `USERNAMES = ["<username>"]` and `EXPORT = "path/to/letterboxd-<username>.zip"`, then run the script.
3. The first page of their films (the 72 most recent) and their RSS feed (recent diary entries with ratings and watch dates).

**Adding a new user:** get their export, run the command above, then add the username to the `options` list in `intro.py`.

Full runs take a while: about 1 hour per 3,000 films that aren't already cached. The first catalog refresh is roughly 9–10k films, about 3 hours.

See [SCOPE.md](SCOPE.md) for project status, known issues and open questions.
