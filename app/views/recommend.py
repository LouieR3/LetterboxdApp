import altair as alt
import pandas as pd
import streamlit as st

from app import data, model, ui

user = ui.setup()
df = data.load_user(user)
ui.header("Recommendations", "Films you haven't logged, ranked by the rating the taste model expects you'd give them.")
if not ui.needs_ratings(df, 20):
    st.stop()

r = model.rated(df)
weights, accuracy = model.fit(data.data_signature())


@st.cache_data(show_spinner="Scoring the catalog…")
def scored(username: str, _sig: tuple) -> pd.DataFrame:
    user_df = data.load_user(username)
    cand = model.unseen(data.load_catalog(), user_df)
    out = model.predict(model.rated(user_df), cand, weights)
    watch = data.load_watchlist(username).set_index("Slug")["Added"]
    out["OnWatchlist"] = out["Slug"].isin(watch.index)
    out["Added"] = out["Slug"].map(watch)
    return out


@st.cache_data(show_spinner=False)
def rewatch(username: str, _sig: tuple) -> pd.DataFrame:
    rr = model.rated(data.load_user(username))
    out = model.predict(rr, rr, weights, loo=True)
    out["Upside"] = out["Predicted"] - out["MyRating"]
    return out


picks_tab, watchlist_tab, rewatch_tab, how_tab = st.tabs(
    ["✨ For you", "📋 Your watchlist, ranked", "🔁 Worth a rewatch", "🧪 How it works"])

with picks_tab:
    recs = scored(user, data.data_signature())
    with st.expander("Filters", expanded=True):
        c = st.columns(4)
        all_genres = sorted({g for gs in recs["Genre"] for g in gs})
        genres = c[0].multiselect("Genres (any of)", all_genres)
        years = c[1].slider("Released", int(recs["ReleaseYear"].min()), int(recs["ReleaseYear"].max()),
                            (int(recs["ReleaseYear"].min()), int(recs["ReleaseYear"].max())))
        max_len = c[2].slider("Max runtime (min)", 60, 275, 275, step=5)
        min_votes = c[3].select_slider("Min Letterboxd ratings", [0, 1_000, 10_000, 50_000, 100_000, 500_000], 10_000,
                                       format_func=lambda v: f"{v:,}")
        t1, t2, t3 = st.columns(3)
        watch_only = t1.toggle("Only films on my watchlist", False)
        top_only = t2.toggle("Only films from the Top 1001 list", False)
        hide_seen_directors = t3.toggle("Only directors I haven't seen yet", False)
    view = recs[(recs["ReleaseYear"].between(*years)) & (recs["MovieLength"] <= max_len)
                & (recs["NumberOfRatings"].fillna(0) >= min_votes)]
    if genres:
        view = view[view["Genre"].map(lambda gs: bool(set(gs) & set(genres)))]
    if watch_only:
        view = view[view["OnWatchlist"]]
    if top_only:
        view = view[view["TopRank"].notna()]
    if hide_seen_directors:
        view = view[~view["Director"].isin(set(df["Director"]))]
    view = view.sort_values("Predicted", ascending=False).head(50).copy()
    if view.empty:
        st.info("No films match those filters.")
    else:
        view["Why"] = model.reasons(r, view)
        view["Out of 10"] = (view["Predicted"] * 2).round(1)
        view["Genres"] = view["Genre"].map(", ".join)
        view["Link"] = view.apply(data.film_url, axis=1)
        top = view.iloc[0]
        st.markdown(f"#### Top pick: **{top['Movie']}** ({top['ReleaseYear']}) · predicted {ui.stars(top['Predicted'])}")
        if top["Why"]:
            st.caption(f"Because you like {top['Why']}")
        st.dataframe(view[["Movie", "ReleaseYear", "Predicted", "Out of 10", "LBRating", "OnWatchlist", "TopRank", "Director", "Genres",
                           "Why", "Link"]],
                     hide_index=True, use_container_width=True, height=600, column_config={
                         "Movie": st.column_config.TextColumn("Film", width="medium"),
                         "ReleaseYear": st.column_config.NumberColumn("Year", format="%d"),
                         "Predicted": st.column_config.ProgressColumn("Predicted ★", format="%.2f", min_value=0.5, max_value=5),
                         "Out of 10": st.column_config.NumberColumn("/10", format="%.1f"),
                         "LBRating": st.column_config.NumberColumn("Letterboxd", format="★ %.2f"),
                         "OnWatchlist": st.column_config.CheckboxColumn("📋", help="On your watchlist"),
                         "TopRank": st.column_config.NumberColumn("Top 1001", format="#%d",
                                                                  help="Rank in the Top 1001 list, if it's on it"),
                         "Why": st.column_config.TextColumn("Because you like", width="large"),
                         "Link": st.column_config.LinkColumn("", display_text="↗"),
                     })
        st.markdown("**Where each pick's score comes from**")
        parts = view.head(15).melt(id_vars=["Movie"], value_vars=[f"c_{f}" for f in model.FEATURES],
                                   var_name="Signal", value_name="Stars")
        parts["Signal"] = parts["Signal"].str.removeprefix("c_")
        st.altair_chart(alt.Chart(parts).mark_bar().encode(
            x=alt.X("sum(Stars):Q", title="Contribution (★ above/below your average)"),
            y=alt.Y("Movie:N", sort=list(view.head(15)["Movie"]), title=None),
            color=alt.Color("Signal:N", scale=alt.Scale(scheme="tableau10")),
            tooltip=["Movie", "Signal", alt.Tooltip("Stars:Q", format="+.2f")],
        ).properties(height=420), use_container_width=True)

