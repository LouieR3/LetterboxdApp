def lenMovies(option):
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    # import streamlit as st
    from user import user

    file = user(option)
    # file = user()
    df = pd.read_csv(file)

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

    # define the weighting factor
    weight = 0.95

    # create a new column with the weighted sum of ratings and total_movies
    length_ratings['Weighted Average'] = length_ratings['Average Rating']*weight + length_ratings['Total Movies']*(1-weight) + length_ratings['Difference']
    length_ratings = length_ratings.drop(["Average Rating", "Total Movies", "Difference"], axis=1)
    length_ratings= length_ratings.sort_values(by=['Weighted Average'], ascending=False)
    # length_ratings["Ranking"] = range(1, len(length_ratings) + 1)
    # length_ratings.insert(0, 'length', length_ratings.index)
    # length_ratings['length'] = length_ratings.index
    # length_ratings = length_ratings.set_index("Ranking")
    return length_ratings
