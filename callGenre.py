def genreMovies():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    file = user()
    df = pd.read_csv(file)

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

                        avg1 = sub_df["MyRating"].mean()
                        avg = avg1
                        avg += (float(diff)/2)
                        avg = avg * (1 + (tot/2500))
                        finAvg = "{:.2f}".format(avg)

                        finList.append([a, finAvg])

    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    df.columns = ["genre", "average"]
    return df
    # sortList = df.values.tolist()
    # sortList = sorted(sortList, key=itemgetter(3), reverse=True)
