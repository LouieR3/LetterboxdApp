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
# actors_list = df[actorList].stack().unique()

# Split the actors column into a list of actors
df['Actors'] = df['Actors'].str.split(',', n=key)

# Create a new dataframe with the split actors
df_split = df.explode('Actors')

# Add a column for the number of movies seen by the actor
df_split['Movies_Seen'] = df_split.groupby('Actors')['Actors'].transform('count')
df_split= df_split.loc[df_split['Movies_Seen'] > 1]

# Add a column for the billing position of the actor
df_split['Billing_Position'] = df_split.groupby('Actors').cumcount() + 1

# Calculate the weight based on the number of movies seen and billing position
df_split['Weight'] = df_split['Movies_Seen'] / df_split['Billing_Position']

# Calculate the weighted rating for each actor
df_split['Weighted_Rating'] = df_split['MyRating'] * df_split['Weight']
df_split.dropna(subset=['Weighted_Rating'], inplace=True)

print(df_split)
print()
# Group the data by actor and calculate the average weighted rating
df_grouped = df_split.groupby(['Actors', 'Movies_Seen'])['Weighted_Rating'].mean().reset_index()

# Sort the data by the average weighted rating
df_grouped = df_grouped.sort_values('Weighted_Rating', ascending=False).reset_index()

# Get the top actor
favorite_actor = df_grouped.iloc[0]['Actors']
print(df_grouped)