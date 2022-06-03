def app():
    import pandas as pd
    import os
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st

    st.header('Directors Ranked')
    st.caption('Here are your favorite directors ranked by the average rating of the movies you have watched of theirs, accounting for the number of their films you have seen, and the difference in the average rating you have for the director compared to Letterboxd')

    # dataPath = "C:\\Users\\louie\\OneDrive\\Desktop\\repo\\LetterboxdApp"
    # dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
    # user = "goldfishbrain"
    # user = "zacierka"
    # user = "bluegrace11"
    user = "cloakenswagger"
    file = "AllFilms" + user + ".csv"
    # file = "AllFilmsMike.csv"
    # fullCSV = os.path.join(dataPath, file)
    df = pd.read_csv(file)

    # CHECKING FAVORITE GENRE AND RATING BY GENRE\
    filmAverage = df["MyRating"].mean()
    for i in range(len(df)):
        director = df["Director"].iloc[i]
        df.at[i, "Director"] = director
        rate = df["MyRating"].iloc[i]
    # DataFrame for movies with unique genre
    finalDF = df.Director.unique()
    # print("=========")
    finList = []
    dList = ratings()
    for mem in finalDF:
        # print(mem)
        cnt = 0
        finWeight = 0
        tot = 0
        # DataFrame for movies of just the current iteration genre
        xdf = df.loc[df["Director"] == mem]
        diff = xdf["Difference"].mean()
        diff = "{:.2f}".format(diff)
        for rate in dList:
            rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
            finWeight = (rateLen*rate[0]) * rate[1]
            cnt += finWeight
            tot += rateLen
        if tot > 1:
            fin = cnt / tot
            fin += (float(diff)/2)
            fin = fin * (1 + (tot/100))
            # ^ THIS SHOULD BE TOTAL WATCHED / TOTAL FILMS THEY HAVE THAT ARE DECENTLY WATCHED AND ACCOUNT FOR BAD RATINGS
            # higher total should mean difference is more legit and factored in more
            finFloat = "{:.2f}".format(fin)

            avg1 = xdf["MyRating"].mean()
            avg2 = "{:.2f}".format(avg1)
            avg = avg1
            avg += (float(diff)/2)
            avg = avg * (1 + (tot/100))
            # HIGHEST NUMBER IN LIST * 10 / 2
            finAvg = "{:.2f}".format(avg)

            if avg > filmAverage:
                finList.append(
                    [mem, finFloat, avg2, finAvg, tot, diff])

    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    df['Ranking'] = range(1, len(df) + 1)
    sortList = df.values.tolist()
    sortList = sorted(sortList, key=itemgetter(3), reverse=True)
    df2 = pd.DataFrame(sortList, columns=[
        "Director",
        "Weighted",
        "Average",
        "Final Weighted",
        "# of Movies Watched",
        "Difference",
        'Ranking'
    ])

    df2 = df2.style.background_gradient(subset=['Ranking'])
    st.dataframe(df2, height=700, width=2000)
