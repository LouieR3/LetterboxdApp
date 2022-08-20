def len():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    file = user()
    df = pd.read_csv(file)

    start = 60
    end = 70
    limit = 500
    finList = []
    dList = ratings()
    while start <= limit:
        cnt = 0
        finWeight = 0
        tot = 0
        lim = str(start) + "-" + str(end)
        data = df[(df['MovieLength'] >= start) & (df['MovieLength'] < end)]
        diff = data["Difference"].mean()
        diff = "{:.2f}".format(diff)
        for rate in dList:
            rateLen = len(data[(data["MyRating"] == rate[0])])
            finWeight = (rateLen*rate[0]) * rate[1]
            cnt += finWeight
            tot += rateLen
        if tot > 0:
            fin = cnt / tot
            fin = fin * (1 + (tot/1000))
            fin += (float(diff)/2)
            fin = max(fin, 0.5)
            avg1 = data["MyRating"].mean()
            avg = avg1
            avg += (float(diff)/2)
            avg = avg * (1 + (tot/1000))
            # HIGHEST NUMBER IN LIST * 10 / 2
            finAvg = "{:.2f}".format(avg)
            finList.append([lim, finAvg])
        start += 10
        end += 10
    # sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(finList)
    # print(finList)
    return finList
