def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from ratings import ratings
    from user import user
    import webbrowser
    import unidecode

    st.header('Actors Ranked')
    st.caption('Here are your favorite actors ranked by the average rating of the movies you have watched of theirs, accounting for the number of their films you have seen, the difference in the average rating you have for the actor compared to Letterboxd, and the actors billing score. Billing score, being the number of movies you have seen of that actor over the totalality of all that actors placings in the movies billing lists')

    file = user()
    df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None

    dList = ratings()

    numActors = 2
    if len(df) < 800:
        numActors = 1

    filmAverage = df["MyRating"].mean()
    # DataFrame for movies within our length with a rating
    lenDF = df[df["Actors"].notna()]
    print(len(lenDF))
    lenDF = lenDF[lenDF["Genre"].str.contains("Documentary") == False]
    print(len(lenDF))
    finList = []
    # For each index in our final DataFrame
    for i in range(len(lenDF)):
        # actor is a list of every actor in the current film
        actors = lenDF["Actors"].iloc[i].split(",")
        # for each actor in this film
        for a in actors:
            inList = False
            # if the list isn't empty
            if len(finList) > 0:
                # for each list in the list
                for i in range(len(finList)):
                    # check if actor is in that list already and if true set the checker to true
                    y = a in finList[i]
                    if y == True:
                        inList = True
            if inList != True and (" " in a):
                tot = 0
                avg = 0
                mid = a + ","
                sub_df = lenDF[lenDF["Actors"].str.contains(mid, na=False)]
                if len(sub_df) > numActors:
                    totalCount = 0
                    for i in range(len(sub_df)):
                        subActor = sub_df["Actors"].iloc[i].split(",")
                        count = 1
                        for actor in subActor:
                            if a == actor:
                                totalCount += count
                                break
                            count += 1
                    try:
                        # finMult = (len(sub_df) / totalCount)*2
                        finMult = len(sub_df) / totalCount
                    except:
                        finMult = 0
                    if finMult < 0.1:
                        break
                    diff = sub_df["Difference"].mean()
                    diff = "{:.2f}".format(diff)
                    cnt = 0
                    finWeight = 0
                    tot = 0
                    for rate in dList:
                        rateLen = len(sub_df[(sub_df["MyRating"] == rate[0])])
                        finWeight = (rateLen * rate[0]) * rate[1]
                        cnt += finWeight
                        tot += rateLen
                    if tot > 0:
                        fin = cnt / tot
                        fin += float(diff) / 2
                        fin = max(fin, 0.5)
                        fin = fin * (1 + (tot / 100))
                        # finFloat += finMult
                        fin *= 1 + finMult
                        finFloat = fin / 1.75
                        finFloatStr = "{:.2f}".format(finFloat)

                        avg1 = sub_df["MyRating"].mean()
                        avg2 = "{:.2f}".format(avg1)
                        avg = avg1
                        avg += float(diff)
                        avg = avg * (1 + (tot / 100))
                        # HIGHEST NUMBER IN LIST * 10 / 2
                        avg *= 1 + finMult
                        finAv1 = avg / 1.75
                        finAvg = "{:.2f}".format(finAv1)

                        if len(df) > 800:
                            if finAv1 > 2.8:
                                finList.append(
                                    [a, finFloatStr, avg2, finAvg,
                                        tot, diff, finMult]
                                )
                        else:
                            if finAv1 > 1.25:
                                finList.append(
                                    [a, finFloatStr, avg2, finAvg,
                                        tot, diff, finMult]
                                )
                        # if finFloat > filmAverage:
                        #     finList.append(
                        #         [a, finFloatStr, avg2, finAvg, tot, diff, finMult])
    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    df["Ranking"] = range(1, len(df) + 1)
    sortList = df.values.tolist()
    sortList = sorted(sortList, key=itemgetter(3), reverse=True)
    df = pd.DataFrame(sortList, columns=[
        "Actor",
        "Weighted",
        "Average",
        "Final Weighted",
        "# of Movies Watched",
        "Difference",
        "Billing Score",
        "Ranking",
    ])
    df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])
    st.dataframe(df2, height=900, width=2000)

    actor = st.text_input('Check Actor', '')
    if actor:
        unaccented_string = unidecode.unidecode(actor)
        actSplit = unaccented_string.replace(' ', '-').lower()
        urlTemp = "https://letterboxd.com/cloakenswagger/films/with/actor/" + actSplit + "/"
        webbrowser.open_new_tab(urlTemp)
        st.write(urlTemp)
