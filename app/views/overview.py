import altair as alt
import pandas as pd
import streamlit as st

from app import data, model, ui

user = ui.setup()
df = data.load_user(user)
r = model.rated(df)
ui.header(f"{user}'s films", "Everything logged on Letterboxd, at a glance.")
if not ui.needs_ratings(df):
    st.stop()

hours = df["MovieLength"].sum() / 60
c = st.columns(5)
c[0].metric("Films logged", f"{len(df):,}")
c[1].metric("Average rating", ui.stars(r["MyRating"].mean()))
c[2].metric("Hours watched", f"{hours:,.0f}", help="Sum of runtimes of every logged film")
c[3].metric("vs Letterboxd", f"{r['Difference'].mean():+.2f}★",
            help="How much higher (or lower) you rate films than the Letterboxd average, on average")
c[4].metric("Directors seen", f"{df['Director'].replace('', pd.NA).nunique():,}")

left, right = st.columns(2, gap="large")
with left:
    st.subheader("How you rate")
    dist = pd.concat([
        r["MyRating"].round(1).value_counts().rename("You"),
        (r["LBRating"] * 2).round().div(2).value_counts().rename("Letterboxd average"),
    ], axis=1).fillna(0).rename_axis("Stars").reset_index().melt("Stars", var_name="Who", value_name="Films")
    st.altair_chart(
        alt.Chart(dist).mark_bar(opacity=0.85, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("Stars:O", title="Stars"), xOffset="Who:N", y=alt.Y("Films:Q"),
            color=alt.Color("Who:N", scale=alt.Scale(range=[ui.GREEN, ui.MUTED]), legend=alt.Legend(orient="top", title=None)),
            tooltip=["Who", "Stars", "Films"],
        ).properties(height=320), use_container_width=True)
with right:
    st.subheader("You vs Letterboxd")
    diag = alt.Chart(pd.DataFrame({"x": [0.5, 5], "y": [0.5, 5]})).mark_line(color=ui.MUTED, strokeDash=[4, 4]).encode(x="x", y="y")
    pts = alt.Chart(r).mark_circle(size=45, opacity=0.65).encode(
        x=alt.X("LBRating:Q", title="Letterboxd average", scale=alt.Scale(domain=[0.5, 5])),
        y=alt.Y("MyRating:Q", title="Your rating", scale=alt.Scale(domain=[0.5, 5.2])),
        color=alt.Color("Difference:Q", scale=ui.DIVERGING, legend=None),
        tooltip=["Movie", "ReleaseYear", alt.Tooltip("MyRating", title="You"), alt.Tooltip("LBRating", title="Letterboxd"),
                 alt.Tooltip("Difference", format="+.2f")],
    )
    st.altair_chart((diag + pts).properties(height=320).interactive(), use_container_width=True)

st.subheader("When you watched")
dated = df.dropna(subset=["Watched"])
if dated.empty:
    st.caption("No watch dates in this user's data.")
else:
    monthly = dated.set_index("Watched").resample("MS").agg(Films=("Movie", "size"), Avg=("MyRating", "mean")).reset_index()
    st.altair_chart(alt.Chart(monthly).mark_bar(color=ui.ORANGE, cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
        x=alt.X("Watched:T", title=None), y=alt.Y("Films:Q", title="Films per month"),
        tooltip=[alt.Tooltip("Watched:T", format="%B %Y", title="Month"), "Films", alt.Tooltip("Avg:Q", format=".2f", title="Avg ★")],
    ).properties(height=220), use_container_width=True)
    st.caption(f"{len(dated):,} of {len(df):,} films have a diary date.")

left, right = st.columns(2, gap="large")
cols = {"Movie": "Film", "ReleaseYear": st.column_config.NumberColumn("Year", format="%d"),
        "MyRating": st.column_config.NumberColumn("You", format="★ %.1f"),
        "LBRating": st.column_config.NumberColumn("Letterboxd", format="★ %.2f"),
        "Difference": st.column_config.NumberColumn("Gap", format="%+.2f")}
show = ["Movie", "ReleaseYear", "MyRating", "LBRating", "Difference"]
with left:
    st.subheader("🔥 Hot takes: you loved them more")
    st.dataframe(r.nlargest(10, "Difference")[show], column_config=cols, hide_index=True, use_container_width=True)
with right:
    st.subheader("🧊 Cold takes: everyone else liked them more")
    st.dataframe(r.nsmallest(10, "Difference")[show], column_config=cols, hide_index=True, use_container_width=True)

st.subheader("Recently logged")
recent = df.dropna(subset=["Watched"]).sort_values("Watched", ascending=False).head(12)
st.dataframe(recent[["Watched"] + show], hide_index=True, use_container_width=True,
             column_config={**cols, "Watched": st.column_config.DateColumn("Watched", format="MMM D, YYYY")})
