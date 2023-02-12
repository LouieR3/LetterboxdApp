import praw
import pandas as pd
import requests

# Connect to Reddit API using PRAW
reddit = praw.Reddit(client_id='your_client_id',
                     client_secret='your_client_secret',
                     user_agent='your_user_agent')

# Get NBA schedule using the NBA schedule API
url = 'https://www.balldontlie.io/#get-all-games'
schedule = requests.get(url).json()

# Create a dictionary to store the comment counts for each game thread
comment_counts = {}

# Iterate through the schedule and get the comment counts for each game thread
for game in schedule:
    home_team = game['home_team']['full_name']
    away_team = game['away_team']['full_name']
    date = game['date']
    subreddit = reddit.subreddit('nba')
    # title = f'[Post Game Thread] {away_team} @ {home_team}'
    title = f'[Post Game Thread]'
    submission = subreddit.search(title, sort='new', limit=1).next()
    print(submission)
    comment_counts[title] = submission.num_comments

# Create a pandas DataFrame from the comment counts dictionary
df = pd.DataFrame.from_dict(comment_counts, orient='index', columns=['Comment Count'])

# Perform statistical analysis on the data to calculate the disparity for the amount of comments when a team wins than when they lose
# code for statistical analysis 

# Visualize the data using matplotlib or other visualization library
# code for visualization