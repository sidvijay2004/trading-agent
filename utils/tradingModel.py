import logging
from APIs.alpacaAPI import get_stock_data, place_trade, check_stock_ownership
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

client = MongoClient(MONGO_URI)
db = client["tradingData"]

sentiment_collection = db["sentiment_data"]
stock_data_collection = db["stock_data"]
trade_decision_collection = db["trade_decisions"]

def get_latest_sentiment_stocks():
    """
    Fetch the latest stocks mentioned in sentiment data.
    """
    stock_mentions = {}

    collections = ["sentimentData.news_articles", "sentimentData.reddit_posts"]

    for collection_name in collections:
        collection = client["sentimentData"][collection_name.split(".")[1]]
        recent_sentiments = collection.find({}, sort=[("timestamp", -1)]).limit(5)

        for sentiment_data in recent_sentiments:
            stock = sentiment_data.get("stock")
            if stock:
                stock_mentions[stock] = {
                    "sentiment_score": sentiment_data["sentiment"]["vader_score"],
                    "expected_impact": sentiment_data["expected_impact"]
                }
    
    return stock_mentions

def evaluate_trade(symbol, sentiment_score, expected_impact):
    """
    Aggressive trade evaluation:
    - Favor action (buy/sell) over holding
    - Use sentiment, expected impact, and minimal market filters
    """
    if sentiment_score is None or expected_impact is None:
        return "hold"

    stock_data = get_stock_data(symbol)
    if not stock_data:
        logger.warning(f"❌ No stock data available for {symbol}")
        return "hold"

    spread = stock_data["spread"]
    volume = stock_data["volume"]
    owned_shares = check_stock_ownership(symbol)
    owns_stock = owned_shares is not None and owned_shares > 0

    # if spread > 5 or volume < 10000:
    #     return "hold"

    if sentiment_score > 0.6 and expected_impact > 1:
        return "buy"
    elif sentiment_score < 0.4 and expected_impact > 1 and owns_stock:
        return "sell"
    elif owns_stock:
        return "sell"
    else:
        return "buy"



def execute_trades():
    """
    Evaluate all stocks with recent sentiment and place trades accordingly.
    Also stores every stock query and trade decision in MongoDB.
    """
    stock_mentions = get_latest_sentiment_stocks()
    if not stock_mentions:
        logger.info("🚫 No stocks with relevant sentiment data.")
        return

    for symbol, data in stock_mentions.items():
        sentiment_score = data["sentiment_score"]
        expected_impact = data["expected_impact"]
        decision = evaluate_trade(symbol, sentiment_score, expected_impact)

        # ✅ Log trade decision in MongoDB (including HOLD actions)
        trade_decision_entry = {
            "stock": symbol,
            "decision": decision,
            "sentiment_score": sentiment_score,
            "expected_impact": expected_impact,
            "timestamp": datetime.utcnow()
        }
        trade_decision_collection.insert_one(trade_decision_entry)
        logger.info(f"📊 Trade Decision Stored: {trade_decision_entry}")

        if decision == "buy":
            logger.info(f"📈 Executing BUY order for {symbol}")
            trade_info = place_trade(symbol, 1, "buy")

        elif decision == "sell":
            # ✅ Check if stock is owned before selling
            owned_shares = check_stock_ownership(symbol)
            if owned_shares is None:
                logger.warning(f"⚠️ Could not determine if {symbol} is owned. Skipping sell.")
                continue
            elif owned_shares > 0:
                logger.info(f"📉 Selling {owned_shares} shares of {symbol}")
                trade_info = place_trade(symbol, owned_shares, "sell")
            else:
                logger.warning(f"⚠️ Cannot sell {symbol}, no shares owned.")
                continue

        else:
            logger.info(f"🤔 Holding {symbol}, no action taken.")
            trade_info = None  # No trade executed for hold

        # ✅ Log executed trade (only if a trade was made)
        if trade_info:
            trade_entry = {
                "stock": symbol,
                "decision": decision,
                "quantity": owned_shares if decision == "sell" else 1,
                "filled_avg_price": trade_info.get("filled_avg_price"),
                "status": trade_info["status"],
                "submitted_at": trade_info["submitted_at"],
                "timestamp": datetime.utcnow()
            }
            trade_decision_collection.insert_one(trade_entry)
            logger.info(f"✅ Trade logged: {trade_entry}")


if __name__ == "__main__":
    execute_trades()
