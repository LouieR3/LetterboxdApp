import altair as alt
import pandas as pd
import streamlit as st

from app import data, model, ui

user = ui.setup()
df = data.load_user(user)
ui.header("Eras, runtimes & languages", "When your favourite films were made, how long they run, and where they come from.")
if not ui.needs_ratings(df):
    st.stop()
r = model.rated(df)


def avg_bars(table: pd.DataFrame, x: str, title: str, sort=None) -> alt.Chart:
    """Bars for film counts with your average rating as a line on a second axis."""
    base = alt.Chart(table).encode(x=alt.X(f"{x}:O", title=title, sort=sort))
    bars = base.mark_bar(color=ui.BLUE, opacity=0.55, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        y=alt.Y("Films:Q", title="Films", axis=alt.Axis(titleColor=ui.BLUE)),
        tooltip=[x, "Films", alt.Tooltip("Avg rating:Q", format=".2f"), alt.Tooltip("Taste score:Q", format="+.2f")])
    line = base.mark_line(color=ui.GREEN, point=alt.OverlayMarkDef(color=ui.GREEN, size=60)).encode(
        y=alt.Y("Avg rating:Q", title="Your avg ★", scale=alt.Scale(zero=False), axis=alt.Axis(titleColor=ui.GREEN)))
    return alt.layer(bars, line).resolve_scale(y="independent").properties(height=320)


eras, runtime, places = st.tabs(["📅 Eras", "⏱️ Runtime", "🌍 Languages & countries"])

with eras:
    decades = model.affinity_table(df, "Decade").rename(columns={"Item": "Decade"})
    best = decades[decades["Films"] >= 5].iloc[0] if (decades["Films"] >= 5).any() else decades.iloc[0]
    c = st.columns(3)
    c[0].metric("Favourite decade", best["Decade"], f"{best['Taste score']:+.2f}★ vs your average")
    c[1].metric("Oldest film", int(df["ReleaseYear"].min()) if df["ReleaseYear"].notna().any() else "–")
    c[2].metric("Median release year", int(df["ReleaseYear"].median()) if df["ReleaseYear"].notna().any() else "–")
    st.altair_chart(avg_bars(decades, "Decade", "Decade", sort="ascending"), use_container_width=True)

    st.markdown("**Every film by release year**")
    pts = alt.Chart(r).mark_circle(size=40, opacity=0.5).encode(
        x=alt.X("ReleaseYear:Q", title="Release year", scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
        y=alt.Y("MyRating:Q", title="Your rating", scale=alt.Scale(domain=[0, 5.2])),
        color=alt.Color("Difference:Q", scale=ui.DIVERGING, legend=None),
        tooltip=["Movie", "ReleaseYear", "MyRating", "LBRating"])
    trend = alt.Chart(r).transform_loess("ReleaseYear", "MyRating", bandwidth=0.4).mark_line(color=ui.ORANGE, size=3).encode(
        x="ReleaseYear:Q", y="MyRating:Q")
    st.altair_chart((pts + trend).properties(height=300).interactive(), use_container_width=True)

with runtime:
    order = sorted(df["MovieLength"].dropna().map(model.runtime_bucket).unique(),
                   key=lambda b: (b != "Under 90 min", b == "3 h +", b))
    runtimes = model.affinity_table(df, "Runtime").rename(columns={"Item": "Runtime"})
    c = st.columns(3)
    c[0].metric("Average runtime", f"{df['MovieLength'].mean():.0f} min")
    c[1].metric("Longest", f"{df['MovieLength'].max():.0f} min", df.loc[df["MovieLength"].idxmax(), "Movie"], delta_color="off")
    sweet = runtimes[runtimes["Films"] >= 5].iloc[0] if (runtimes["Films"] >= 5).any() else runtimes.iloc[0]
    c[2].metric("Sweet spot", sweet["Runtime"], f"{sweet['Taste score']:+.2f}★")
    st.altair_chart(avg_bars(runtimes, "Runtime", "Runtime", sort=order), use_container_width=True)
    st.markdown("**Rating vs runtime**")
    st.altair_chart(alt.Chart(r).mark_circle(size=40, opacity=0.5, color=ui.BLUE).encode(
        x=alt.X("MovieLength:Q", title="Runtime (min)", scale=alt.Scale(zero=False)),
        y=alt.Y("MyRating:Q", title="Your rating"),
        tooltip=["Movie", "MovieLength", "MyRating"],
    ).properties(height=280).interactive() + alt.Chart(r).transform_loess("MovieLength", "MyRating").mark_line(
        color=ui.ORANGE, size=3).encode(x="MovieLength:Q", y="MyRating:Q"), use_container_width=True)

with places:
    left, right = st.columns(2, gap="large")
    for col, group, label in [(left, "Language", "Language"), (right, "Country", "Country")]:
        with col:
            table = model.affinity_table(df, group)
            st.markdown(f"**{label}s you watch most**")
            top = table.nlargest(12, "Films")
            st.altair_chart(alt.Chart(top).mark_bar(cornerRadiusEnd=3).encode(
                x=alt.X("Films:Q"), y=alt.Y("Item:N", sort="-x", title=None),
                color=alt.Color("Avg rating:Q", scale=alt.Scale(scheme="viridis", domain=[2.5, 5]), title="Avg ★"),
                tooltip=[alt.Tooltip("Item:N", title=label), "Films", alt.Tooltip("Avg rating:Q", format=".2f")],
            ).properties(height=320), use_container_width=True)
            st.dataframe(table, hide_index=True, use_container_width=True, height=300,
                         column_config={**ui.TASTE_COLUMNS, "Item": label})
