import streamlit as st
@st.cache_data(experimental_allow_widgets=True)
def user(user):
    # dataPath = "C:\\Users\\louie\\Desktop\\repo\\LetterboxdApp"
    # dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
    # user = "goldfishbrain"
    # user = "zacierka"
    # user = "bluegrace11"
    # user = "cloakenswagger"
    # user = selection
    # user = "gr8escape10"
    # user = "prahladsingh"
    # user = "carmal"
    file = "AllFilms" + user + ".csv"
    st.session_state.key = file
    return file
