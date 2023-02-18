import streamlit as st
import pandas as pd
# Define your cached function using st.cache_data
@st.cache_data()
def load_user_data(user):
    # Load user data for the selected username
    user_data = "AllFilms" + user + ".csv"
     
    return user_data

# Define your Streamlit app pages as functions
def homepage():
    # Let the user select a username from a selectbox
    username = st.selectbox("Select a username", ["goldfishbrain", "cloakenswagger", "carmal"])
    
    # Cache the user data for the selected username
    user_data = load_user_data(username)
    
    # Display the user data on the homepage
    st.write(f"User data for {username}:")
    df = pd.read_csv(user_data)
    df["Genre"] = df["Genre"].str.split(",")
    df["Languages"] = df["Languages"].str.split(",")
    df["Actors"] = df["Actors"].str.split(",")
    df = df.drop(["MovieLength", "NumberOfReviews"], axis=1)
    df = df.rename(columns={"MyRating": "Your Rating", "LBRating": "Letterboxd Rating", "ReviewDate": "Date Reviewed", "LengthInHour": "Movie Length", "Genre": "Genres", "NumberOfRatings": "Number Of Ratings", "ReleaseYear": "Release Year"})
    # st.write(user_data)
    st.dataframe(user_data, height=700, use_container_width=True)

def another_page():
    # Get the selected username from the cached function
    username = st.cache_data_lookup(load_user_data).args[0]
    df = pd.read_csv(username)
    df['MyRating'] = (df["MyRating"]*2)
    df['length'] = (df["MovieLength"]//10)*10
    # group the dataframe by user and length
    user_length_group = df.groupby(["length"])

    # calculate the sum of ratings for each length seen by each user
    length_sum_ratings = user_length_group["MyRating"].sum()

    # calculate the total number of movies seen by each user for each length
    length_total_movies = user_length_group["Movie"].count()

    # calculate the average rating for each length seen by each user
    length_avg_ratings = length_sum_ratings / length_total_movies

    difference = user_length_group["Difference"].mean()

    # create a dataframe with the average rating for each length seen by each user
    length_ratings = pd.DataFrame({"Average Rating": length_avg_ratings, "Total Movies": length_total_movies, "Difference": difference})

    # calculate the percentage of movies seen for each length by each user
    length_ratings["Percentage"] = (length_ratings["Total Movies"] / len(df)) * 100

    # define the weighting factor
    weight = 0.95

    # create a new column with the weighted sum of ratings and total_movies
    length_ratings['Weighted Average'] = length_ratings['Average Rating']*weight + length_ratings['Total Movies']*(1-weight) + length_ratings['Difference']

    # print the favorite length for user 1
    # length_ratings= length_ratings.sort_values(by=['Weighted Average'], ascending=False)
    # length_ratings["Ranking"] = range(1, len(length_ratings) + 1)
    # length_ratings.insert(0, 'length', length_ratings.index)
    # genre_ratings['Genre'] = genre_ratings.index
    # length_ratings = length_ratings.set_index("Ranking")
    length_ratings["Average Rating"] = length_ratings["Average Rating"]/2
    df2 = length_ratings.style.background_gradient(subset=['Weighted Average']).format({"Difference": "{:.2f}","Average Rating": "{:.2f}","Percentage": "{:.2f}", 'Weighted Average': '{:.2f}'})
    # df2.index += 1 
    st.dataframe(df2, height=700, use_container_width=True)
    # Display the selected username on another page
    st.write(f"You selected the username: {username}")

# Define your Streamlit app navigation
PAGES = {
    "Homepage": homepage,
    "Another Page": another_page
}

# Run the Streamlit app
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page()