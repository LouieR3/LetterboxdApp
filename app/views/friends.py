import altair as alt
import pandas as pd
import streamlit as st

from app import data, model, ui

user = ui.setup()
users = data.list_users()
ui.header("Friends", "How everyone's taste stacks up, and where you agree and disagree.")


@st.cache_data(show_spinner=False)
def leaderboard(_sig: tuple) -> pd.DataFrame:
    rows = []
    for u in data.list_users():
        d = data.load_user(u)
        r = model.rated(d)
        directors = model.affinity_table(d, "Director")
        genres = model.affinity_table(d, "Genres")
        rows.append({
            "User": u, "Films": len(d), "Rated": len(r), "Avg rating": r["MyRating"].mean(),
            "vs Letterboxd": r["Difference"].mean(), "Hours": d["MovieLength"].sum() / 60,
            "Median year": d["ReleaseYear"].median(),
            "Favourite director": directors[directors["Films"] >= 2]["Item"].iloc[0] if (directors["Films"] >= 2).any() else "–",
            "Favourite genre": genres[genres["Films"] >= 5]["Item"].iloc[0] if (genres["Films"] >= 5).any() else "–",
        })
    return pd.DataFrame(rows)


board = leaderboard(data.data_signature())
st.dataframe(board, hide_index=True, use_container_width=True, column_config={
    "Films": st.column_config.NumberColumn(format="%d"),
    "Rated": st.column_config.NumberColumn(format="%d"),
    "Avg rating": st.column_config.NumberColumn("Avg ★", format="%.2f"),
    "vs Letterboxd": st.column_config.NumberColumn(format="%+.2f",
                                                    help="Positive = more generous than the Letterboxd crowd"),
    "Hours": st.column_config.ProgressColumn(format="%.0f h", min_value=0, max_value=float(board["Hours"].max() or 1)),
    "Median year": st.column_config.NumberColumn(format="%d"),
})
st.altair_chart(alt.Chart(board).mark_circle(size=300, opacity=0.85).encode(
    x=alt.X("Avg rating:Q", title="Average rating", scale=alt.Scale(zero=False)),
    y=alt.Y("vs Letterboxd:Q", title="Generosity vs Letterboxd"),
    color=alt.Color("User:N", legend=None), size=alt.Size("Films:Q", legend=None, scale=alt.Scale(range=[150, 1500])),
    tooltip=["User", "Films", alt.Tooltip("Avg rating:Q", format=".2f"), alt.Tooltip("vs Letterboxd:Q", format="+.2f")],
).properties(height=320) + alt.Chart(board).mark_text(dy=-20, color=ui.MUTED).encode(
    x="Avg rating:Q", y="vs Letterboxd:Q", text="User:N"), use_container_width=True)

st.divider()
others = [u for u in users if u != user]
if not others:
    st.stop()
friend = st.selectbox(f"Compare **{user}** with", others)
a, b = model.rated(data.load_user(user)), model.rated(data.load_user(friend))
a["Key"] = a["Slug"].fillna(a["TitleKey"])
b["Key"] = b["Slug"].fillna(b["TitleKey"])
shared = a.merge(b[["Key", "MyRating"]], on="Key", suffixes=("", "_friend"))
shared["Gap"] = shared["MyRating"] - shared["MyRating_friend"]

c = st.columns(4)
c[0].metric("Films you've both rated", f"{len(shared):,}")
corr = shared["MyRating"].corr(shared["MyRating_friend"]) if len(shared) >= 5 else float("nan")
c[1].metric("Taste match", "–" if pd.isna(corr) else f"{corr:.0%}", help="Correlation of your ratings on shared films")
c[2].metric("Agree within ½★", f"{(shared['Gap'].abs() <= 0.5).mean():.0%}" if len(shared) else "–")
c[3].metric(f"{friend} vs you", f"{-shared['Gap'].mean():+.2f}★" if len(shared) else "–",
            help=f"On shared films, {friend}'s average rating minus yours")

if len(shared):
    left, right = st.columns([3, 2], gap="large")
    with left:
        jitter = shared.assign(x=shared["MyRating"], y=shared["MyRating_friend"])
        counts = jitter.groupby(["x", "y"]).agg(Films=("Movie", "size"), Titles=("Movie", lambda t: ", ".join(t[:4]))).reset_index()
        st.altair_chart(alt.Chart(counts).mark_circle(opacity=0.8, color=ui.GREEN).encode(
            x=alt.X("x:Q", title=f"{user} ★", scale=alt.Scale(domain=[0, 5.25])),
            y=alt.Y("y:Q", title=f"{friend} ★", scale=alt.Scale(domain=[0, 5.25])),
            size=alt.Size("Films:Q", scale=alt.Scale(range=[30, 1200]), legend=None),
            tooltip=["Films", "Titles"]).properties(height=360, title="Every shared film"), use_container_width=True)
    with right:
        st.markdown("**Biggest disagreements**")
        cols = {"Movie": "Film", "MyRating": st.column_config.NumberColumn(user, format="★ %.1f"),
                "MyRating_friend": st.column_config.NumberColumn(friend, format="★ %.1f")}
        st.dataframe(shared.reindex(shared["Gap"].abs().sort_values(ascending=False).index).head(12)[
            ["Movie", "MyRating", "MyRating_friend"]], hide_index=True, use_container_width=True, column_config=cols)

st.markdown(f"**{friend}'s favourites you haven't logged**")
mine = data.load_user(user)
seen = set(mine["Slug"].dropna()) | set(mine["TitleKey"])
picks = b[(b["MyRating"] >= 4.5) & ~(b["Slug"].isin(seen) | b["TitleKey"].isin(seen))]
picks = picks.sort_values(["MyRating", "LBRating"], ascending=False).head(20)
if picks.empty:
    st.caption("Nothing yet: you've seen all their top-rated films.")
else:
    st.dataframe(picks[["Movie", "ReleaseYear", "MyRating", "LBRating", "Director"]], hide_index=True,
                 use_container_width=True, column_config={
                     "Movie": "Film", "ReleaseYear": st.column_config.NumberColumn("Year", format="%d"),
                     "MyRating": st.column_config.NumberColumn(f"{friend}", format="★ %.1f"),
                     "LBRating": st.column_config.NumberColumn("Letterboxd", format="★ %.2f")})
