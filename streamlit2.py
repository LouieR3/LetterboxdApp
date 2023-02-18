
import streamlit as st


@st.cache
def get_name():
    return None

def page1():
    name = get_name() or "unknown"
    st.write("Hello, {}! This is page 1.".format(name))
    set_name()

def page2():
    name = get_name() or "unknown"
    st.write("Hello, {}! This is page 2.".format(name))
    set_name()

def page3():
    name = get_name() or "unknown"
    st.write("Hello, {}! This is page 3.".format(name))
    set_name()

def set_name():
    name = st.text_input("What is your name?")
    if name:
        get_name.cache_clear()
        get_name.set(name)

# Define the pages and their associated functions
PAGES = {
    "Page 1": page1,
    "Page 2": page2,
    "Page 3": page3,
}

# Define the sidebar navigation
nav = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[nav]
page()