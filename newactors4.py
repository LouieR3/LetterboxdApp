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
df['Actors_List'] = df['Actors'].str.split(',', n=key)
print(df)
# Create a new column called 'Billing_Score' that calculates the billing score for each actor
df['Billing_Score'] = df['Actors_List'].apply(lambda actors: [1 - (actors.index(actor) / len(actors)) if actor in actors else 0 for actor in actors])
print(df)
# Create a new dataframe where we groupby 'Actors' and sum the Billing_Score
df_grouped = df.groupby(['Actors']).sum()
print(df_grouped)


# Create a new dataframe where we groupby 'Actors' and count the number of movies
df_count = df.groupby(['Actors']).count()

# Create a new column called 'Average_Billing_Score' that calculates the average billing score by dividing the Billing_Score by number of movies
df_grouped['Average_Billing_Score'] = df_grouped['Billing_Score'] / df_count['Movie']
print(df_grouped)
# Filter the dataframe to only include actors who have appeared in more than 1 movie
df_grouped = df_grouped[df_count['Movie'] > 1]

# Print the dataframe with the average billing score for each actor
print(df_grouped)