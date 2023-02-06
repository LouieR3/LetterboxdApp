def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from user import user
    from callLength import lenMovies
    from callGenre import genreMovies
    from callLanguage import langMovies
    from callDirector import directorMovies
    from callDecade import decadeMovies
    from callActors import actorMovies
    import unidecode
    from bs4 import BeautifulSoup
    import requests
    import json
    import re

    st.header('Recommender By Top 1001 Films')

    option = 'cloakenswagger'
    option = st.selectbox(
        'Which user do you want to look at?',
        ('cloakenswagger', 'carmal', 'prahladsingh', 'bluegrace11', 'gr8escape10', 'zacierka'))

    st.write('You selected:', option)
    file = user(option)
    lenList = lenMovies(option)
    genreList = genreMovies(option)
    genreList = pd.DataFrame(genreList)
    genreList.columns = ["genre", "average"]
    langList = langMovies(option)
    langList = pd.DataFrame(langList)
    langList.columns = ["language", "average"]
    decList = decadeMovies(option)
    decList = pd.DataFrame(decList)
    decList.columns = ["decade", "average"]
    directList = directorMovies(option)
    directList = pd.DataFrame(directList)
    directList.columns = ["director", "average"]
    actorList = actorMovies(option)
    actorList = pd.DataFrame(actorList)
    actorList.columns = ["actor", "average"]
    
    # file = user()
    df = pd.read_csv(file)

    pd.options.mode.chained_assignment = None

    df2 = pd.read_csv(file)
    df250 = pd.read_csv("Top1001Films.csv")

    cond = df250['Movie'].isin(df2['Movie'])
    df250.drop(df250[cond].index, inplace = True)
    df250 = df250.reset_index(drop=True)
    df250['length'] = (df250["MovieLength"]//10)*10
    df250['decade'] = (df250["ReleaseYear"]//10)*10
    recommendList = []
    for movie in range(len(df250)):
        lbr = float(df250["LBRating"][movie]*2)
        numberOfRatings = int(df250["NumberOfRatings"][movie])
        finRating = lbr*(1+(numberOfRatings/2000000))
        finalLen = df250["length"][movie]
        for i in lenList:
            nums = i[0].split("-")
            for y in nums:
                if str(finalLen) == y:
                    rate = float(i[1])
                    finRating = finRating * (1+(rate/10))

        gList = df250["Genre"][movie].split(",")
        cnt = 0
        tot = 0
        for g in gList:
            if len(genreList.loc[genreList['genre'] == g]) > 0:
                grow = genreList.loc[genreList['genre']
                                        == g, "average"].iat[0]
                cnt += float(grow)
                tot += 1
        if cnt > 0 and tot > 0:
            fin = cnt / tot
            finRating = finRating * (1+(fin/10))

        lang = df250["Languages"][movie].split(",")[0]
        if len(langList.loc[langList['language'] == lang]) > 0:
            lrow = float(
                langList.loc[langList['language'] == lang, "average"].iat[0])
            lrow = lrow/10
        else:
            lrow = 0.1
        finRating = finRating * (1+(lrow))
        
        release = df250["decade"][movie]
        if len(decList.loc[decList['decade'] == release]) > 0:
            drow = float(
                decList.loc[decList['decade'] == release, "average"].iat[0])
            drow = drow/10
        else:
            drow = 0.1
        finRating = finRating * (1+(drow))

        direct = df250["Director"][movie]
        if len(directList.loc[directList['director'] == direct]) > 0:
            directorRank = float(
                directList.loc[directList['director'] == direct, "average"].iat[0])
            # directorRank = directorRank/10
            # finRating = finRating * (1+(directorRank))
            finRating += directorRank
        else:
            # directorRank = 0.1
            directorRank = 1
            finRating += directorRank

        allActors = df250["Actors"][movie]
        actors = df250["Actors"][movie].split(",")
        cnt = 0
        tot = 0
        billTotal = 0
        for act in actors:
            billTotal += 1
            if len(actorList.loc[actorList['actor'] == act]) > 0:
                arow = float(actorList.loc[actorList['actor']
                                        == act, "average"].iat[0])
                tot += 1
                billScore = billTotal / 10
                billFin = arow - billScore
                cnt += billFin
        if cnt > 0 and tot > 0:
            fin = cnt / tot
            actorRank = fin
            # finRating = finRating * (1+(fin/10))
            finRating += actorRank
        else:
            actorRank = 2
            finRating += actorRank

        # if len(actorList.loc[actorList['actor'] == direct]) > 0:
        #     directorRank = float(
        #         actorList.loc[actorList['actor'] == direct, "average"].iat[0])
        #     directorRank = directorRank/10
        # else:
        #     directorRank = 0.1
        # finRating = finRating * (1+(directorRank))

        # finRating /= 5

        movieName = df250["Movie"][movie]
        lengthInHour = df250["LengthInHour"][movie]
        languageStr = df250["Languages"][movie]
        genreString = df250["Genre"][movie]
        country = df250["Country"][movie]
        numReviews = df250["NumberOfReviews"][movie]
        recommendList.append([movieName, finRating, lbr, lengthInHour,
                                languageStr, direct, release, genreString, country, numReviews, numberOfRatings, allActors])
    sortList = sorted(recommendList, key=itemgetter(1), reverse=True)
    df = pd.DataFrame(sortList)
    sortList = df.values.tolist()
    sortList = sorted(sortList, key=itemgetter(1), reverse=True)
    df2 = pd.DataFrame(sortList, columns=[
        "Movie",
        "Weighted Rating",
        "LB Rating",
        "Movie Length",
        "Languages",
        "Director",
        'Release Year',
        'Genre',
        'Country',
        'Number of Reviews',
        'Number of Ratings',
        'Actors'
    ])
    df2.index += 1

    df3 = df2.style.background_gradient(subset=['Number of Ratings'])
    # df3.index += 1 
    st.dataframe(df3, height=700, width=2000)
