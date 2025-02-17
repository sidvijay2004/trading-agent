import requests
import datetime
from DB.dbConnection import X_collection  
import os
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Define stock-related query for sentiment analysis
QUERY = "(stock market OR investing OR trading OR WallStreet) -is:retweet lang:en"

# Define the API endpoint
URL = "https://api.twitter.com/2/tweets/search/recent"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# ✅ Request more relevant tweet fields including engagement metrics
PARAMS = {
    "query": QUERY,
    "max_results": 10,  # Fetch latest 10 tweets (minimum limit for free tier)
    "tweet.fields": "created_at,author_id,text,public_metrics,lang",
    "expansions": "author_id",
    "user.fields": "username,verified"
}

def fetch_tweets():
    response = requests.get(URL, headers=HEADERS, params=PARAMS)
    
    if response.status_code == 200:
        data = response.json()
        tweets = []
        
        # Extract user data
        users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}

        for tweet in data.get("data", []):
            metrics = tweet["public_metrics"]

            # ✅ Set minimum engagement threshold to filter out low-quality tweets
            if metrics["like_count"] < 5 and metrics["retweet_count"] < 3:
                continue

            author_info = users.get(tweet["author_id"], {})
            tweet_data = {
                "tweet_id": tweet["id"],
                "text": tweet["text"],
                "author_id": tweet["author_id"],
                "author_username": author_info.get("username", "Unknown"),
                "verified": author_info.get("verified", False),
                "like_count": metrics["like_count"],
                "retweet_count": metrics["retweet_count"],
                "reply_count": metrics["reply_count"],
                "created_at": tweet["created_at"],
                "timestamp": datetime.datetime.utcnow()
            }
            tweets.append(tweet_data)

        if tweets:
            X_collection.insert_many(tweets)  # Insert into MongoDB
            print(f"✅ Inserted {len(tweets)} relevant tweets into MongoDB!")

    else:
        print(f"❌ Error: {response.status_code}, {response.text}")

fetch_tweets()
