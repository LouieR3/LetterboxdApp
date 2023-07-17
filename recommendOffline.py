import pandas as pd

def genreMovies(option):
    file = "AllFilms" + option + ".csv"
    df = pd.read_csv(file)
    df = df[df["Genre"].notna()]
    df['MyRating'] = (df["MyRating"]*2)
    split_df = df["Genre"].str.split(",").apply(pd.Series)
    if 3 in split_df.columns:
        split_df = split_df.drop([3], axis=1)
    if 4 in split_df.columns:
        split_df = split_df.drop([4], axis=1)
    if 5 in split_df.columns:
        split_df = split_df.drop([5], axis=1)
    if 6 in split_df.columns:
        split_df = split_df.drop([6], axis=1)
    if 7 in split_df.columns:
        split_df = split_df.drop([7], axis=1)
    if 8 in split_df.columns:
        split_df = split_df.drop([8], axis=1)
    df = df.join(split_df)
    df = df.drop(['LBRating',  'ReviewDate', 'MovieLength', 'LengthInHour', 'Languages', 'Director', 'ReleaseYear', 'Country', 'NumberOfReviews', 'NumberOfRatings', 'Actors'], axis=1)
    df.columns = ["Movie", "MyRating", "Difference", "Genre", "genre_1", "genre_2", "genre_3"]
    genres_list = df[["genre_1", "genre_2", "genre_3"]].stack().unique()
    checkList = []
    for genre in genres_list:
        mask = df["Genre"].str.contains(genre)
        avg_rating = df.loc[mask, "MyRating"].mean()
        difference = df.loc[mask, "Difference"].mean()
        total_movies = df.loc[mask, "MyRating"].count()
        checkList.append([genre, avg_rating, total_movies, difference])
    genre_ratings = pd.DataFrame(checkList, columns =['Genre', 'Average Rating', 'Total', 'Difference']).set_index('Genre')
    weight = 0.98
    genre_ratings['Weighted Average'] = (genre_ratings['Average Rating']*weight) + (genre_ratings['Total']*(1-weight)) + genre_ratings['Difference']
    genre_ratings= genre_ratings.sort_values(by=['Weighted Average'], ascending=False)
    genre_ratings = genre_ratings.drop(["Average Rating", "Total", "Difference"], axis=1)
    return genre_ratings
