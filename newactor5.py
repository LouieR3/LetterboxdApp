from collections import defaultdict
import pandas as pd
from user import user
import time

start_time = time.time()

# load the dataframe
file = user()
df = pd.read_csv(file)
df = df[df["Actors"].notna()]
print(len(df))
df = df[df["Genre"].str.contains("Documentary") == False]
print(len(df))
df = df[df["Actors"].str.contains(",") == True]

actors = {}
for i in range(len(df)):
    subActor = df["Actors"].iloc[i].split(",")
    for j, actor in enumerate(subActor):
        if actor not in actors:
            actors[actor] = []
        actors[actor].append(j+1)
# print(actors)
# Step 2: For each actor, calculate the average of their billing positions
for actor in actors:
    actors[actor] = len(actors[actor]) / sum(actors[actor])

# Step 3: Create a new dataframe with actors as index and their average billing position as values
actors_df = pd.DataFrame.from_dict(actors, orient='index', columns=['Average Billing'])
actors_df.index.name = 'Actor'

def calculate_favorite_actor(user_movies, actors_df):
    # Step 1: Extract the actors from the 'Actors' column of each movie that the user has watched
    user_actors = []
    for index, row in user_movies.iterrows():
        actors = row["Actors"].split(",")
        user_actors.extend(actors)
        
    # Step 2: Create a dictionary to store the number of movies watched for each actor
    # and their total weighted billing average
    actor_dict = defaultdict(lambda: [0, 0])
    print(actor_dict)
    # Step 3: Increment the count for each actor in the dictionary
    for actor in user_actors:
        actor_dict[actor][0] += 1
        
    # Step 4: Calculate the weighted billing average for each actor
    for actor in actor_dict:
        billing_total = 0
        for i in range(len(user_movies)):
            subActor = user_movies["Actors"].iloc[i].split(",")
            count = 1
            for actor2 in subActor:
                if actor == actor2:
                    billing_total += count
                    break
                count += 1
        try:
            billing_score = len(user_movies) / billing_total
            actor_dict[actor][1] = billing_score / actor_dict[actor][0]
        except ZeroDivisionError:
            actor_dict[actor][1] = 0
            
    # Step 5: Store the actor with the highest weighted billing average as the user's favorite actor
    favorite_actor = min(actor_dict, key=lambda x: actor_dict[x][1])
    
    return favorite_actor

print(calculate_favorite_actor(df, actors_df))