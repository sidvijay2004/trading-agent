import requests
import datetime
import os
from dotenv import load_dotenv
from DB.dbConnection import X_collection
from baseAPI import BaseAPI  # ✅ Inherit from BaseAPI

# Load environment variables
load_dotenv()
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

QUERY = "(stock market OR investing OR trading OR WallStreet) -is:retweet lang:en"
URL = "https://api.twitter.com/2/tweets/search/recent"
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

PARAMS = {
    "query": QUERY,
    "max_results": 10,
    "tweet.fields": "created_at,author_id,text,public_metrics,lang",
    "expansions": "author_id",
    "user.fields": "username,verified"
}

class XAPI(BaseAPI):  # ✅ Inherit from BaseAPI
    def fetch_tweets(self):
        response = requests.get(URL, headers=HEADERS, params=PARAMS)
        
        if response.status_code == 200:
            data = response.json()
            tweets = []

            users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}

            for tweet in data.get("data", []):
                metrics = tweet["public_metrics"]
                if metrics["like_count"] < 5 and metrics["retweet_count"] < 3:
                    continue

                text = tweet["text"]
                stock = self.get_tracked_stock(text)  # ✅ Identify stock
                if not stock:
                    continue  # Skip if no tracked stock is mentioned

                author_info = users.get(tweet["author_id"], {})
                sentiment = self.analyze_sentiment(text)  # ✅ Use BaseAPI method
                expected_impact = self.calculate_expected_impact(text, sentiment)

                tweet_data = {
                    "stock": stock,  # ✅ Store stock symbol
                    "tweet_id": tweet["id"],
                    "text": text,
                    "author_id": tweet["author_id"],
                    "author_username": author_info.get("username", "Unknown"),
                    "verified": author_info.get("verified", False),
                    "like_count": metrics["like_count"],
                    "retweet_count": metrics["retweet_count"],
                    "reply_count": metrics["reply_count"],
                    "created_at": tweet["created_at"],
                    "timestamp": datetime.datetime.utcnow(),
                    "sentiment": sentiment,  # ✅ Added sentiment analysis
                    "expected_impact": expected_impact  # ✅ Added expected impact
                }
                tweets.append(tweet_data)

            if tweets:
                X_collection.insert_many(tweets)
                print(f"✅ Inserted {len(tweets)} filtered tweets into MongoDB!")

        else:
            print(f"❌ Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    x_api = XAPI()
    x_api.fetch_tweets()
