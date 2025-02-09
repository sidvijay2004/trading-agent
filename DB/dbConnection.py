import os
from pymongo import MongoClient
from dotenv import load_dotenv 


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

client = MongoClient(MONGO_URI)

db = client["sentimentData"]

reddit_collection = db["reddit_posts"]
news_collection = db["news_articles"]
X_collection = db["X_posts"]


def get_collection(collection_name):
    return db[collection_name]
