def app():
    import pandas as pd
    from operator import itemgetter
    from ratings import ratings
    import streamlit as st
    from user import user

    st.header('Your Favorite Movies by Length in Minutes')
    st.caption('Here are ...')

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
        lim = str(start) + "-" + str(end) + " minutes"
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
            finFloat = "{:.2f}".format(fin)
            avg1 = data["MyRating"].mean()
            avg2 = "{:.2f}".format(avg1)
            avg = avg1
            avg += (float(diff)/2)
            avg = avg * (1 + (tot/1000))
            # HIGHEST NUMBER IN LIST * 10 / 2
            finAvg = "{:.2f}".format(avg)
            finList.append([lim, finFloat, avg2, finAvg, tot, diff])
        start += 10
        end += 10
    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    df['index'] = range(1, len(df) + 1)
    sortList = df.values.tolist()
    sortList = sorted(sortList, key=itemgetter(3), reverse=True)
    df2 = pd.DataFrame(sortList, columns=[
        "Length",
        "Weighted",
        "Average",
        "Final Weighted",
        "# of Movies Watched",
        "Difference",
        'Ranking'
    ])

    df2 = df2.style.background_gradient(subset=['Ranking'])
    st.dataframe(df2, height=700, width=2000)
