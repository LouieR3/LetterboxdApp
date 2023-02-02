def app():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    st.header('Your Favorite Movies by Length in Minutes')
    st.caption('Here are ...')

    file = user()
    df = pd.read_csv(file)

    df['MyRating'] = (df["MyRating"]*2)
    df['length'] = (df["MovieLength"]//10)*10
    # group the dataframe by user and length
    user_length_group = df.groupby(["length"])

    # calculate the total number of movies seen by each user
    user_total_movies = len(df)

    # calculate the sum of ratings for each length seen by each user
    length_sum_ratings = user_length_group["MyRating"].sum()

    # calculate the total number of movies seen by each user for each length
    length_total_movies = user_length_group["Movie"].count()

    # calculate the average rating for each length seen by each user
    length_avg_ratings = length_sum_ratings / length_total_movies

    # create a dataframe with the average rating for each length seen by each user
    length_ratings = pd.DataFrame({"Average Rating": length_avg_ratings, "Total Movies": length_total_movies})

    # calculate the percentage of movies seen for each length by each user
    length_ratings["Percentage"] = (length_ratings["Total Movies"] / len(df)) * 100



    # find the favorite length for each user
    # favorite_length = length_ratings.loc[length_ratings.groupby("user_id")["percentage"].idxmax()]

    # define the weighting factor
    weight = 0.95

    # create a new column with the weighted sum of ratings and total_movies
    length_ratings['Weighted Average'] = length_ratings['Average Rating']*weight + length_ratings['Total Movies']*(1-weight)

    # find the favorite length for each user
    # favorite_length = length_ratings.loc[length_ratings.groupby("user_id")["Weighted Average"].idxmax()]

    # print the favorite length for user 1
    length_ratings= length_ratings.sort_values(by=['Weighted Average'], ascending=False)
    df2 = length_ratings.style.background_gradient(subset=['Final Weighted'])
    # df2.index += 1 
    st.dataframe(df2, height=700, width=2000)
