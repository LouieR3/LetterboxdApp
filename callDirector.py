def directorMovies(option):
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    # import streamlit as st
    from user import user

    file = user(option)
    # file = user()
    df = pd.read_csv(file)
    df['MyRating'] = (df["MyRating"]*2)
    # group the dataframe by user and director
    user_director_group = df.groupby(["Director"])

    # calculate the sum of ratings for each director seen by each user
    director_sum_ratings = user_director_group["MyRating"].sum()

    # calculate the total number of movies seen by each user for each director
    director_total_movies = user_director_group["Movie"].count()
    director_difference = user_director_group["Difference"].mean()

    # calculate the average rating for each director seen by each user
    director_avg_ratings = director_sum_ratings / director_total_movies

    # create a dataframe with the average rating for each director seen by each user
    director_ratings = pd.DataFrame({"Average Rating": director_avg_ratings, "Total Movies": director_total_movies, "Difference": director_difference})

    # create a new column with the weighted sum of ratings and total_movies
    director_ratings['Weighted Average'] = director_ratings['Average Rating']*0.9 + ((director_ratings["Total Movies"] + director_ratings['Difference'])*0.2)

    # print the favorite director for user 1
    director_ratings= director_ratings.sort_values(by=['Weighted Average'], ascending=False)
    director_ratings = director_ratings.drop(["Total Movies", "Average Rating", "Difference"], axis=1)
    # director_ratings["Ranking"] = range(1, len(director_ratings) + 1)
    # director_ratings = director_ratings[:50]
    # director_ratings.insert(0, 'Director', director_ratings.index)
    # director_ratings = director_ratings.set_index("Ranking")
    return director_ratings