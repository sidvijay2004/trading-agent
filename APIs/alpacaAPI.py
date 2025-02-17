import asyncio
import logging
import os
import json
import websockets
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Alpaca API credentials
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")

# ✅ Correct WebSocket URL for News Stream
NEWS_WEBSOCKET_URL = "wss://stream.data.alpaca.markets/v1beta1/news"

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

client = MongoClient(MONGO_URI)
db = client["sentimentData"]
news_collection = db["news_articles"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect():
    """Connects to the Alpaca WebSocket and listens for news data."""
    async with websockets.connect(NEWS_WEBSOCKET_URL) as ws:
        logger.info("✅ Connected to Alpaca News WebSocket.")

        # ✅ Authenticate
        auth_msg = json.dumps({
            "action": "auth",
            "key": API_KEY,
            "secret": API_SECRET
        })
        await ws.send(auth_msg)
        response = await ws.recv()
        logger.info(f"✅ Authentication Response: {response}")

        # ✅ Subscribe to the news stream
        subscribe_msg = json.dumps({
            "action": "subscribe",
            "news": ["*"]
        })
        await ws.send(subscribe_msg)
        response = await ws.recv()
        logger.info(f"✅ Subscription Response: {response}")

        # ✅ Continuously listen for incoming messages
        while True:
            message = await ws.recv()
            process_news(message)


def process_news(message):
    """Handles incoming news data."""
    try:
        news = json.loads(message)
        logger.info(f"🔔 News Received: {news}")

        # Insert into MongoDB if not duplicate
        for article in news:
            if article.get("T") == "n":  # Ensures message is a news article
                news_data = {
                    "id": article["id"],
                    "headline": article["headline"],
                    "summary": article.get("summary", ""),
                    "author": article.get("author", ""),
                    "created_at": article.get("created_at", ""),
                    "updated_at": article.get("updated_at", ""),
                    "url": article.get("url", ""),
                    "symbols": article.get("symbols", []),
                    "source": article.get("source", ""),
                    "content": article.get("content", "")
                }

                # Insert only if not already in database
                if not news_collection.find_one({"id": article["id"]}):
                    news_collection.insert_one(news_data)
                    logger.info(f"✅ Inserted news: {news_data['headline']}")
                else:
                    logger.info(f"⚠️ Duplicate news skipped: {news_data['headline']}")

    except Exception as e:
        logger.error(f"⚠️ Error processing news: {e}")


# Run the WebSocket connection
if __name__ == "__main__":
    asyncio.run(connect())