with watchlist_tab:
    wl = scored(user, data.data_signature())
    wl = wl[wl["OnWatchlist"]].sort_values("Predicted", ascending=False).copy()
    if wl.empty:
        st.info("No watchlist for this user yet. It comes from their Letterboxd export "
                "(plus the first page of their live watchlist) via `scripts/refresh_data.py`.")
    else:
        st.markdown("Everything on your watchlist that you haven't logged, best bets first.")
        c = st.columns(3)
        c[0].metric("On your watchlist", f"{len(wl):,}")
        c[1].metric("Predicted ★4 or higher", f"{(wl['Predicted'] >= 4).sum():,}")
        c[2].metric("Hours to clear it", f"{wl['MovieLength'].sum() / 60:,.0f}")
        wl["Why"] = model.reasons(r, wl.head(60)) + [""] * max(0, len(wl) - 60)
        wl["Link"] = wl.apply(data.film_url, axis=1)
        st.dataframe(wl[["Movie", "ReleaseYear", "Predicted", "LBRating", "MovieLength", "Added", "Director", "Why", "Link"]],
                     hide_index=True, use_container_width=True, height=560, column_config={
                         "Movie": st.column_config.TextColumn("Film", width="medium"),
                         "ReleaseYear": st.column_config.NumberColumn("Year", format="%d"),
                         "Predicted": st.column_config.ProgressColumn("Predicted ★", format="%.2f", min_value=0.5, max_value=5),
                         "LBRating": st.column_config.NumberColumn("Letterboxd", format="★ %.2f"),
                         "MovieLength": st.column_config.NumberColumn("Runtime", format="%d min"),
                         "Added": st.column_config.DateColumn("Added", format="MMM D, YYYY"),
                         "Why": st.column_config.TextColumn("Because you like", width="large"),
                         "Link": st.column_config.LinkColumn("", display_text="↗"),
                     })
        st.altair_chart(alt.Chart(wl).mark_circle(size=70, opacity=0.75).encode(
            x=alt.X("LBRating:Q", title="Letterboxd average", scale=alt.Scale(zero=False)),
            y=alt.Y("Predicted:Q", title="Predicted for you", scale=alt.Scale(zero=False)),
            color=alt.Color("MovieLength:Q", scale=alt.Scale(scheme="blues"), title="Runtime"),
            tooltip=["Movie", "ReleaseYear", alt.Tooltip("Predicted:Q", format=".2f"), "LBRating", "MovieLength"],
        ).properties(height=320, title="Your watchlist: crowd favourite vs your fit").interactive(), use_container_width=True)

with rewatch_tab:
    st.markdown("Films you rated well below what the model expects, given everything else you like. "
                "Maybe it was the mood that day.")
    rw = rewatch(user, data.data_signature())
    rw = rw[rw["Upside"] >= 0.75].sort_values("Upside", ascending=False).head(25)
    if rw.empty:
        st.info("No big surprises: your ratings are very consistent with your taste.")
    else:
        rw["Why"] = model.reasons(r, rw)
        st.dataframe(rw[["Movie", "ReleaseYear", "MyRating", "Predicted", "Upside", "LBRating", "Why"]], hide_index=True,
                     use_container_width=True, column_config={
                         "Movie": "Film", "ReleaseYear": st.column_config.NumberColumn("Year", format="%d"),
                         "MyRating": st.column_config.NumberColumn("You gave", format="★ %.1f"),
                         "Predicted": st.column_config.NumberColumn("Model expects", format="★ %.1f"),
                         "Upside": st.column_config.NumberColumn("Upside", format="+%.1f"),
                         "LBRating": st.column_config.NumberColumn("Letterboxd", format="★ %.2f"),
                         "Why": st.column_config.TextColumn("Things you usually like", width="large")})

with how_tab:
    st.markdown("""
For every director, actor, genre, theme, decade, runtime band, language and country, the model works out your
**affinity**: how many stars above or below your own average you rate films that have it. Each affinity is pulled
toward zero when it comes from only a few films. A candidate film's prediction is your average plus a weighted
sum of its affinities, plus its Letterboxd rating and popularity.

The weights are learned from all the friends' ratings at once. The errors below are measured on each person
using weights learned **only from the other people**, with each film's own rating left out of its features.
That makes them honest estimates of how far off a prediction typically is.
""")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**What the model listens to**")
        w = weights.rename("Weight").rename_axis("Signal").reset_index()
        st.altair_chart(alt.Chart(w).mark_bar(cornerRadiusEnd=3).encode(
            x="Weight:Q", y=alt.Y("Signal:N", sort="-x", title=None),
            color=alt.condition("datum.Weight > 0", alt.value(ui.GREEN), alt.value(ui.ORANGE)),
            tooltip=["Signal", alt.Tooltip("Weight:Q", format=".3f")]).properties(height=300), use_container_width=True)
    with right:
        st.markdown("**Average error, in stars (lower is better)**")
        if not accuracy.empty:
            long = accuracy.melt(id_vars=["User", "Rated films"], var_name="Method", value_name="Error")
            st.altair_chart(alt.Chart(long).mark_bar().encode(
                x=alt.X("Error:Q", title="Mean absolute error (★)"), y=alt.Y("User:N", title=None), yOffset="Method:N",
                color=alt.Color("Method:N", scale=alt.Scale(range=[ui.GREEN, ui.BLUE, ui.MUTED]),
                                legend=alt.Legend(orient="bottom", title=None)),
                tooltip=["User", "Method", alt.Tooltip("Error:Q", format=".3f"), "Rated films"]).properties(height=360),
                use_container_width=True)
    st.caption("“Letterboxd-average” predicts the film's Letterboxd rating shifted to your average; "
               "“Your-average” always predicts your mean rating.")
