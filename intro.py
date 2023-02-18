def app():
    import pandas as pd
    import streamlit as st
    from user import user

    st.header('All Your Movies')
    # st.write('TO PUT HERE.....')
    options = ['cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka', 'goldfishbrain']
    if st.session_state != None:
        st.write(st.session_state)
    for key in st.session_state:
        st.write(key)
        del st.session_state
    # option = 'cloakenswagger'
    st.selectbox('Which user do you want to look at?', options, on_change=lambda value: st.session_state.update_option(value))
    # print(option)
    # Define a default value for the session variable
    if "selected_option" not in st.session_state:
        st.session_state.key = options[0]
        
    st.write('You selected:', st.session_state.key)

    file = user(st.session_state.key)
    df = pd.read_csv(file)
    df["Genre"] = df["Genre"].str.split(",")
    df["Languages"] = df["Languages"].str.split(",")
    df["Actors"] = df["Actors"].str.split(",")
    df = df.drop(["MovieLength", "NumberOfReviews"], axis=1)
    df = df.rename(columns={"MyRating": "Your Rating", "LBRating": "Letterboxd Rating", "ReviewDate": "Date Reviewed", "LengthInHour": "Movie Length", "Genre": "Genres", "NumberOfRatings": "Number Of Ratings", "ReleaseYear": "Release Year"}) 
    pd.options.mode.chained_assignment = None
    # df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])
    st.dataframe(df, height=700, use_container_width=True)
