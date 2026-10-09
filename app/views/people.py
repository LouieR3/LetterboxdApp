import altair as alt
import streamlit as st

from app import data, model, ui

user = ui.setup()
df = data.load_user(user)
ui.header("Directors & actors", "Ranked by taste score: how far above your own average you rate their films, "
          "with a pull toward zero when you've only seen a few.")
if not ui.needs_ratings(df):
    st.stop()

ROLE_PATH = {"Director": "director", "Actors": "actor"}

for tab, group, label in zip(st.tabs(["🎬 Directors", "🎭 Actors"]), ["Director", "Actors"], ["Director", "Actor"]):
    with tab:
        table = model.affinity_table(df, group)
        c1, c2 = st.columns([1, 2])
        min_films = c1.slider("Minimum films seen", 1, 10, 3 if group == "Actors" else 2, key=f"min_{group}")
        query = c2.text_input(f"Search {label.lower()}s", key=f"q_{group}", placeholder="e.g. Wes Anderson")
        table = table[table["Films"] >= min_films]
        if query:
            table = table[table["Item"].str.contains(query, case=False, regex=False)]
        if table.empty:
            st.info("Nothing matches those filters.")
            continue

        left, right = st.columns([3, 2], gap="large")
        with left:
            st.markdown(f"**Top {min(20, len(table))} {label.lower()}s**")
            st.altair_chart(ui.taste_bar(table, label), use_container_width=True)
        with right:
            st.markdown("**Most watched**")
            most = table.nlargest(15, "Films")
            st.altair_chart(alt.Chart(most).mark_circle(opacity=0.8).encode(
                x=alt.X("Films:Q", title="Films seen"), y=alt.Y("Avg rating:Q", title="Your avg ★", scale=alt.Scale(zero=False)),
                size=alt.Size("Films:Q", legend=None, scale=alt.Scale(range=[80, 900])),
                color=alt.Color("Taste score:Q", scale=ui.DIVERGING, legend=None),
                tooltip=[alt.Tooltip("Item:N", title=label), "Films", alt.Tooltip("Avg rating:Q", format=".2f"),
                         alt.Tooltip("Taste score:Q", format="+.2f")],
            ).properties(height=max(220, 22 * min(20, len(table)))), use_container_width=True)

        table = table.copy()
        table.insert(0, "Rank", range(1, len(table) + 1))
        table["Letterboxd"] = table["Item"].map(
            lambda n: f"https://letterboxd.com/{user}/films/with/{ROLE_PATH[group]}/{data.name_slug(n)}/")
        st.dataframe(table, hide_index=True, use_container_width=True, height=480, column_config={
            **ui.TASTE_COLUMNS, "Item": label,
            "Letterboxd": st.column_config.LinkColumn("Your films", display_text="open ↗"),
        })
