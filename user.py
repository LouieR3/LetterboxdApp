import streamlit as st

file = None

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
    global file
    file = "AllFilms" + user + ".csv"
    st.session_state.key = user
    # return file

def get_user():
    return file