def app():
    import pandas as pd
    import os
    from operator import itemgetter
    import streamlit as st
    import numpy as np

    st.header('All Your Movies')
    st.caption('TO PUT HERE.....')
    # dataPath = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\LetterboxdApp"
    # dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
    # user = "goldfishbrain"
    # user = "zacierka"
    # user = "bluegrace11"
    user = "cloakenswagger"
    file = "AllFilms" + user + ".csv"
    # fullCSV = os.path.join(dataPath, file)
    df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None
    # df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])
    st.dataframe(df, height=700, width=2000)
