def actorMovies(option):
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    # file = user(option)
    file = st.session_state.my_global_variable
    # file = user()
    username = file.split(".cs")[0].split("AllFilms")[1]
    # df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None

    # load the dataframe
    # file = user()
    df = pd.read_csv(file)
    df = df[df["Actors"].notna()]
    # print(len(df))
    df = df[df["Genre"].str.contains("Documentary") == False]
    # print(len(df))
    df = df[df["Actors"].str.contains(",") == True]
    # print(len(df))
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
        # actors[actor]['Weighted Average'] = ((actors[actor]["Average Rating"]*0.7 + (2*actors[actor]['Billing Score'])*1.3 + actors[actor]['Number of Movies Seen']*0.2) + actors[actor]["Difference"]) * 1.2
        # actors[actor]['Weighted Average'] = ((actors[actor]["Average Rating"] + (2*actors[actor]['Billing Score'])*1.5 + actors[actor]['Number of Movies Seen']*0.2) + actors[actor]["Difference"]) * 1.2
        actors[actor]['Weighted Average'] = ((actors[actor]["Average Rating"] + (2*actors[actor]['Billing Score'])+ actors[actor]['Number of Movies Seen']*0.2) + actors[actor]["Difference"])
        

    # Step 3: Create a new dataframe with actors as index and their average billing position and number of movies  as values
    actor_df = pd.DataFrame.from_dict(actors, orient='index')
    actor_df.index.name = 'Actor'
    if df.shape[0] > 600:
        actor_df = actor_df[actor_df["Number of Movies Seen"] > 2]
    else:
        actor_df = actor_df[actor_df["Number of Movies Seen"] > 1]
    actor_df = actor_df.sort_values("Weighted Average", ascending=False)
    # actor_df["Ranking"] = range(1, len(actor_df) + 1)
    actor_df = actor_df.drop(["Billing Positions", "Number of Movies Seen", "Average Rating", "Difference", "Billing Score"], axis=1)


    actor_df = actor_df[:(round(len(df)*.2))]
    # actor_df["Ranking"] = range(1, len(actor_df) + 1)
    # actor_df.insert(0, 'Actor', actor_df.index)
    # actor_df = actor_df.set_index("Ranking")
    return actor_df