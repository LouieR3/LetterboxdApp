def app():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    st.header('Genre Ranked')
    st.caption('Here are your favorite genres ranked by the average rating of the movies you have watched, accounting for the number of their films you have seen, and the difference in the average rating you have for the director compared to Letterboxd')

    file = user()
    df = pd.read_csv(file)

    df['MyRating'] = (df["MyRating"]*2)

    # split the genres column into multiple rows
    split_df = df["Genre"].str.split(",").apply(pd.Series)
    split_df = split_df.drop([4, 5], axis=1)

    # join the split dataframe back to the original dataframe
    df = df.join(split_df)

    # ReviewDate,MovieLength,LengthInHour,Languages,Director,ReleaseYear
    df = df.drop(['LBRating',  'ReviewDate', 'MovieLength', 'LengthInHour', 'Languages', 'Director', 'ReleaseYear', 'Country', 'NumberOfReviews', 'NumberOfRatings', 'Actors'], axis=1)

    # rename the columns
    df.columns = ["Movie", "MyRating", "Difference", "Genre", "genre_1", "genre_2", "genre_3", "genre_4"]

    # # drop the original genres column
    # df = df.drop(["Genre"], axis=1)
    genres_list = df[["genre_1", "genre_2", "genre_3", "genre_4"]].stack().unique()


    # MAKE LIST WITH THOSE NUMS PLUS THE WEIGHTED AND THEN MAKE DF OF THAT LIST AFTER
    checkList = []
    for genre in genres_list:
        # create a boolean mask to select the 
        # rows where the genre is contained in the genres column
        mask = df["Genre"].str.contains(genre)
        # calculate the average rating for the selected rows
        avg_rating = df.loc[mask, "MyRating"].mean()
        difference = df.loc[mask, "Difference"].mean()
        total_movies = df.loc[mask, "MyRating"].count()

        # print the average rating
        checkList.append([genre, avg_rating, total_movies, difference])
        # checkList.append([genre, avg_rating, total_movies])

    # create a dataframe with the average rating for each genre seen by each user
    genre_ratings = pd.DataFrame(checkList, columns =['Genre', 'avg_rating', 'Total', 'Difference']).set_index('Genre')
    # genre_ratings = pd.DataFrame(checkList, columns =['Genre', 'avg_rating', 'Total']).set_index('Genre')

    # calculate the percentage of movies seen for each genre by each user
    genre_ratings["percentage"] = (genre_ratings["Total"] / len(df)) * 100

    # define the weighting factor
    weight = 0.98

    # create a new column with the weighted sum of ratings and total_movies
    # genre_ratings['weighted_sum'] = (genre_ratings['avg_rating']*weight) + (genre_ratings['Total']*(1-weight)) + genre_ratings['Difference']
    genre_ratings['weighted_sum'] = (genre_ratings['avg_rating']*weight) + (genre_ratings['Total']*(1-weight)) + genre_ratings['Difference']

    # print the favorite genre for user 1
    genre_ratings= genre_ratings.sort_values(by=['weighted_sum'], ascending=False)
    df3 = genre_ratings.style.background_gradient(subset=['Ranking'])
    # df2.index += 1 
    st.dataframe(df3, height=700, width=2000)