def lenMovies(option):
    file = "AllFilms" + option + ".csv"
    df = pd.read_csv(file)
    df['MyRating'] = (df["MyRating"]*2)
    df['length'] = (df["MovieLength"]//10)*10
    user_length_group = df.groupby(["length"])
    length_sum_ratings = user_length_group["MyRating"].sum()
    length_total_movies = user_length_group["Movie"].count()
    length_avg_ratings = length_sum_ratings / length_total_movies
    difference = user_length_group["Difference"].mean()
    length_ratings = pd.DataFrame({"Average Rating": length_avg_ratings, "Total Movies": length_total_movies, "Difference": difference})
    weight = 0.95
    length_ratings['Weighted Average'] = length_ratings['Average Rating']*weight + length_ratings['Total Movies']*(1-weight) + length_ratings['Difference']
    length_ratings = length_ratings.drop(["Average Rating", "Total Movies", "Difference"], axis=1)
    length_ratings= length_ratings.sort_values(by=['Weighted Average'], ascending=False)
    return length_ratings
def langMovies(option):
    file = "AllFilms" + option + ".csv"
    df = pd.read_csv(file)
    df['MyRating'] = (df["MyRating"]*2)
    df = df[df["Languages"].notna()]
    df['language'] = df['Languages'].str.split(',').str[0]
    user_language_group = df.groupby(["language"])
    user_total_movies = len(df)
    language_sum_ratings = user_language_group["MyRating"].sum()
    language_total_movies = user_language_group["Movie"].count()
    language_avg_ratings = language_sum_ratings / language_total_movies
    difference = user_language_group["Difference"].mean()
    language_ratings = pd.DataFrame({"Average Rating": language_avg_ratings, "Total Movies": language_total_movies, "Difference": difference})
    weight = 0.95
    language_ratings['Weighted Average'] = language_ratings['Average Rating']*weight + language_ratings['Total Movies']*(1-weight) + language_ratings['Difference']
    language_ratings= language_ratings.sort_values(by=['Weighted Average'], ascending=False)
    language_ratings = language_ratings.drop(["Average Rating", "Total Movies", "Difference"], axis=1)
    return language_ratings
def decadeMovies(option):
    file = "AllFilms" + option + ".csv"
    df = pd.read_csv(file)
    df['decade'] = (df["ReleaseYear"]//10)*10
    df['MyRating'] = (df["MyRating"]*2)
    user_decade_group = df.groupby(["decade"])
    decade_sum_ratings = user_decade_group["MyRating"].sum()
    decade_total_movies = user_decade_group["Movie"].count()
    difference = user_decade_group["Difference"].mean()
    decade_avg_ratings = decade_sum_ratings / decade_total_movies
    decade_ratings = pd.DataFrame({"Average Rating": decade_avg_ratings, "Total Movies": decade_total_movies, "Difference": difference})
    weight = 0.99
    decade_ratings['Weighted Average'] = decade_ratings['Average Rating']*weight + decade_ratings['Total Movies']*(1-weight) + decade_ratings['Difference']
    decade_ratings= decade_ratings.sort_values(by=['Weighted Average'], ascending=False)
    decade_ratings = decade_ratings.drop(["Total Movies", "Average Rating", "Difference"], axis=1)
    return decade_ratings
def directorMovies(option):
    file = "AllFilms" + option + ".csv"
    df = pd.read_csv(file)
    df = df[df["Genre"].str.contains("Documentary") == False]
    df['MyRating'] = (df["MyRating"]*2)
    user_director_group = df.groupby(["Director"])
    director_sum_ratings = user_director_group["MyRating"].sum()
    director_total_movies = user_director_group["Movie"].count()
    director_difference = user_director_group["Difference"].mean()
    director_avg_ratings = director_sum_ratings / director_total_movies
    director_ratings = pd.DataFrame({"Average Rating": director_avg_ratings, "Total Movies": director_total_movies, "Difference": director_difference})
    director_ratings['Weighted Average'] = (director_ratings['Average Rating']*0.9 + ((director_ratings['Total Movies'] + director_ratings['Difference'])*0.2))*2
    director_ratings= director_ratings.sort_values(by=['Weighted Average'], ascending=False)
    director_ratings = director_ratings.drop(["Total Movies", "Average Rating", "Difference"], axis=1)
    director_ratings["Ranking"] = range(1, len(director_ratings) + 1)
    director_ratings['Weighted Average'] = director_ratings['Weighted Average'] - director_ratings["Ranking"]/10
    director_ratings = director_ratings.drop(["Ranking"], axis=1)
    director_ratings = director_ratings[:(round(len(df)*.15))]
    return director_ratings
def actorMovies(option):
    file = "AllFilms" + option + ".csv"
    username = file.split(".cs")[0].split("AllFilms")[1]
    df = pd.read_csv(file)
    df = df[df["Actors"].notna()]
    df = df[df["Genre"].str.contains("Documentary") == False]
    df = df[df["Actors"].str.contains(",") == True]
    df['MyRating'] = (df["MyRating"]*2)
    key = 15
    actorList = []
    for i in range(key):
        num = i+1
        actStr = "actor_" + str(num)
        actorList.append(str)
    actors = {}
    for i in range(len(df)):
        subActor = df["Actors"].iloc[i].split(",", 10)
        rating = df["MyRating"].iloc[i]
        difference = df["Difference"].iloc[i]
        for j, actor in enumerate(subActor):
            if actor not in actors:
                actors[actor] = {"Billing Positions": [], "Number of Movies Seen": 0, "Average Rating": [], "Difference": []}
            actors[actor]["Billing Positions"].append(j+1)
            actors[actor]["Number of Movies Seen"] += 1
            actors[actor]["Average Rating"].append(rating)
            actors[actor]["Difference"].append(difference)
    for actor in actors:
        actors[actor]["Billing Score"] = len(actors[actor]["Billing Positions"]) / sum(actors[actor]["Billing Positions"])
        actors[actor]["Average Rating"] = sum(actors[actor]["Average Rating"]) / len(actors[actor]["Average Rating"])
        actors[actor]["Difference"] = sum(actors[actor]["Difference"]) / len(actors[actor]["Difference"])
        actors[actor]['Weighted Average'] = ((actors[actor]["Average Rating"] + (2*actors[actor]['Billing Score'])+ actors[actor]['Number of Movies Seen']*0.2) + actors[actor]["Difference"])
    actor_df = pd.DataFrame.from_dict(actors, orient='index')
    actor_df.index.name = 'Actor'
    if df.shape[0] > 600:
        actor_df = actor_df[actor_df["Number of Movies Seen"] > 2]
    else:
        actor_df = actor_df[actor_df["Number of Movies Seen"] > 1]
    actor_df = actor_df.sort_values("Weighted Average", ascending=False)
    actor_df = actor_df.drop(["Billing Positions", "Number of Movies Seen", "Average Rating", "Difference", "Billing Score"], axis=1)
    actor_df = actor_df[:(round(len(df)*.2))]
    return actor_df

option = "cloakenswagger"
# file = user(option)
# file = option
file = "AllFilms" + option + ".csv"
fav_length = lenMovies(option)
fav_genres = genreMovies(option)
fav_language = langMovies(option)
fav_decade = decadeMovies(option)
fav_directors = directorMovies(option)
fav_actors = actorMovies(option)
# df250 = pd.read_csv("Top1001Films.csv")
df250 = pd.read_csv("TopFilms2.csv")
df250 = df250[df250['Genre'].notnull()]
df250 = df250[df250['Actors'].notnull()]
df = pd.read_csv(file)
# cond = df250['Movie'].isin(df['Movie'])
# df250.drop(df250[cond].index, inplace = True)
# df250 = df250.reset_index(drop=True)

# df250['LBRating'] = (df250["LBRating"]*3)
df250['LBRatingNew'] = (df250["LBRating"]*3)
# df250['Length'] = (df250["MovieLength"]//10)*10
# df250['LBRating'] = str(round(df250["LBRating"], 2))
# df250['decade'] = (df250["ReleaseYear"]//10)*10

total_num_ratings = df250["NumberOfRatings"].max()
genre_weight = 0.4
actor_weight = 0.4
director_weight = 1.1
length_weight = 0.8
language_weight = 0.3
decade_weight = 1
popularity_weight = 0.4
rating_weight = 1.5




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
            score += (directorScore*director_weight)
        else:
            directorScore = 10
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
        if actorsScore > 10:
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
        else:
            genreScore = fav_genres["Weighted Average"].min()
            score += genreScore

        # calculate the length score
        length = movie['MovieLength']
        length_bucket = length // 10 * 10
        if length_bucket in fav_length.index:
            lengthScore = (fav_length.loc[length_bucket, 'Weighted Average']*length_weight)
            score += lengthScore
        else:
            lengthScore = 0
            score += lengthScore
        
        # calculate the decade score
        decade = movie['ReleaseYear'] // 10 * 10
        # decade = movie['decade']
        if decade in fav_decade.index:
            decadeScore = (fav_decade.loc[decade, 'Weighted Average']*decade_weight)
            score += decadeScore
        else:
            decadeScore = fav_decade["Weighted Average"].min()
            score += decadeScore

        # calculate the language score
        language = movie['Languages'].split(',')[0]
        if language in fav_language.index:
            languageScore = (fav_language.loc[language, 'Weighted Average']*language_weight)
            score += languageScore
        else:
            languageScore = 0
            score += languageScore

        # LBscore = float(movie['LBRating'])
        # score += LBscore

        popularityScore = (float(movie['LBRatingNew'])*rating_weight)*(1+(movie['NumberOfRatings']/total_num_ratings))
        score += popularityScore
        # score = str(round(score, 2))
        scores.append(score)
        # scoreList.append([directorScore, actorsScore, genreScore, lengthScore, decadeScore, languageScore, popularityScore])
        scoreList.append([round(directorScore, 2), round(actorsScore, 2), round(genreScore, 2), round(lengthScore, 2), round(decadeScore, 2), round(languageScore, 2), round(popularityScore, 2)])
    # movies_df['Score'] = scores
    movies_df['scoreList'] = scoreList
    movies_df.insert(1, 'Score', scores)
    movies_df['Score'] = movies_df['Score'].round(2)
    movies_df['LBRating'] = movies_df['LBRating'].round(2)
    
    return movies_df

# use the calculate_score function on your movie dataframe
movies_df = calculate_score(df250, fav_directors, fav_actors, fav_genres, fav_length, fav_decade, fav_language)
movies_df= movies_df.sort_values(by=['Score'], ascending=False)
movies_df= movies_df.reset_index(drop=True)
movies_df.index = movies_df.index + 1
movies_df = movies_df.drop(["MovieLength", 'Country', "NumberOfReviews", "LBRatingNew"], axis=1)
movies_df["Genre"] = movies_df["Genre"].str.split(",")
movies_df["Languages"] = movies_df["Languages"].str.split(",")
movies_df["Actors"] = movies_df["Actors"].str.split(",")
# movies_df['Score Rating'] = ((movies_df['Score'] / 10).apply(lambda x: min(round(x), 10)) / 2)
movies_df.insert(2, 'Rating Prediction', ((movies_df['Score'] / 10).apply(lambda x: min(round(x), 10)) / 2))
# print(movies_df)
print(movies_df.columns)
print()
# print(df)
print(df.columns)
movies_df.insert(3, 'MyRating', "")
def get_my_rating(row):
    try:
        my_rating = df.loc[(df['Movie'] == row['Movie']) & (df['ReleaseYear'] == row['ReleaseYear']), 'MyRating'].values[0]
        return '{:.1f}'.format(my_rating) if not pd.isnull(my_rating) else 'N/A'
    except IndexError:
        return 'N/A'

movies_df['MyRating'] = movies_df.apply(get_my_rating, axis=1)
print(movies_df)