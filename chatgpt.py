import pandas as pd
from operator import itemgetter
# import streamlit as st
from ratings import ratings
from user import user
from callLength import lenMovies
from callGenre import genreMovies
from callLanguage import langMovies
from callDirector import directorMovies
from callDecade import decadeMovies
from callActors import actorMovies
import time

start_time = time.time()
option = "cloakenswagger"
# load the dataframe
file = user(option)

fav_length = lenMovies(option)
# fav_length.columns = ["Length", "Weighted Average"]

fav_genres = genreMovies(option)
# fav_genres.columns = ["Genres", "Weighted Average"]

fav_language = langMovies(option)
# fav_language.columns = ["Language", "Weighted Average"]
#
fav_decade = decadeMovies(option)
# fav_decade.columns = ["decade", "Weighted Average"]

fav_directors = directorMovies(option)
# fav_directors.columns = ["Director", "Weighted Average"]

fav_actors = actorMovies(option)
# fav_actors.columns = ["Actors", "Weighted Average"]

df250 = pd.read_csv("Top1001Films.csv")
df = pd.read_csv(file)
cond = df250['Movie'].isin(df['Movie'])
df250.drop(df250[cond].index, inplace = True)
df250 = df250.reset_index(drop=True)
df250['LBRating'] = (df250["LBRating"]*3)
# df250['Length'] = (df250["MovieLength"]//10)*10
# df250['decade'] = (df250["ReleaseYear"]//10)*10
# print(round(len(df)*.1))
total_num_ratings = df250["NumberOfRatings"].max()
genre_weight = 0.4
actor_weight = 0.4
director_weight = 1.5
length_weight = 0.8
language_weight = 0.3
decade_weight = 1
popularity_weight = 0.4
rating_weight = 0.4

def calculate_score(movies_df, fav_directors, fav_actors, fav_genres, fav_length, fav_decade, fav_language):
    scores = []
    scoreList = []
    for i in range(len(movies_df)):
        movie = movies_df.iloc[i]
        score = 0
        
        # calculate the director score
        director = movie['Director']
        if director in fav_directors.index:
            directorScore = fav_directors.loc[director, 'Weighted Average']*director_weight
            score += directorScore
        else:
            directorScore = 6
            # directorScore = fav_directors["Weighted Average"].min()
            score += directorScore
        
        # calculate the actors score
        actors = movie['Actors'].split(',')[:10]
        actorsScore = 0
        actors_count = 0
        i = 0
        for actor in actors:
            if actor in fav_actors.index:
                actorsScore += fav_actors.loc[actor, 'Weighted Average'] - i
                actors_count += 1
            i += 1
        if actors_count > 0:
            # print(movie['Movie'])
            # score += ((actorsScore / actors_count) * 1.5)
            # score += actorsScore / actors_count
            score += (actorsScore*actor_weight)
            # print(actorsScore)
            # print()
        else:
            actorsScore = 10
            score += actorsScore
        
        # calculate the genre score
        genres = movie['Genre'].split(',')
        genres_score = 0
        genres_count = 0
        for genre in genres:
            if genre in fav_genres.index:
                genres_score += fav_genres.loc[genre, 'Weighted Average']
                genres_count += 1
        if genres_count > 0:
            genreScore = (genres_score / genres_count)*genre_weight
            score += genreScore
        
        # calculate the length score
        length = movie['MovieLength']
        length_bucket = length // 10 * 10
        if length_bucket in fav_length.index:
            lengthScore = (fav_length.loc[length_bucket, 'Weighted Average']*length_weight)
            score += lengthScore
        else:
            lengthScore = fav_length["Weighted Average"].min()
            score += lengthScore
        
        # calculate the decade score
        decade = movie['ReleaseYear'] // 10 * 10
        # decade = movie['decade']
        if decade in fav_decade.index:
            decadeScore = (fav_decade.loc[decade, 'Weighted Average']*decade_weight)
            score += decadeScore
        
        # calculate the language score
        language = movie['Languages'].split(',')[0]
        if language in fav_language.index:
            languageScore = (fav_language.loc[language, 'Weighted Average']*language_weight)
            score += languageScore
        else:
            languageScore = fav_language["Weighted Average"].min()
            score += languageScore

        # LBscore = float(movie['LBRating'])
        # score += LBscore

        popularityScore = float(movie['LBRating'])*(1+(movie['NumberOfRatings']/total_num_ratings))
        score += popularityScore

        scores.append(score)
        scoreList.append([directorScore, actorsScore, genreScore, lengthScore, decadeScore, languageScore, popularityScore])
    # movies_df['Score'] = scores
    movies_df['scoreList'] = scoreList
    movies_df.insert(1, 'Score', scores)
    return movies_df

# use the calculate_score function on your movie dataframe
movies_df = calculate_score(df250, fav_directors, fav_actors, fav_genres, fav_length, fav_decade, fav_language)
movies_df= movies_df.sort_values(by=['Score'], ascending=False)
movies_df= movies_df.reset_index(drop=True)
movies_df.index = movies_df.index + 1
movies_df = movies_df.drop(["MovieLength", "NumberOfReviews"], axis=1)
print(movies_df)

print("--- %s seconds ---" % (time.time() - start_time))