def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from ratings import ratings
    from user import user
    import unidecode

    st.header('Actors Ranked')
    st.write('Here are your favorite actors ranked by the average rating of the movies you have watched of theirs, accounting for the number of their films you have seen, the difference in the average rating you have for the actor compared to Letterboxd, and the actors billing score. Billing score, being the number of movies you have seen of that actor over the totalality of all that actors placings in the movies billing lists')

    option = 'cloakenswagger'
    option = st.selectbox(
        'Which user do you want to look at?',
        ('cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka'))

    st.write('You selected:', option)
    file = user(option)
    # file = user()
    username = file.split(".cs")[0].split("AllFilms")[1]
    # df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None

    # load the dataframe
    # file = user()
    df = pd.read_csv(file)
    df = df[df["Actors"].notna()]
    print(len(df))
    df = df[df["Genre"].str.contains("Documentary") == False]
    print(len(df))
    df = df[df["Actors"].str.contains(",") == True]
    print(len(df))
    df['MyRating'] = (df["MyRating"]*2)

    key = 15
    actorList = []
    for i in range(key):
        num = i+1
        actStr = "actor_" + str(num)
        actorList.append(str)

    # Step 1: Create a dictionary with actors as keys and a list of their billing positions in each movie as values.
    actors = {}
    for i in range(len(df)):
        subActor = df["Actors"].iloc[i].split(",", 10)
        rating = df["MyRating"].iloc[i]
        difference = df["Difference"].iloc[i]
        for j, actor in enumerate(subActor):
            if actor not in actors:
                actors[actor] = {"Billing Positions": [], "Number of Movies Seen": 0, "Average Rating": [], "Difference": []}
            actors[actor]["Billing Positions"].append(j+1)
            actors[actor]["Number of Movies Seen"] += 1
            actors[actor]["Average Rating"].append(rating)
            actors[actor]["Difference"].append(difference)

    # Step 2: For each actor, calculate the average of their billing positions
    for actor in actors:
        # actors[actor]["Billing Score"] = sum(actors[actor]["Billing Positions"]) / len(actors[actor]["Billing Positions"])
        actors[actor]["Billing Score"] = len(actors[actor]["Billing Positions"]) / sum(actors[actor]["Billing Positions"])
        actors[actor]["Average Rating"] = sum(actors[actor]["Average Rating"]) / len(actors[actor]["Average Rating"])
        actors[actor]["Difference"] = sum(actors[actor]["Difference"]) / len(actors[actor]["Difference"])
        # actors[actor]["weight"] = (actors[actor]["Average Rating"] + 1/(actors[actor]["Billing Score"]*2)) / 2 * (actors[actor]["Number of Movies Seen"] / df.shape[0]*.2)
        # actors[actor]["weight"] = (actors[actor]["Average Rating"] + actors[actor]["Difference"])* (1 + (actors[actor]["Number of Movies Seen"] / (df.shape[0]*.2)))  * (1 + actors[actor]["Billing Score"])
        # actors[actor]["weight"] = ((actors[actor]["Average Rating"]* (1 + actors[actor]["Billing Score"])) + actors[actor]["Difference"])* (2 * (actors[actor]["Number of Movies Seen"] / (df.shape[0]*.2)))  

        # Calculate the weighted average of rating and billing for each actor
        # actors[actor]['Weighted Average'] = ((actors[actor]["Average Rating"]*0.6 + (2*actors[actor]['Billing Score'])*1.2 + actors[actor]['Number of Movies Seen']*0.1) + actors[actor]["Difference"]) * 1.1
        actors[actor]['Weighted Average'] = ((actors[actor]["Average Rating"]*0.7 + (2*actors[actor]['Billing Score'])*1.3 + actors[actor]['Number of Movies Seen']*0.2) + actors[actor]["Difference"]) * 1.2
        

    # Step 3: Create a new dataframe with actors as index and their average billing position and number of movies  as values
    actor_df = pd.DataFrame.from_dict(actors, orient='index')
    actor_df.index.name = 'Actor'
    if df.shape[0] > 600:
        actor_df = actor_df[actor_df["Number of Movies Seen"] > 2]
    else:
        actor_df = actor_df[actor_df["Number of Movies Seen"] > 1]
    actor_df = actor_df.sort_values("Weighted Average", ascending=False)
    actor_df["Ranking"] = range(1, len(actor_df) + 1)
    actor_df = actor_df.drop(["Billing Positions"], axis=1)
    actor_df = actor_df[:100]
    # actor_df['Actor'] = actor_df.index
    actor_df.insert(0, 'Actor', actor_df.index)
    actor_df = actor_df.set_index("Ranking")
    df2 = actor_df.style.background_gradient(subset=['Weighted Average', 'Billing Score']).format({"Difference": "{:.2f}","Billing Score": "{:.2f}","Average Rating": "{:.2f}", 'Weighted Average': '{:.2f}'})
    # df2.index += 1 
    st.dataframe(df2, height=900, width=400)

    actor = st.text_input('Check Actor', '')
    if actor:
        unaccented_string = unidecode.unidecode(actor)
        actSplit = unaccented_string.replace(' ', '-').lower()
        actSplit = actSplit.replace('.', '').replace(',', '')
        urlTemp = "https://letterboxd.com/"+username+"/films/with/actor/" + actSplit + "/"
        st.write(urlTemp)
