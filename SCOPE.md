# Project Scope & Status

_Last updated: 2026-10-09. Last code commit before this round of work: 2024-08-01._

## Goal

Turn a Letterboxd user's rating history into:

1. **Taste stats:** which actors, directors, genres, decades, languages and runtimes the user rates highest, adjusted for sample size and for how far they rate above or below the Letterboxd average.
2. **Recommendations:** a ranked list of films the user hasn't seen, scored against that taste profile plus each film's Letterboxd rating and popularity.

## Decisions (2026-10-09)

| Question | Decision |
|---|---|
| Audience | Me and friends. Not a public self-serve tool. |
| Primary user | `cloakenswagger` (me), and it's the default user in the app. |
| Friends' data | Keep it in the repo. |
| Data source | Stay with Letterboxd. |
| Recommender | Keep it, but improve and modernize it. |
| Archive | Deleted. |
| Priority | Active project. **First:** a big refresh of every user's data and the general film data (ratings, number of ratings and reviews, etc.), starting with my account. |

## Where it stands

### Working

- A Streamlit app (`streamlit2.py`) with 9 pages: Home, 6 stats pages and 2 recommendation pages. Every page loads for every user: 72/72 page × user combinations pass on Streamlit 1.65 and pandas 3.0.
- 8 users in `data/users/`: seanfennessey (2,428 films), cloakenswagger, prahladsingh (626), goldfishbrain (287), carmal (189), zacierka (89), gr8escape10 (87), bluegrace11 (53).
- A recommendation catalog of about 9,300 films (`data/catalog/TopFilms2.csv`).
- **New:** `scripts/refresh_data.py`, a single cached and resumable scraper that refreshes user histories and the catalog. It replaces the 11 old scripts. See the README for usage.

### The Letterboxd access situation (important)

Since the old scrapers were written, Letterboxd has put Cloudflare bot protection on **page 2 and beyond of every member listing** (`/<user>/films/page/2/`, `/films/ratings/`, `/films/diary/`, `/diary/page/2/`). Automated requests to those pages get a challenge, and the scraper doesn't try to get around it. Still open to a normal, honest client:

| Page | Gives us |
|---|---|
| `/film/<slug>/` | All film data: rating, counts, runtime, cast, crew, genres, languages, country |
| `/<user>/films/` (page 1 only) | The user's 72 most recently watched films, with their ratings |
| `/<user>/rss/` | Recent diary entries, with rating and watch date |

What this means:
- **Film data can be fully refreshed.** That covers the catalog and every film in every user's file.
- **A user's new films are only picked up from recent activity.** Films logged between the last scrape (mostly 2023) and roughly the last 70–80 entries are missed. A user's **Letterboxd data export** (Settings → Data → Export your data) gives the complete list, and the script takes it with `--export`. For friends, that means asking them to send you the zip.

`robots.txt` allows all of the pages the script uses. It disallows `/by/` sort pages, which the old `pullFilmsByDate.py` used.

### Data refresh progress

| Dataset | Status |
|---|---|
| cloakenswagger | Refreshed 2026-10-09 (film data updated, recent activity added). Export not applied yet. |
| Other 7 users | Not yet refreshed |
| Catalog (`TopFilms2.csv`) | Not yet refreshed (~9.3k films, ~3 h) |

## Cleanup done (2026-10-09)

- **Removed:** committed `__pycache__/`; `streamlit.py`, an unrelated map demo whose name **shadowed the real `streamlit` package**; the Delco/Swarthmore parcel GIS code and data; scratch test files; `archive/`, which held 29 old experiments; and the 11 old scrapers (they relied on markup and pagination that no longer work). All of it is recoverable from git history.
- **Reorganized:** data now lives in `data/users`, `data/catalog` and `data/lists`. `data/cache/` (git-ignored) holds the scraper cache.
- **Bugs fixed:**
  - Genre and both recommendation pages crashed for every user on pandas 3. `stack()` now keeps NaN values.
  - Recommendations crashed for 4 users when a taste bucket contained only unrated films.
  - The old new-user scraper wrote the wrong column name (`userRating` instead of `MyRating`).

## Known issues / tech debt

| Area | Issue |
|---|---|
| Dependencies | Versions aren't pinned, which is how pandas 3 broke the app. |
| Performance | Nothing is cached in the app. Every page re-reads its CSV and rebuilds every taste table. The recommenders loop over ~9k films row by row on every rerun. |
| State | The selected user only changes when **Change User** is clicked. Changing the dropdown alone does nothing. |
| Duplication | Each stat is computed twice: in the page module (`genre.py`) and in its `call*.py` twin used by the recommenders. |
| Matching | The app matches films by **title**, so seen films are excluded from recommendations by title, and same-title films collide. The cache now has slugs, so the app could switch to matching on slug. |
| Hidden pages | `country.py` and `year.py` are hidden from navigation and would crash: `ratings.py` calls `user()` without its required argument. |
| Recommender | Its weights are hand-picked and have never been measured against real ratings. |

## Roadmap

**Phase 1: Data refresh** (in progress)
- [x] New cached, resumable scraper (`scripts/refresh_data.py`)
- [x] Refresh cloakenswagger
- [ ] Apply cloakenswagger's Letterboxd export for the complete history since 2023
- [ ] Refresh the other 7 users (ideally with their exports)
- [ ] Refresh the catalog (`python scripts/refresh_data.py catalog`, about 3 hours)
- [ ] Optionally, grow the catalog with more films (for example from public lists or the most popular films). This needs a decision on which sources to use.

**Phase 2: Modernize the app and recommender**
- One module per stat instead of the page plus `call*.py` pairs. Use `st.cache_data`, pinned dependencies, and make the user dropdown take effect immediately.
- Match films on slug instead of title.
- Measure the recommender: hold out some of each user's ratings and check how well each version predicts them. Then tune the weights, or try collaborative filtering across the 8 users, or a hybrid.
- Add rewatch suggestions and a 0–10 score scale (from the old `ideas.txt`).

## Open questions

1. **Your export:** can you download your Letterboxd export and drop the zip in the repo folder (or tell me where it is)? That fills in everything you've logged since late 2023.
2. **Friends' exports:** are your friends willing to send theirs? Otherwise their data can only be refreshed with film stats plus recent activity.
3. **Catalog size:** should the catalog stay at about 9.3k films, or grow? If it grows, which sources (public lists, popular films, everything your friends have seen)?
4. **Deployment:** keep Streamlit Community Cloud? Is it OK to rename `streamlit2.py` → `app.py`? That needs a change in the Streamlit Cloud settings.
5. **Old lists:** are `data/lists/movies-of-YYYY.csv` and the favorites list still useful? Nothing in the app reads them.
