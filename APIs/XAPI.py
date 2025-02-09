import requests
import datetime
from DB.dbConnection import X_collection 
import os
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Define the search query
QUERY = "stock market"

# Define the API endpoint
URL = "https://api.twitter.com/2/tweets/search/recent"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

PARAMS = {
    "query": QUERY,
    "max_results": 10,  # Fetch latest 10 tweets (min is 10)
    "tweet.fields": "created_at,author_id,text"
}

def fetch_tweets():
    response = requests.get(URL, headers=HEADERS, params=PARAMS)
    
    if response.status_code == 200:
        data = response.json()
        tweets = []

        for tweet in data.get("data", []):
            tweet_data = {
                "tweet_id": tweet["id"],
                "text": tweet["text"],
                "author_id": tweet["author_id"],
                "created_at": tweet["created_at"],
                "timestamp": datetime.datetime.utcnow()
            }
            tweets.append(tweet_data)

        if tweets:
            X_collection.insert_many(tweets)  # Insert into MongoDB
            print(f"Inserted {len(tweets)} tweets into MongoDB!")

    else:
        print(f"Error: {response.status_code}, {response.text}")

fetch_tweets()
