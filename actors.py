def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from ratings import ratings
    from user import user
    import unidecode

    # --------------
    # FIX JR AND OTHER WEIRD NAMES
    # --------------

    st.header('Actors Ranked')
    st.caption('Here are your favorite actors ranked by the average rating of the movies you have watched of theirs, accounting for the number of their films you have seen, the difference in the average rating you have for the actor compared to Letterboxd, and the actors billing score. Billing score, being the number of movies you have seen of that actor over the totalality of all that actors placings in the movies billing lists')

    file = user()
    username = file.split(".cs")[0].split("AllFilms")[1]
    df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None

    ratingList = ratings()

    # limit on lowest amount of movies seen by actor to include
    numActors = 2
    if len(df) < 800:
        numActors = 1

    # DataFrame for movies within our length with a rating
    movieDF = df[df["Actors"].notna()]
    print(len(movieDF))
    # Don't include Documentaries
    movieDF = movieDF[movieDF["Genre"].str.contains("Documentary") == False]
    print(len(movieDF))
    finList = []
    # For each index in our final DataFrame
    for i in range(len(movieDF)):
        # actor is a list of every actor in the current film
        actors = movieDF["Actors"].iloc[i].split(",")
        # for each actor in this film
        for a in actors:
            inList = False
            # if the final list of actors isn't empty
            if len(finList) > 0:
                # for each actor in the list
                for i in range(len(finList)):
                    # check if actor is in the list already and if true set the checker to true
                    y = a in finList[i]
                    if y == True:
                        inList = True
            # if we have not included this actor yet and it is not a one word name actor (messes up the algo)
            if inList == False and (" " in a):
                tot = 0
                avg = 0
                # we need to only look for names with a comma next to them or it will mess up the algo
                checkActor = a + ","
                # all movies where this actor appears in the movie
                actorsDF = movieDF[movieDF["Actors"].str.contains(
                    checkActor, na=False)]
                # only continue if they have been in more than 2 movies
                if len(actorsDF) > numActors:
                    totalCount = 0
                    # go through each movie
                    for i in range(len(actorsDF)):
                        # get all the actors in each movie to find the billing of the actor for each movie
                        subActor = actorsDF["Actors"].iloc[i].split(",")
                        count = 1
                        # go through all actors for each movie
                        for actor in subActor:
                            # if the current actor is the one we are looking at
                            if a == actor:
                                # tally up billing
                                totalCount += count
                                break
                            count += 1
                    # get the billing score and if it is super low get rid of the person and don't include
                    try:
                        billScore = len(actorsDF) / totalCount
                    except:
                        billScore = 0
                    if billScore < 0.1:
                        break
                    # get the avg difference between user and letterboxd for actor
                    diff = actorsDF["Difference"].mean()
                    diff = "{:.2f}".format(diff)

                    # all of this computes the old weight I used to use
                    cnt = 0
                    finWeight = 0
                    tot = 0
                    for rate in ratingList:
                        rateLen = len(
                            actorsDF[(actorsDF["MyRating"] == rate[0])])
                        finWeight = (rateLen * rate[0]) * rate[1]
                        cnt += finWeight
                        tot += rateLen
                    if tot > 0:
                        # Bad Weighted
                        fin = cnt / tot
                        fin += float(diff) / 2
                        fin = max(fin, 0.5)
                        fin = fin * (1 + (tot / 100))
                        # finFloat += billScore
                        fin *= 1 + billScore
                        finFloat = fin / 1.75
                        finFloatStr = "{:.2f}".format(finFloat)

                        # Final Weighted
                        avg1 = actorsDF["MyRating"].mean()
                        avg2 = "{:.2f}".format(avg1)
                        avg = avg1
                        # plus difference
                        avg += float(diff)
                        # add in total
                        avg = avg * (1 + (tot / 50))
                        # HIGHEST NUMBER IN LIST * 10 / 2
                        # multiply by billing score
                        avg *= 1 + billScore
                        # it just seems dividing by 1.75 brings it to a good number
                        finAv1 = avg / 1.75
                        finAvg = "{:.2f}".format(finAv1)

                        # how many actors you include in the end depends on number of movies user has watched all together
                        if len(df) > 800:
                            if finAv1 > 3:
                                finList.append(
                                    [a, finFloatStr, avg2, finAvg, avg,
                                        tot, diff, billScore]
                                )
                        else:
                            if finAv1 > 1.5:
                                finList.append(
                                    [a, finFloatStr, avg2, finAvg, avg,
                                        tot, diff, billScore]
                                )
                        # if finFloat > filmAverage:
                        #     finList.append(
                        #         [a, finFloatStr, avg2, finAvg, tot, diff, billScore])
    sortList = sorted(finList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    df["Ranking"] = range(1, len(df) + 1)
    sortList = df.values.tolist()
    sortList = sorted(sortList, key=itemgetter(3), reverse=True)
    df = pd.DataFrame(sortList, columns=[
        "Actor",
        "Weighted",
        "Average",
        "Final Weighted",
        "Without Divide",
        "# of Movies Watched",
        "Difference",
        "Billing Score",
        "Ranking",
    ])
    df2 = df.style.background_gradient(subset=['Ranking', 'Billing Score'])
    # df2.index += 1 
    st.dataframe(df2, height=900, width=2000)

    actor = st.text_input('Check Actor', '')
    if actor:
        unaccented_string = unidecode.unidecode(actor)
        actSplit = unaccented_string.replace(' ', '-').lower()
        actSplit = actSplit.replace('.', '').replace(',', '')
        urlTemp = "https://letterboxd.com/"+username+"/films/with/actor/" + actSplit + "/"
        st.write(urlTemp)
