from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
import pandas as pd
import time
import os
from operator import itemgetter
from tabulate import tabulate

start_time = time.time()

dataPath = "C:\\Users\\louie\\Desktop\\repo\\LetterboxdApp"
# dataPath = "C:\\Users\\louie.rodriguez\\OneDrive - PENNONI\\Documents\\git\\DeltekMapScirpts\\LBCode"
# user = "goldfishbrain"
# user = "zacierka"
# user = "bluegrace11"
# user = "gr8escape10"
user = "cloakenswagger"
file = "AllFilms" + user + ".csv"
fullCSV = os.path.join(dataPath, file)
df = pd.read_csv(fullCSV)

pd.options.mode.chained_assignment = None

filmAverage = df["MyRating"].mean()
# DataFrame for movies within our length with a rating
df = df[df["Actors"].notna()]
print(len(df))
df = df[df["Genre"].str.contains("Documentary") == False]
df['MyRating'] = (df["MyRating"]*2)
print(len(df))
actorsList = []
# For each movie in DataFrame
for i in range(len(df)):
    # actors is a list of every actor in the current film
    actors = df["Actors"].iloc[i].split(",")
    # for each actor in this film
    for actor in actors:
        check_if_in_list = False
        # if the list isn't empty
        if len(actorsList) > 0:
            # for each list in the list
            for i in range(len(actorsList)):
                # check if actor is in that list already and if true set the checker to true
                isAlreadyInList = actor in actorsList[i]
                if isAlreadyInList == True:
                    check_if_in_list = True
        # If actor hasn't been checked yet and actor has a first and last name
        if check_if_in_list != True and (" " in actor):
            totalMoviesSeen = 0
            avg = 0
            # including the comma helps us not find actors whos names are short enough that they could be contained in another actors name
            mid = actor + ","
            # get all movies that the current actor is in
            actor_df = df[df["Actors"].str.contains(mid, na=False)]
            # only calculate a score for actors in more than one movie
            if len(actor_df) > 1:
                # calculate billing score as average billing across movies the actor is in
                billingTotal = 0
                for i in range(len(actor_df)):
                    subActor = actor_df["Actors"].iloc[i].split(",")
                    count = 1
                    for actor2 in subActor:
                        if actor == actor2:
                            billingTotal += count
                            break
                        count += 1
                try:
                    # billing_score = (len(actor_df) / billingTotal)*2
                    billing_score = len(actor_df) / billingTotal
                except:
                    billing_score = 0
                # If the actor's billing score is below 0.1, denoting them as mainly a smaller actor, exclude them
                if billing_score < 0.1:
                    break
                
                # Get the average difference between all movies the actor is in, to see how the user favors this actor compared to the site as a whole
                difference = actor_df["Difference"].mean()
                difference = "{:.2f}".format(difference)
                if len(actor_df) > 0:
                    LB_avgStr = actor_df["MyRating"].mean()

                    LB_avg = "{:.2f}".format(LB_avgStr)
                    avg = LB_avgStr
                    # avg += float(difference)
                    # avg *= (1 + (len(actor_df) / (df.shape[0]*.2))) * (1 + billing_score)
                    avg = (avg + float(difference))* (1 + (len(actor_df) / (df.shape[0]*.2)))  * (1 + billing_score)
                    # HIGHEST NUMBER IN LIST * 10 / 2
                    # avg = 1 + billing_score
                    WeightedAvgFlt = avg / 1.75
                    WeightedAvg = "{:.2f}".format(WeightedAvgFlt)
                    actorsList.append(
                            [actor, LB_avg, WeightedAvg, avg, len(actor_df), difference, billing_score]
                        )
                    # if WeightedAvgFlt > 2.8:
                    #     actorsList.append(
                    #         [actor, LB_avg, WeightedAvg, avg, len(actor_df), difference, billing_score]
                    #     )
                    # if finFloat > filmAverage:
                    #     actorsList.append(
                    #         [actor, finFloatStr, LB_avg, WeightedAvg, totalMoviesSeen, difference, billing_score])

sortList = sorted(actorsList, key=itemgetter(3), reverse=True)
sortList = sortList[:100]
df = pd.DataFrame(sortList)
df["index"] = range(1, len(df) + 1)
sortList = df.values.tolist()
sortList = sorted(sortList, key=itemgetter(3), reverse=True)
print(
    tabulate(
        sortList,
        headers=[
            "Actor",
            "Average",
            "Weigthed 2",
            "Without Divide",
            "Total",
            "Difference",
            "Billing Score",
            "Index",
        ],
    )
)
print(len(sortList))
# THIS OPTION?
# https://letterboxd.com/cloakenswagger/films/ratings/with/actor/saoirse-ronan/by/entry-rating/

# NEED TO ACCOUNT FOR % OF FILMS WATCHED OF ACTOR

print("--- %s seconds ---" % (time.time() - start_time))
