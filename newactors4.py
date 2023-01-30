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
print(len(df))
df['MyRating'] = (df["MyRating"]*2)

key = 15
actorList = []
for i in range(key):
    num = i+1
    actStr = "actor_" + str(num)
    actorList.append(str)

# Create a new column called 'Actors_List' which splits the 'Actors' column by ','
# df['Actors_List'] = df['Actors'].str.split(',', n=key)
# # print(df)
# # Create a new column called 'Billing_Score' that calculates the billing score for each actor
# df['Billing_Score'] = df['Actors_List'].apply(lambda actors: [1 - (actors.index(actor) / len(actors)) if actor in actors else 0 for actor in actors])
# print(df)
# print(df['Actors_List'][0])
# # actor_df = df["Tom Cruise" in df["Actors_List"] == True]
# actor_df = df[df['Actors'].str.contains("Tom Cruise")]

# Step 1: Create a dictionary with actors as keys and a list of their billing positions in each movie as values.
actors = {}
for i in range(len(df)):
    subActor = df["Actors"].iloc[i].split(",", 10)
    rating = df["MyRating"].iloc[i]
    difference = df["Difference"].iloc[i]
    for j, actor in enumerate(subActor):
        if actor not in actors:
            actors[actor] = {"Billing Positions": [], "movies_seen": 0, "rating": [], "weight": 0, "difference": []}
        actors[actor]["Billing Positions"].append(j+1)
        actors[actor]["movies_seen"] += 1
        actors[actor]["rating"].append(rating)
        actors[actor]["difference"].append(difference)

# Step 2: For each actor, calculate the average of their billing positions
for actor in actors:
    # actors[actor]["billing_avg"] = sum(actors[actor]["Billing Positions"]) / len(actors[actor]["Billing Positions"])
    actors[actor]["billing_avg"] = len(actors[actor]["Billing Positions"]) / sum(actors[actor]["Billing Positions"])
    actors[actor]["rating"] = sum(actors[actor]["rating"]) / len(actors[actor]["rating"])
    actors[actor]["difference"] = sum(actors[actor]["difference"]) / len(actors[actor]["difference"])
    # actors[actor]["weight"] = (actors[actor]["rating"] + 1/actors[actor]["billing_avg"]) / 2 * (actors[actor]["movies_seen"] / df.shape[0])
    # avg = (avg + float(difference))* (1 + (len(actor_df) / (df.shape[0]*.2)))  * (1 + billing_score)
    actors[actor]["weight"] = (actors[actor]["rating"] + actors[actor]["difference"])* (1 + (actors[actor]["movies_seen"] / (df.shape[0]*.2)))  * (1 + actors[actor]["billing_avg"])

# Step 3: Create a new dataframe with actors as index and their average billing position and number of movies  as values
actor_df = pd.DataFrame.from_dict(actors, orient='index')
actor_df.index.name = 'Actor'
if df.shape[0] > 600:
    actor_df = actor_df[actor_df["movies_seen"] > 2]
else:
    actor_df = actor_df[actor_df["movies_seen"] > 1]
# actor_df = actor_df[actor_df["billing_avg"] >= .1]
actor_df = actor_df.sort_values("weight", ascending=False)
print("==================================")
# print(df)
print(actor_df.head(50))
# print(actor_df.sort_values(['billing_avg'], ascending=False))
print("==================================")
# sub_df = 
# Create a new dataframe where we groupby 'Actors' and sum the Billing_Score
# df_grouped = df.groupby(['Actors']).sum()
# print(df_grouped)


# Create a new dataframe where we groupby 'Actors' and count the number of movies
# df_count = df.groupby(['Actors']).count()

# Create a new column called 'Average_Billing_Score' that calculates the average billing score by dividing the Billing_Score by number of movies
# df_grouped['Average_Billing_Score'] = df_grouped['Billing_Score'] / df_count['Movie']
# print(df_grouped)
# Filter the dataframe to only include actors who have appeared in more than 1 movie
# df_grouped = df_grouped[df_count['Movie'] > 1]

# Print the dataframe with the average billing score for each actor
# print(df_grouped)

print("--- %s seconds ---" % (time.time() - start_time))
