import streamlit as st

from app import data, ui

user = ui.setup()
df = data.load_user(user)
ui.header("All films", "Search and filter everything logged.")

c = st.columns([2, 2, 1, 1])
query = c[0].text_input("Search title, director or actor", placeholder="e.g. Kubrick")
genres = c[1].multiselect("Genres", sorted({g for gs in df["Genre"] for g in gs}))
min_rating = c[2].select_slider("Your rating ≥", [0.0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], 0.0)
rated_only = c[3].toggle("Rated only", False)

view = df
if query:
    q = query.lower()
    view = view[view["Movie"].str.lower().str.contains(q, regex=False)
                | view["Director"].str.lower().str.contains(q, regex=False)
                | view["Actors"].map(lambda xs: any(q in a.lower() for a in xs))]
if genres:
    view = view[view["Genre"].map(lambda gs: bool(set(gs) & set(genres)))]
if min_rating:
    view = view[view["MyRating"] >= min_rating]
if rated_only:
    view = view[view["MyRating"].notna()]

view = view.assign(Genres=view["Genre"].map(", ".join), Cast=view["Actors"].map(lambda xs: ", ".join(xs[:5])),
                   ThemeList=view["Themes"].map(", ".join), Link=view.apply(data.film_url, axis=1))
st.caption(f"{len(view):,} films")
st.dataframe(view[["Movie", "ReleaseYear", "MyRating", "LBRating", "Difference", "Watched", "Director", "Genres",
                   "MovieLength", "Language", "Cast", "ThemeList", "NumberOfRatings", "Link"]],
             hide_index=True, use_container_width=True, height=720, column_config={
                 "Movie": st.column_config.TextColumn("Film", width="medium"),
                 "ReleaseYear": st.column_config.NumberColumn("Year", format="%d"),
                 "MyRating": st.column_config.NumberColumn("You", format="★ %.1f"),
                 "LBRating": st.column_config.NumberColumn("Letterboxd", format="★ %.2f"),
                 "Difference": st.column_config.NumberColumn("Gap", format="%+.2f"),
                 "Watched": st.column_config.DateColumn("Watched", format="MMM D, YYYY"),
                 "MovieLength": st.column_config.NumberColumn("Runtime", format="%d min"),
                 "ThemeList": st.column_config.TextColumn("Themes", width="large"),
                 "NumberOfRatings": st.column_config.NumberColumn("LB ratings", format="%d"),
                 "Link": st.column_config.LinkColumn("", display_text="↗"),
             })
