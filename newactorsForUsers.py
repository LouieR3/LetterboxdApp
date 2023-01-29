# Import necessary modules
import pandas as pd
from collections import Counter

# Define weighting factors
actor_weight = 0.8
billing_weight = 0.2

# Create a new dataframe with the number of movies seen for each actor
movies_seen = ratings_df.groupby(['user_id', 'actors'])['movie_id'].count().reset_index(name='movies_seen')

# Split the actors column into separate rows for each actor
movies_seen = movies_seen.actors.str.split(',', expand=True) \
    .stack() \
    .reset_index(level=1, drop=True) \
    .to_frame('actors') \
    .join(movies_seen.drop('actors', 1), how='left')

# Create a new column with the weight of each actor based on number of movies seen
movies_seen['actor_weight'] = movies_seen['movies_seen'] / movies_seen.groupby('user_id')['movies_seen'].transform('sum')

# Create a new column with the billing weight of each actor
movies_seen['billing_weight'] = 1 / (movies_seen.level + 1)

# Create a new column with the combined weight of the actor and billing
movies_seen['weighted_score'] = actor_weight * movies_seen['actor_weight'] + billing_weight * movies_seen['billing_weight']

# Find the favorite actors for each user
favorite_actors = movies_seen.groupby(['user_id', 'actors'])['weighted_score'].max().reset_index()

# Print the favorite actors for user 1
print(favorite_actors.loc[favorite_actors['user_id'] == 1])