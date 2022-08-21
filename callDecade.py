def decadeMovies():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    # import streamlit as st
    from user import user

    dList = ratings()
    file = user()
    df = pd.read_csv(file)

    finalDF = df.ReleaseYear.unique()
    decadeList = []
    for mem in finalDF:
        y = str(mem)
        x = y[:3]
        if x not in decadeList:
            decadeList.append(x)
    finList = []

    for mem in decadeList:
        df['ReleaseYear'] = df['ReleaseYear'].astype("string")
        cnt = 0
        finWeight = 0
        tot = 0
        # DataFrame for movies of just the current iteration genre
        xdf = df.loc[df["ReleaseYear"].str.startswith(mem, na=False)]
        diff = xdf["Difference"].mean()
        diff = "{:.2f}".format(diff)
        for rate in dList:
            rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
            finWeight = (rateLen*rate[0]) * rate[1]
            cnt += finWeight
            tot += rateLen
        if tot > 0:
            fin = cnt / tot
            fin = fin * (1 + (tot/1000))
            fin += (float(diff)/2)
            s = mem + "0"
            s = int(s)
            avg1 = xdf["MyRating"].mean()
            avg = avg1
            avg += (float(diff)/2)
            avg = avg * (1 + (tot/1700))
            # HIGHEST NUMBER IN LIST * 10 / 2
            finAvg = "{:.2f}".format(avg)

            finList.append([s, finAvg])

    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    return sortList
