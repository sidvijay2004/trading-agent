# DB/dbConnection.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Access Databases
sentiment_db = client["sentimentData"]
trading_db = client["tradingData"]

# Collections in sentimentData
reddit_collection = sentiment_db["reddit_posts"]
news_collection = sentiment_db["news_articles"]
X_collection = sentiment_db["X_posts"]

# Collections in tradingData
trades_collection = trading_db["executed_trades"]
stock_data_collection = trading_db["stock_data"]
account_data_collection = trading_db["account_info"]
portfolio_collection = trading_db["portfolio"]

def get_collection(db_name, collection_name):
    """Fetch a collection dynamically based on the database name."""
    if db_name == "sentimentData":
        return sentiment_db[collection_name]
    elif db_name == "tradingData":
        return trading_db[collection_name]
    else:
        raise ValueError("Invalid database name!")
