def directorMovies():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    # import streamlit as st
    from user import user

    dList = ratings()
    file = user()
    df = pd.read_csv(file)

    # CHECKING FAVORITE Director AND RATING BY Director
    filmAverage = df["MyRating"].mean()
    for i in range(len(df)):
        director = df["Director"].iloc[i]
        df.at[i, "Director"] = director
        rate = df["MyRating"].iloc[i]
    # DataFrame for movies with unique Director
    finalDF = df.Director.unique()
    # print("=========")
    finList = []
    dList = ratings()
    for mem in finalDF:
        # print(mem)
        cnt = 0
        finWeight = 0
        tot = 0
        # DataFrame for movies of just the current iteration Director
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
            avg1 = xdf["MyRating"].mean()
            avg = avg1
            avg += (float(diff)/2)
            avg = avg * (1 + (tot/50))
            # HIGHEST NUMBER IN LIST * 10 / 2
            finAvg = "{:.2f}".format(avg)

            if avg > filmAverage:
                finList.append(
                    [mem, finAvg])
    return finList