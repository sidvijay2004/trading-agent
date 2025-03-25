import praw
from DB.dbConnection import reddit_collection
import datetime
import os
import itertools
from dotenv import load_dotenv
from baseAPI import BaseAPI

# Load environment variables
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

SUBREDDITS = ["stocks", "wallstreetbets", "investing", "securityanalysis"]

class RedditAPI(BaseAPI):
    def fetch_reddit_posts(self):
        posts = []
        for subreddit_name in SUBREDDITS:
            subreddit = reddit.subreddit(subreddit_name)

            for post in itertools.chain(subreddit.hot(limit=3), subreddit.rising(limit=3)):
                if post.score < 50:
                    continue  

                text = f"{post.title} {post.selftext}"
                stock = self.get_tracked_stock(text)
                if not stock:
                    continue  # Skip if no tracked stock is mentioned

                post.comments.replace_more(limit=0)
                top_comments = [comment.body for comment in post.comments.list()[:5]]

                sentiment = self.analyze_sentiment(text)
                expected_impact = self.calculate_expected_impact(text, sentiment)

                reddit_data = {
                    "stock": stock,
                    "title": post.title,
                    "author": str(post.author),
                    "upvotes": post.score,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "selftext": post.selftext[:500] if post.is_self else None,
                    "flair": post.link_flair_text if post.link_flair_text else None,
                    "top_comments": top_comments,
                    "timestamp": datetime.datetime.utcnow(),
                    "sentiment": sentiment,
                    "expected_impact": expected_impact
                }
                posts.append(reddit_data)

        if posts:
            reddit_collection.insert_many(posts)
            print(f"✅ Inserted {len(posts)} filtered Reddit posts into MongoDB!")

if __name__ == "__main__":
    reddit_api = RedditAPI()
    reddit_api.fetch_reddit_posts()
