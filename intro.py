def app():
    import pandas as pd
    import streamlit as st
    from user import user
    from user import get_user

    st.header('All Your Movies')
    # st.write('TO PUT HERE.....')
    options = ['cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka', 'goldfishbrain']

    # option = 'cloakenswagger'
    username = st.selectbox('Which user do you want to look at?', options)
    username.on_change=(lambda value: user(value.new))
    # print(option)
    # Define a default value for the session variable
    if "key" not in st.session_state:
        st.session_state.key = options[0]
        
    st.write('You selected:', st.session_state.key)

    file = get_user()
    df = pd.read_csv(file)
    df["Genre"] = df["Genre"].str.split(",")
    df["Languages"] = df["Languages"].str.split(",")
    df["Actors"] = df["Actors"].str.split(",")
    df = df.drop(["MovieLength", "NumberOfReviews"], axis=1)
    df = df.rename(columns={"MyRating": "Your Rating", "LBRating": "Letterboxd Rating", "ReviewDate": "Date Reviewed", "LengthInHour": "Movie Length", "Genre": "Genres", "NumberOfRatings": "Number Of Ratings", "ReleaseYear": "Release Year"}) 
    pd.options.mode.chained_assignment = None
    # df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])
    st.dataframe(df, height=700, use_container_width=True)
