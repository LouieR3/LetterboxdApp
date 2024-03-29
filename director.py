def app():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user
    import unidecode

    st.header('Directors Ranked')
    st.write('Here are your favorite directors ranked by the average rating of the movies you have watched of theirs, accounting for the number of their films you have seen, and the difference in the average rating you have for the director compared to Letterboxd')

    # option = 'cloakenswagger'
    # option = st.selectbox(
    #     'Which user do you want to look at?',
    #     ('cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka'))
    option = st.session_state.my_global_variable
    st.write('You selected:', option.split("AllFilms")[1].split(".csv")[0])
    # file = user(option)
    file = option
    df = pd.read_csv(file)
    df = df[df["Genre"].str.contains("Documentary") == False]
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

    # calculate the percentage of movies seen for each director by each user
    # director_ratings["percentage"] = (director_ratings["Total Movies"] / len(df)) * 100

    # create a new column with the weighted sum of ratings and total_movies
    director_ratings['Weighted Average'] = (director_ratings['Average Rating']*0.9 + ((director_ratings['Total Movies'] + director_ratings['Difference'])*0.2))*2

    # print the favorite director for user 1
    director_ratings= director_ratings.sort_values(by=['Weighted Average'], ascending=False)
    director_ratings["Ranking"] = range(1, len(director_ratings) + 1)
    director_ratings["Average Rating"] = director_ratings["Average Rating"]/2
    director_ratings['Weighted Average'] = director_ratings['Weighted Average'] - director_ratings["Ranking"]/10
    director_ratings = director_ratings[:50]
    director_ratings.insert(0, 'Director', director_ratings.index)
    director_ratings = director_ratings.set_index("Ranking")

    df3 = director_ratings.style.background_gradient(subset=['Weighted Average']).format({"Difference": "{:.2f}","Average Rating": "{:.2f}", 'Weighted Average': '{:.2f}'})

    
    # df2.index += 1 
    st.dataframe(df3, height=700, use_container_width=True)

    director = st.text_input('Check Director', '')
    if director:
        unaccented_string = unidecode.unidecode(director)
        directorSplit = unaccented_string.replace(' ', '-').lower()
        directorSplit = directorSplit.replace('.', '').replace(',', '')
        urlTemp = "https://letterboxd.com/director/" + directorSplit + "/"
        st.write(urlTemp)
