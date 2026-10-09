import altair as alt
import pandas as pd
import streamlit as st

from app import data, model, ui

user = ui.setup()
df = data.load_user(user)
ui.header("Genres & themes", "What kinds of films you gravitate to, and which ones you actually rate highly.")
if not ui.needs_ratings(df):
    st.stop()

genres_tab, themes_tab = st.tabs(["🎞️ Genres", "🧭 Themes"])

with genres_tab:
    table = model.affinity_table(df, "Genres")
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown("**Taste score by genre**")
        st.altair_chart(ui.taste_bar(table, "Genre"), use_container_width=True)
    with right:
        st.markdown("**How much you watch vs how much you like**")
        st.altair_chart(alt.Chart(table).mark_circle(opacity=0.85).encode(
            x=alt.X("Films:Q", title="Films seen", scale=alt.Scale(type="log")),
            y=alt.Y("Avg rating:Q", title="Your avg ★", scale=alt.Scale(zero=False)),
            size=alt.Size("Films:Q", legend=None, scale=alt.Scale(range=[60, 1200])),
            color=alt.Color("Taste score:Q", scale=ui.DIVERGING, legend=None),
            tooltip=[alt.Tooltip("Item:N", title="Genre"), "Films", alt.Tooltip("Avg rating:Q", format=".2f")],
        ).properties(height=440) + alt.Chart(table).mark_text(dy=-12, fontSize=11, color=ui.MUTED).encode(
            x=alt.X("Films:Q", scale=alt.Scale(type="log")), y="Avg rating:Q", text="Item:N"),
            use_container_width=True)

    st.markdown("**Genre × decade** (average rating; darker = more films)")
    r = model.rated(df)
    long = r[["Genre", "Decade", "MyRating"]].explode("Genre").dropna()
    top = table.nlargest(12, "Films")["Item"]
    heat = long[long["Genre"].isin(top)].groupby(["Genre", "Decade"]).agg(
        Avg=("MyRating", "mean"), Films=("MyRating", "size")).reset_index()
    heat["Decade"] = heat["Decade"].astype(int).astype(str) + "s"
    base = alt.Chart(heat).encode(x=alt.X("Decade:O", title=None), y=alt.Y("Genre:N", title=None, sort=list(top)))
    st.altair_chart((base.mark_rect(cornerRadius=3).encode(
        color=alt.Color("Avg:Q", scale=alt.Scale(scheme="viridis", domain=[2.5, 4.5]), title="Avg ★"),
        opacity=alt.Opacity("Films:Q", scale=alt.Scale(range=[0.35, 1], type="log"), legend=None),
        tooltip=["Genre", "Decade", alt.Tooltip("Avg:Q", format=".2f"), "Films"],
    ) + base.mark_text(fontSize=10).encode(text=alt.Text("Avg:Q", format=".1f"))).properties(height=34 * len(top)),
        use_container_width=True)

with themes_tab:
    covered = df["Themes"].map(len).gt(0).mean()
    if covered == 0:
        st.info("No theme data yet. Themes are collected by `scripts/refresh_data.py`; rerun it to fill them in.")
        st.stop()
    table = model.affinity_table(df, "Themes")
    min_films = st.slider("Minimum films with the theme", 1, 15, 3)
    table = table[table["Films"] >= min_films]
    st.caption(f"Letterboxd tags each film with up to ~7 themes. {covered:.0%} of this user's films have theme data.")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**Themes you love**")
        st.altair_chart(ui.taste_bar(table, "Theme", n=15), use_container_width=True)
    with right:
        st.markdown("**Themes that don't land**")
        st.altair_chart(ui.taste_bar(table.sort_values("Taste score").head(15).iloc[::-1], "Theme", n=15),
                        use_container_width=True)
    st.markdown("**Most-watched themes**")
    ui.tags(f"{t} · {n}" for t, n in table.nlargest(25, "Films")[["Item", "Films"]].itertuples(index=False))
    st.dataframe(table, hide_index=True, use_container_width=True, height=420,
                 column_config={**ui.TASTE_COLUMNS, "Item": "Theme"})
