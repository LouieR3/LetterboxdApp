# Import necessary modules
import pandas as pd
from collections import Counter
from user import user
import time

start_time = time.time()

# load the dataframe
file = user()
df = pd.read_csv(file)
df = df[df["Actors"].notna()]
print(len(df))
df = df[df["Genre"].str.contains("Documentary") == False]

df['MyRating'] = (df["MyRating"]*2)
df['user_id'] = 1
df.insert(0, 'movie_id', range(1, len(df) + 1))

# Define weighting factors
actor_weight = 0.8
billing_weight = 0.2

# --------------------------------------------------
# # Create a new column that calculates the average rating for each actor
# df['avg_rating'] = df.groupby('Actors')['MyRating'].mean()

# # Create a new column that calculates the position of the actor in the Actors column
# df['actor_position'] = df.groupby('Actors').cumcount()+1

# # Create a new column that combines the avg_rating and actor_position to create a score
# df['actor_score'] = df['avg_rating'] + (1/df['actor_position'])

# # Find the actor with the highest score
# favorite_actor = df.loc[df['actor_score'].idxmax()]['Actors']

# print("The user's favorite actor is:", favorite_actor)
# --------------------------------------------------

# Create a new dataframe with the number of movies seen for each actor
movies_seen = df.groupby(['user_id', 'Actors'])['movie_id'].count().reset_index(name='movies_seen')

# Split the actors column into separate rows for each actor
movies_seen = movies_seen.Actors.str.split(',', n=15, expand=True) \
    .stack() \
    .reset_index(level=1, drop=True) \
    .to_frame('Actors') \
    .join(movies_seen.drop('Actors', 1), how='left')

# Create a new column with the weight of each actor based on number of movies seen
movies_seen['actor_weight'] = movies_seen['movies_seen'] / movies_seen.groupby('user_id')['movies_seen'].transform('sum')

# Create a new column with the billing weight of each actor
movies_seen['billing_weight'] = 1 / (movies_seen.groupby(['user_id', 'Actors']).cumcount() + 1)

# Create a new column with the combined weight of the actor and billing
movies_seen['weighted_score'] = actor_weight * movies_seen['actor_weight'] + billing_weight * movies_seen['billing_weight']

# Find the favorite actors for each user
favorite_actors = movies_seen.groupby(['user_id', 'Actors'])['weighted_score'].max().reset_index()

# Print the favorite actors for user 1
print(favorite_actors)
print(movies_seen.sort_values(by='movies_seen', ascending=False))