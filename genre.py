def app():
    import pandas as pd
    import os
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st

    st.header('Genre Ranked')
    st.caption('Here are your favorite genres ranked by the average rating of the movies you have watched, accounting for the number of their films you have seen, and the difference in the average rating you have for the director compared to Letterboxd')

    dataPath = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\LetterboxdApp"
    # dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
    # user = "goldfishbrain"
    # user = "zacierka"
    # user = "bluegrace11"
    user = "cloakenswagger"
    file = "AllFilms" + user + ".csv"
    fullCSV = os.path.join(dataPath, file)
    df = pd.read_csv(fullCSV)

    lenDF = df[df["Genre"].notna()]
    finList = []
    dList = ratings()
    # For each index in our final DataFrame
    for i in range(len(lenDF)):
        # actor is a list of every actor in the current film
        genre = lenDF["Genre"].iloc[i].split(",")
        # for each actor in this film
        for a in genre:
            x = False
            if len(finList) > 0:
                for i in range(len(finList)):
                    y = a in finList[i]
                    if y == True:
                        x = True
            if x == True:
                break
            else:
                tot = 0
                avg = 0
                mid = a
                sub_df = lenDF[lenDF['Genre'].str.contains(mid, na=False)]
                if len(sub_df) > 3:
                    diff = sub_df["Difference"].mean()
                    diff = "{:.2f}".format(diff)
                    cnt = 0
                    finWeight = 0
                    tot = 0
                    for rate in dList:
                        rateLen = len(sub_df[(sub_df["MyRating"] == rate[0])])
                        finWeight = (rateLen*rate[0]) * rate[1]
                        cnt += finWeight
                        tot += rateLen
                    if tot > 0:
                        fin = cnt / tot
                        fin += (float(diff)/2)
                        fin = fin * (1 + (tot/1000))
                        finFloat = "{:.2f}".format(fin)

                        avg1 = sub_df["MyRating"].mean()
                        avg2 = "{:.2f}".format(avg1)
                        avg = avg1
                        avg += (float(diff)/2)
                        avg = avg * (1 + (tot/2500))
                        finAvg = "{:.2f}".format(avg)

                        finList.append([a, finFloat, avg2, finAvg, tot, diff])

    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    df['index'] = range(1, len(df) + 1)
    sortList = df.values.tolist()
    sortList = sorted(sortList, key=itemgetter(3), reverse=True)
    df2 = pd.DataFrame(sortList, columns=[
        "Genre",
        "Weighted",
        "Average",
        "Normal Weighted",
        "# of Movies Watched",
        "Difference",
        'Ranking'
    ])

    df2 = df2.style.background_gradient(subset=['Ranking'])
    st.dataframe(df2, height=700)
