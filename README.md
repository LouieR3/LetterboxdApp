# Letterboxd Stats

A Streamlit app for a group of friends on Letterboxd. It breaks down each person's taste (directors, actors, genres, themes, eras, runtimes, languages), recommends films they haven't seen, and compares everyone's ratings.

**Live app:** https://louier3-letterboxd-stats.streamlit.app/ (Streamlit Community Cloud; it sleeps when idle, so the first load can take a minute)

## Run it locally

Requires Python 3.10+.

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
streamlit run streamlit2.py
```

(On macOS/Linux, activate with `source .venv/bin/activate`.)

## Pages

Pick whose films to look at in the sidebar; the choice carries across pages and is kept in the URL (`?user=`).

| Page | What it shows |
|---|---|
| Overview | Headline numbers, your rating distribution next to Letterboxd's, your ratings vs Letterboxd's, watch activity by month, your hottest and coldest takes, recent watches |
| Directors & actors | Leaderboards by **taste score**, with charts, search and links to your films on Letterboxd |
| Genres & themes | Taste score by genre, a genre × decade heatmap, and the Letterboxd themes you love or don't |
| Eras, runtimes & languages | Decades and release years, runtime sweet spot, languages and countries |
| All films | Searchable, filterable table of everything logged |
| Recommendations | Unseen films ranked by predicted rating, with filters, "because you like…" reasons, a per-signal breakdown, rewatch suggestions, and the model's measured accuracy |
| Friends | Leaderboard of everyone, head-to-head taste match, biggest disagreements, and a friend's favourites you haven't seen |

**Taste score** means how many stars above or below your own average you rate films with that director, genre, theme and so on, pulled toward zero when it's based on only a few films. The recommender predicts a rating from those taste scores plus each film's Letterboxd rating and popularity, using weights learned from everyone's ratings.

## Repo layout

```
streamlit2.py            App entry point (Streamlit Cloud's main file: don't rename without updating the deployment)
app/
  data.py                Loads and joins the CSVs below (cached)
  model.py               Taste scores and the recommendation model
  ui.py                  Shared styling, user picker, chart helpers
  views/                 One file per page
.streamlit/config.toml   Theme

data/
  films.csv              The definitive film table (see below)
  top_list.csv           The Top 1001 list's films and ranks
  users/<user>.csv       Each user's logged films: slug, title, year, rating, watch date
  watchlists/<user>.csv  Each user's watchlist: slug, title, year, date added
  slug_overrides.csv     Optional hand fixes for titles the matcher gets wrong (title,year,slug)
  lists/                 Old scraped Letterboxd lists (not used by the app)
  cache/                 Scraper cache (git-ignored)

scripts/refresh_data.py  Refreshes everything from Letterboxd
```

## Data

**`data/films.csv`** is the single source of public film data. It has one row per film, covering every film in the [Top 1001 list](https://letterboxd.com/juliodogpit/list/the-1001-greatest-films-ranked-as-objectively/) plus every film any user has logged or has on their watchlist:

`Slug, Movie, ReleaseYear, LBRating, NumberOfRatings, NumberOfReviews, MovieLength, Director, Directors, Genre, Themes, Languages, Country, Actors, TopRank, FetchedAt`

- `LBRating` is the Letterboxd average (0.5–5). `TopRank` is the film's position in the Top 1001 list, or blank if it isn't on it.
- `Directors`, `Genre`, `Languages` and `Actors` are comma-separated, with actors in billing order. `Themes` is `|`-separated, because theme names contain commas. These are the themes Letterboxd shows on the film page, up to about 7.

**`data/users/<user>.csv`** holds only the personal part: `Slug, Movie, ReleaseYear, MyRating, Watched`. A blank `MyRating` means the film was logged but not rated. The app joins this with `films.csv` on `Slug`.

Recommendations are drawn from `films.csv`: feature films (60–275 min) with a Letterboxd rating that the user hasn't logged. That means the Top 1001, anything a friend has seen, and everyone's watchlists. The Recommendations page also ranks your watchlist and can filter to it.

## Refreshing data

Set the CONFIG variables at the top of `scripts/refresh_data.py`, then run it from the repo root:

```bash
python scripts/refresh_data.py
```

| Setting | Meaning |
|---|---|
| `COMMAND` | `"all"`: users, then the Top 1001 list, then film data. `"users"`: only the users (and the film data for their films). `"films"`: only film data. |
| `USERS` | The friend group. Each gets a `data/users/<user>.csv`, and their films go into `films.csv`. |
| `REFRESH_USERS` | `None` refreshes everyone, or a subset such as `["cloakenswagger"]` |
| `EXPORTS` | Only needed for an export that isn't in the repo folder. Any `letterboxd-<user>-*.zip` there (or in `exports/`) is picked up automatically, newest first. |
| `TOP_LIST` | The list that defines the general film pool |
| `MAX_AGE_DAYS` | Film pages older than this are fetched again. Default 30; `0` refetches everything. |
| `DELAY` | Seconds between requests. Default 1.0. |

**The order of a run, cheapest first:**

1. **Users:** about 2 requests each (RSS feed, plus the first page of their films) to add recent activity to what's already in their file.
2. **Top list:** 11 requests for the list's 1,001 films.
3. **Film data:** one request per film in the combined set, skipped if it was fetched within `MAX_AGE_DAYS`. Each film is fetched once however many users logged it, and cached, so an interrupted run resumes where it stopped.

Letterboxd has no bulk source for ratings, counts or themes, so step 3 is the slow one: about 1 film per second, so a full refresh of ~4k films takes a bit over an hour. Later runs within `MAX_AGE_DAYS` only fetch new films.

**Where a user's history comes from.** Letterboxd blocks automated access to page 2 and beyond of a member's film lists, and this script doesn't try to get around that. On its own it sees the films already in the user's file plus their recent activity: roughly the last 70–120 films. **A Letterboxd data export** (letterboxd.com → Settings → Data → Export your data) fills in the complete history and watchlist. Drop the zip, named as Letterboxd names it (`letterboxd-<user>-<date>.zip`), in the repo folder and run. The export is treated as the truth up to its date: its ratings replace older ones (so re-ratings show up), and older entries it doesn't contain are dropped. Anything logged after the export still comes in through RSS. Exports contain personal data (email, profile), so `letterboxd-*.zip` is gitignored. Without an export, watchlists only cover the first page (28 films).

**Adding a user:** add them to `USERS` (and drop their export zip in the repo folder if they've sent one) and run. The app picks up every file in `data/users/` automatically.

**Fixing a wrong match:** old files only had titles, so the first migration matched each title to a film page by guessing the URL and checking the year and director. Doubtful matches and misses are listed in `data/cache/unresolved.csv`. To fix one, add a `title,year,slug` row to `data/slug_overrides.csv`.

The scraper sends an honest User-Agent and waits between requests. If Letterboxd starts challenging requests, it pauses, then stops. Progress is saved, so you can rerun later.

See [SCOPE.md](SCOPE.md) for project status and next steps.
