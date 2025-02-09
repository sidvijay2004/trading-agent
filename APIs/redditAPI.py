# redditAPI.py
import praw
from DB.dbConnection import reddit_collection
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Reddit API credentials
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Initialize the Reddit API client
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

# Function to fetch Reddit posts and store them in MongoDB
def fetch_reddit_posts():
    subreddit = reddit.subreddit("stocks")
    posts = []

    for post in subreddit.hot(limit=5):
        reddit_data = {
            "title": post.title,
            "author": str(post.author),
            "upvotes": post.score,
            "url": post.url,
            "timestamp": datetime.datetime.utcnow()
        }
        posts.append(reddit_data)

    if posts:
        reddit_collection.insert_many(posts)  # Insert into MongoDB
        print(f"Inserted {len(posts)} posts into MongoDB!")


fetch_reddit_posts()
