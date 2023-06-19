def app():
    import pandas as pd
    import streamlit as st
    from user import user
    from user import get_user

    st.header('All Your Movies')
    # st.write('TO PUT HERE.....')
    options = ['cloakenswagger', 'carmal', 'prahladsingh',
               'bluegrace11', 'gr8escape10', 'zacierka', 'goldfishbrain', 'seanfennessey']

    # option = 'cloakenswagger'
    selectUser = st.selectbox('Which user do you want to look at?', options)
    st.button('Change User', on_click=user, args=(selectUser, ))
    # print(option)
    # Define a default value for the session variable
    if "my_global_variable" not in st.session_state:
        st.session_state.my_global_variable = "AllFilms" + options[0] + ".csv"

    st.write('You selected:', st.session_state.my_global_variable.split(
        "AllFilms")[1].split(".csv")[0])

    file = get_user()
    df = pd.read_csv(file)
    df = df.dropna(subset=['MyRating'])
    dfAvg = df[(df["MovieLength"] > 60) & (df["MovieLength"] < 275)]
    avg = dfAvg["MyRating"].sum() / dfAvg["Movie"].count()

    df["Genre"] = df["Genre"].str.split(",")
    df["Languages"] = df["Languages"].str.split(",")
    df["Actors"] = df["Actors"].str.split(",")

    df = df.drop(["MovieLength", "NumberOfReviews"], axis=1)
    df.index = df.index + 1
    df = df.rename(columns={"MyRating": "Your Rating", "LBRating": "Letterboxd Rating", "ReviewDate": "Date Reviewed",
                   "LengthInHour": "Movie Length", "Genre": "Genres", "NumberOfRatings": "Number Of Ratings", "ReleaseYear": "Release Year"})
    pd.options.mode.chained_assignment = None
    # df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])

    avgRound = "{:.2f}".format(avg)
    totalMovies = len(df)
    st.write(
        f'Your average rating across all movies is: **{avgRound}** over **{totalMovies}** amount of movies')

    st.dataframe(df, height=700, use_container_width=True)
