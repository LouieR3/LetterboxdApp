def app():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    st.header('Your Favorite Movies by Length in Minutes')
    st.write('This is how much you like a movie by 10 minute increments')

    # option = 'cloakenswagger'
    # option = st.selectbox(
    #     'Which user do you want to look at?',
    #     ('cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka'))
    option = st.session_state.my_global_variable
    st.write('You selected:', option.split("AllFilms")[1].split(".csv")[0])
    # file = user(option)
    file = option
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
