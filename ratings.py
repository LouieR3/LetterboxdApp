import pandas as pd
import time
import os
from operator import itemgetter
from user import user

start_time = time.time()


def ratings():
    # dataPath = "C:\\Users\\louie\\Desktop\\repo\\LetterboxdApp"
    # dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
    # user = "goldfishbrain"
    # user = "zacierka"
    # user = "bluegrace11"
    # user = "cloakenswagger"
    # file = "AllFilms" + user + ".csv"
    file = user()
    # fullCSV = os.path.join(dataPath, file)
    df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None

    lenDF = df.MyRating.unique()
    sortList = sorted(lenDF, reverse=True)
    dList = []
    pnt = 1
    for i in sortList:
        if pd.notna(i):
            num = df["MyRating"].value_counts(normalize=True)[i]
            numFloat = "{:.4f}".format(num)
            pct = float(numFloat)
            pnt -= pct
            numFloat2 = "{:.4f}".format(pnt)
            pnt = float(numFloat2)
            if pnt <= 0:
                pnt = 0.004
            fin = 0.5 + pnt
            if i == 4:
                fin -= 0.1
            # fin = pnt
            forOne = fin * i
            dList.append([i, fin, forOne])
    return dList

# PERCENTAGE OF EACH RATING DISTRIBUTION
# DataFrame for movies with unique rating
# lenDF = df.MyRating.unique()
# sortList = sorted(lenDF, reverse=True)
# dList = []
# pnt = 1
# # pnt = .9
# for i in sortList:
#     if pd.notna(i):
#         num = df["MyRating"].value_counts(normalize=True)[i]
#         numFloat = "{:.4f}".format(num)
#         pct = float(numFloat)
#         pnt -= pct
#         numFloat2 = "{:.4f}".format(pnt)
#         pnt = float(numFloat2)
#         if pnt <= 0:
#             pnt = 0.004
#         # fin = pnt
#         fin = 0.4 + pnt
#         if i == 4:
#             fin -= 0.1
#         if fin > 1:
#             fin = 1.2
#         if i == 4.5:
#             fin -= 0.1
#         if i == 5:
#             fin -= 0.1
#         # fin = pnt
#         forOne = fin * i
#         dList.append([i, pnt, fin, forOne])
