def langMovies():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    # import streamlit as st
    from user import user

    dList = ratings()
    file = user()
    df = pd.read_csv(file)

    lenDF = df[~df["Languages"].str.contains("No spoken language")]
    for i in range(len(df)):
        language = df["Languages"].iloc[i].split(",")[0]
        lenDF.at[i, "Languages"] = language
        rate = df["MyRating"].iloc[i]
    # DataFrame for movies with unique language
    finalDF = lenDF.Languages.unique()
    finList = []
    for mem in finalDF:
        cnt = 0
        finWeight = 0
        tot = 0
        # DataFrame for movies of just the current iteration language
        # Weighted average is too high for bad movies like 2.0 Uncle Boonme
        xdf = lenDF.loc[lenDF["Languages"] == mem]
        diff = xdf["Difference"].mean()
        diff = "{:.2f}".format(diff)
        for rate in dList:
            rateLen = len(xdf[(xdf["MyRating"] == rate[0])])
            finWeight = (rateLen*rate[0]) * rate[1]
            cnt += finWeight
            tot += rateLen
        if tot > 0:
            fin = cnt / tot
            fin += (float(diff)/2)
            fin = fin * (1 + (tot/1000))
            fin = max(fin, 0.5)

            avg1 = xdf["MyRating"].mean()
            avg = avg1
            avg += (float(diff)/2)
            avg = avg * (1 + (tot/4700))
            # HIGHEST NUMBER IN LIST * 10 / 2
            finAvg = "{:.2f}".format(avg)
            finList.append([mem, finAvg])
    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    df['index'] = range(1, len(df) + 1)

    sortList = df.values.tolist()
    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    return sortList
