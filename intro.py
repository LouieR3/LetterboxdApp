def app():
    import pandas as pd
    import streamlit as st
    from user import user

    st.header('All Your Movies')
    st.caption('TO PUT HERE.....')
    

    option = st.selectbox(
        'Which user do you want to look at?',
        ('cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka'))

    st.write('You selected:', option)
    file = user(option)
    df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None
    # df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])
    st.dataframe(df, height=700, width=2000)
