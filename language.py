def app():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    st.header('Language Ranked')
    st.write('Here are your favorite languages of movies ranked')

    # option = 'cloakenswagger'
    # option = st.selectbox(
    #     'Which user do you want to look at?',
    #     ('cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka'))
    option = st.session_state.my_global_variable
    st.write('You selected:', option.split("AllFilms")[1].split(".csv")[0])
    # file = user(option)
    file = option
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

    # calculate the percentage of movies seen for each language by each user
    language_ratings["Percentage"] = (language_ratings["Total Movies"] / len(df)) * 100

    # define the weighting factor
    weight = 0.95

    # create a new column with the weighted sum of ratings and Total Movies
    language_ratings['Weighted Average'] = language_ratings['Average Rating']*weight + language_ratings['Total Movies']*(1-weight) + language_ratings['Difference']

    language_ratings= language_ratings.sort_values(by=['Weighted Average'], ascending=False)
    # print the favorite language for user 1
    language_ratings["Ranking"] = range(1, len(language_ratings) + 1)
    language_ratings["Average Rating"] = language_ratings["Average Rating"]/2
    language_ratings.insert(0, 'language', language_ratings.index)
    language_ratings = language_ratings.set_index("Ranking")
    df3 = language_ratings.style.background_gradient(subset=['Weighted Average']).format({"Difference": "{:.2f}","Average Rating": "{:.2f}","Percentage": "{:.2f}", 'Weighted Average': '{:.2f}'})
    # df2.index += 1 
    st.dataframe(df3, height=700, use_container_width=True)
