def app():
    import pandas as pd
    import streamlit as st
    from user import user

    st.header('All Your Movies')
    # st.write('TO PUT HERE.....')

    # option = 'cloakenswagger'
    option = st.selectbox( 'Which user do you want to look at?',
            ('cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka'), on_change=user(option))

    st.write('You selected:', option)

    file = user(option)
    df = pd.read_csv(file)
    df["Genre"] = df["Genre"].str.split(",")
    df["Languages"] = df["Languages"].str.split(",")
    df["Actors"] = df["Actors"].str.split(",")
    df = df.drop(["MovieLength", "NumberOfReviews"], axis=1)
    df = df.rename(columns={"MyRating": "Your Rating", "LBRating": "Letterboxd Rating", "ReviewDate": "Date Reviewed", "LengthInHour": "Movie Length", "Genre": "Genres", "NumberOfRatings": "Number Of Ratings", "ReleaseYear": "Release Year"}) 
    pd.options.mode.chained_assignment = None
    # df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])
    st.dataframe(df, height=700, use_container_width=True)
