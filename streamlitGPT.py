
import streamlit as st
import pandas as pd
# Define your cached function using st.cache_data
# file = ""
@st.cache_data()
def load_user_data(user):
    user_data = "AllFilms" + user + ".csv"
    st.session_state.key = user_data
    global file
    file = user_data
    return user_data

def homepage():
    username = st.selectbox("Select a username", ["goldfishbrain", "cloakenswagger", "carmal"])
    user_data = load_user_data(username)
    
    st.write(f"User data for {username}:")
    df = pd.read_csv(user_data)
    df["Genre"] = df["Genre"].str.split(",")
    df["Languages"] = df["Languages"].str.split(",")
    df["Actors"] = df["Actors"].str.split(",")
    df = df.drop(["MovieLength", "NumberOfReviews"], axis=1)
    df = df.rename(columns={"MyRating": "Your Rating", "LBRating": "Letterboxd Rating", "ReviewDate": "Date Reviewed", "LengthInHour": "Movie Length", "Genre": "Genres", "NumberOfRatings": "Number Of Ratings", "ReleaseYear": "Release Year"})

    st.dataframe(df, height=700, use_container_width=True)

def another_page():
    username = st.session_state.key
    st.write(username)
    df = pd.read_csv(username)
    df['MyRating'] = (df["MyRating"]*2)
    df['length'] = (df["MovieLength"]//10)*10
    user_length_group = df.groupby(["length"])
    length_sum_ratings = user_length_group["MyRating"].sum()
    length_total_movies = user_length_group["Movie"].count()
    length_avg_ratings = length_sum_ratings / length_total_movies
    difference = user_length_group["Difference"].mean()
    length_ratings = pd.DataFrame({"Average Rating": length_avg_ratings, "Total Movies": length_total_movies, "Difference": difference})
    length_ratings["Percentage"] = (length_ratings["Total Movies"] / len(df)) * 100
    weight = 0.95
    length_ratings['Weighted Average'] = length_ratings['Average Rating']*weight + length_ratings['Total Movies']*(1-weight) + length_ratings['Difference']
    length_ratings["Average Rating"] = length_ratings["Average Rating"]/2
    df2 = length_ratings.style.background_gradient(subset=['Weighted Average']).format({"Difference": "{:.2f}","Average Rating": "{:.2f}","Percentage": "{:.2f}", 'Weighted Average': '{:.2f}'})
    st.dataframe(df2, height=700, use_container_width=True)
    st.write(f"You selected the username: {username}")

PAGES = {
    "Homepage": homepage,
    "Another Page": another_page
}
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page()