def decadeMovies(option):
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    # import streamlit as st
    from user import user

    file = user(option)
    # file = user()
    df = pd.read_csv(file)

    df['decade'] = (df["ReleaseYear"]//10)*10
    df['MyRating'] = (df["MyRating"]*2)
    # group the dataframe by user and decade
    user_decade_group = df.groupby(["decade"])

    # calculate the sum of ratings for each decade seen by each user
    decade_sum_ratings = user_decade_group["MyRating"].sum()

    # calculate the total number of movies seen by each user for each decade
    decade_total_movies = user_decade_group["Movie"].count()

    difference = user_decade_group["Difference"].mean()

    # calculate the average rating for each decade seen by each user
    decade_avg_ratings = decade_sum_ratings / decade_total_movies

    # create a dataframe with the average rating for each decade seen by each user
    decade_ratings = pd.DataFrame({"Average Rating": decade_avg_ratings, "Total Movies": decade_total_movies, "Difference": difference})

    # calculate the percentage of movies seen for each decade by each user
    decade_ratings["percentage"] = (decade_ratings["Total Movies"] / len(df)) * 100

    # define the weighting factor
    weight = 0.99

    # create a new column with the weighted sum of ratings and total_movies
    decade_ratings['Weighted Average'] = decade_ratings['Average Rating']*weight + decade_ratings['Total Movies']*(1-weight) + decade_ratings['Difference']

    # print the favorite decade for user 1
    decade_ratings= decade_ratings.sort_values(by=['Weighted Average'], ascending=False)
    decade_ratings = decade_ratings.drop(["Total Movies", "Average Rating", "percentage", "Billing Score"], axis=1)
    decade_ratings["Ranking"] = range(1, len(decade_ratings) + 1)
    decade_ratings.insert(0, 'decade', decade_ratings.index)
    decade_ratings = decade_ratings.set_index("Ranking")
    return decade_ratings
