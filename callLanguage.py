def langMovies(option):
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    # import streamlit as st
    from user import user

    file = user(option)
    # file = user()
    df = pd.read_csv(file)

    df['MyRating'] = (df["MyRating"]*2)
    df = df[df["Languages"].notna()]
    df['language'] = df['Languages'].str.split(',').str[0]
    # group the dataframe by user and language
    user_language_group = df.groupby(["language"])

    # calculate the total number of movies seen by each user
    user_total_movies = len(df)

    # calculate the sum of ratings for each language seen by each user
    language_sum_ratings = user_language_group["MyRating"].sum()

    # calculate the total number of movies seen by each user for each language
    language_total_movies = user_language_group["Movie"].count()

    # calculate the average rating for each language seen by each user
    language_avg_ratings = language_sum_ratings / language_total_movies

    # create a dataframe with the average rating for each language seen by each user
    difference = user_language_group["Difference"].mean()

    # create a dataframe with the average rating for each language seen by each user
    language_ratings = pd.DataFrame({"Average Rating": language_avg_ratings, "Total Movies": language_total_movies, "Difference": difference})

    # define the weighting factor
    weight = 0.95

    # create a new column with the weighted sum of ratings and Total Movies
    language_ratings['Weighted Average'] = language_ratings['Average Rating']*weight + language_ratings['Total Movies']*(1-weight) + language_ratings['Difference']

    language_ratings= language_ratings.sort_values(by=['Weighted Average'], ascending=False)
    # print the favorite language for user 1
    language_ratings = language_ratings.drop(["Average Rating", "Total Movies", "Difference"], axis=1)
    # language_ratings["Ranking"] = range(1, len(language_ratings) + 1)
    # language_ratings.insert(0, 'language', language_ratings.index)
    # language_ratings = language_ratings.set_index("Ranking")
    return language_ratings
