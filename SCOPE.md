# Project Scope & Status

_Last updated: 2026-10-09._

## Goal

A Streamlit app for me and my friends on Letterboxd:

1. **Taste stats:** which directors, actors, genres, themes, eras, runtimes and languages each person rates highest.
2. **Recommendations:** unseen films ranked by how much the person is predicted to like them.
3. **Friends:** comparing everyone's taste.

## Decisions

| Question | Decision |
|---|---|
| Audience | Me and friends. Not a public self-serve tool. |
| Primary user | `cloakenswagger` (me), the default in the app |
| Friends | cloakenswagger, bluegrace11, carmal, goldfishbrain, gr8escape10, prahladsingh, zacierka, stephanie216, rec3, ganonuptilt. seanfennessey was removed. Their data stays in the repo. |
| Data source | Letterboxd. `data/films.csv` is the single source of public film data: the Top 1001 list plus every film a user has logged. |
| Themes | Collected for every film: the up-to-~7 themes shown on the film page. The full "Show All" themes page is behind Letterboxd's bot check, so it isn't fetched. |
| App | Redesigned: multipage navigation, Altair charts, a learned taste model |

## Where it stands

- **App:** 7 pages (Overview, Directors & actors, Genres & themes, Eras/runtimes/languages, All films, Recommendations, Friends). Every page loads for every user under Streamlit's test harness.
- **Recommender:** taste scores plus Letterboxd rating and popularity, with weights learned by ridge regression across all friends. Accuracy is measured on films and users held out of training, and it's shown on the page. Before themes were added, it beat "Letterboxd's average adjusted to your scale" only slightly (0.48★ vs 0.50★ mean error for cloakenswagger). Expect modest gains, not miracles.
- **Data pipeline:** `scripts/refresh_data.py` refreshes users (cheap), then the Top 1001 list, then film data (about 1 film per second, cached and resumable).

### The Letterboxd access situation

Cloudflare challenges automated requests to page 2 and beyond of **member** pages (films, ratings, diary) and to a film's full themes page. Film pages, **list** pages (including all 11 pages of the Top 1001), page 1 of a member's films, and RSS feeds all load normally. Without an export, a user's history is their existing file plus recent activity. **A Letterboxd data export** fills in everything.

The new users (stephanie216, rec3, ganonuptilt) have no older data, so until they send exports the app only knows their roughly 70–120 most recent films.

## Known issues

| Area | Issue |
|---|---|
| History gaps | For anyone without an export: films logged between their last full scrape (mostly 2023) and their recent activity are missing |
| Title matching | Migrating old files matched titles to film pages. A few doubtful matches are listed in `data/cache/unresolved.csv` (e.g. *The Trial* (2017), *$* (1971)). Fix them in `data/slug_overrides.csv`. |
| TV in the pool | A few miniseries that Letterboxd lists as films can show up as recommendations |
| Watch dates | Only diary entries have dates, so watch-activity charts cover a subset of films |

## Next steps

- [ ] Get Letterboxd exports from me and friends, and add them to `EXPORTS`
- [ ] Review `data/cache/unresolved.csv` and add fixes to `data/slug_overrides.csv`
- [ ] Re-check recommender accuracy now that themes are in; tune `SHRINK` / `RIDGE` in `app/model.py` if needed
- [ ] Optionally grow the pool with more lists (add a second list alongside `TOP_LIST`)
- [ ] Redeploy on Streamlit Community Cloud (main file stays `streamlit2.py`; requirements now pin `streamlit>=1.40`)
