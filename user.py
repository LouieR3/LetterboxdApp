import streamlit as st

file = "AllFilmscloakenswagger.csv"

def user(new_value):
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
    global file
    file = "AllFilms" + new_value + ".csv"
    st.session_state.my_global_variable = file
    # return file

def get_user():
    return st.session_state.my_global_variable