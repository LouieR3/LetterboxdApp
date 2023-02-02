def app():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    st.header('Decade Ranked')
    st.caption('Here are ...')

    file = user()
    df = pd.read_csv(file)

    df['decade'] = (df["ReleaseYear"]//10)*10
    df['MyRating'] = (df["MyRating"]*2)
    # group the dataframe by user and decade
    user_decade_group = df.groupby(["decade"])

    # calculate the total number of movies seen by each user
    user_total_movies = len(df)

    # calculate the sum of ratings for each decade seen by each user
    decade_sum_ratings = user_decade_group["MyRating"].sum()

    # calculate the total number of movies seen by each user for each decade
    decade_total_movies = user_decade_group["Movie"].count()

    # calculate the average rating for each decade seen by each user
    decade_avg_ratings = decade_sum_ratings / decade_total_movies

    # create a dataframe with the average rating for each decade seen by each user
    decade_ratings = pd.DataFrame({"Average Rating": decade_avg_ratings, "Total Movies": decade_total_movies})

    # calculate the percentage of movies seen for each decade by each user
    decade_ratings["percentage"] = (decade_ratings["Total Movies"] / len(df)) * 100

    # define the weighting factor
    weight = 0.99

    # create a new column with the weighted sum of ratings and total_movies
    decade_ratings['Weighted Average'] = decade_ratings['Average Rating']*weight + decade_ratings['Total Movies']*(1-weight)

    # print the favorite decade for user 1
    decade_ratings= decade_ratings.sort_values(by=['Weighted Average'], ascending=False)
    decade_ratings["Ranking"] = range(1, len(decade_ratings) + 1)
    df3 = decade_ratings.style.background_gradient(subset=['Weighted Average'])
    # df2.index += 1 
    st.dataframe(df3, height=425, width=2000)
