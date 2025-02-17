# redditAPI.py
import praw
from DB.dbConnection import reddit_collection
import datetime
import os
import itertools  # ✅ Added for chaining generators
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

# Define subreddits related to stock trading
SUBREDDITS = ["stocks", "wallstreetbets", "investing", "securityanalysis"]

# Define engagement thresholds
MIN_UPVOTES = 50  
MAX_POSTS_PER_SUB = 3  
MAX_TOTAL_POSTS = 12  

def fetch_reddit_posts():
    posts = []
    total_collected = 0  

    for subreddit_name in SUBREDDITS:
        subreddit = reddit.subreddit(subreddit_name)

        for post in itertools.chain(
            subreddit.hot(limit=MAX_POSTS_PER_SUB // 2), 
            subreddit.rising(limit=MAX_POSTS_PER_SUB - (MAX_POSTS_PER_SUB // 2)) 
        ):
            if total_collected >= MAX_TOTAL_POSTS:
                break  

            if post.score < MIN_UPVOTES:
                continue  

            post.comments.replace_more(limit=0) 
            top_comments = [comment.body for comment in post.comments.list()[:5]]  

            reddit_data = {
                "title": post.title,
                "author": str(post.author),
                "upvotes": post.score,
                "num_comments": post.num_comments,
                "url": post.url,
                "selftext": post.selftext[:500] if post.is_self else None, 
                "flair": post.link_flair_text if post.link_flair_text else None,
                "top_comments": top_comments,
                "timestamp": datetime.datetime.utcnow()
            }
            posts.append(reddit_data)
            total_collected += 1  

        if total_collected >= MAX_TOTAL_POSTS:
            break  
        
    # Store posts in MongoDB
    if posts:
        reddit_collection.insert_many(posts)
        print(f"✅ Inserted {len(posts)} relevant posts into MongoDB!")


fetch_reddit_posts()
