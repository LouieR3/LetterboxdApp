import pandas as pd
from user import user
import numpy as np
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


# Step 1: Create a dictionary with actors as keys and a list of their billing positions in each movie as values.
actors = {}
for i in range(len(df)):
    subActor = df["Actors"].iloc[i].split(",")
    for j, actor in enumerate(subActor):
        if actor not in actors:
            actors[actor] = []
        actors[actor].append(j+1)

# Step 2: For each actor, calculate the average of their billing positions
for actor in actors:
    actors[actor] = sum(actors[actor]) / len(actors[actor])

# Step 3: Create a new dataframe with actors as index and their average billing position as values
billing_df = pd.DataFrame.from_dict(actors, orient='index', columns=['Average Billing'])
billing_df.index.name = 'Actor'

# Step 4: Merge the actors dataframe with the movies dataframe on the actors column
merged_df = pd.merge(df, billing_df, left_on='Actors', right_index=True, how='left')

# Step 5: Calculate the total number of movies seen for each actor by counting the number of non-null values in the "Actor" column
merged_df['Actor'].notnull().groupby(merged_df['Actor']).sum()

# Step 6: Calculate the weighted rating score for each actor
# The weight is calculated as the product of the actor's average rating and the number of movies seen
merged_df['Weighted Rating'] = merged_df['Rating'] * merged_df['Actor'].notnull().groupby(merged_df['Actor']).sum()

# Step 7: Normalize the weighted rating score for each actor by dividing by the total number of movies seen for that actor
merged_df['Normalized Weighted Rating'] = merged_df['Weighted Rating'] / merged_df['Actor'].notnull().groupby(merged_df['Actor']).sum()

# Step 8: Calculate the final score for each actor by taking the product of the Normalized Weighted Rating and 1 / Average Billing
merged_df['Final Score'] = merged_df['Normalized Weighted Rating'] * (1 / merged_df['Average Billing'])

print(merged_df)