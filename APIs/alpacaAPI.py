import requests
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# Alpaca API credentials (Paper Trading)
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = os.getenv("ALPACA_TRADE_ENDPOINT")

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

client = MongoClient(MONGO_URI)
db = client["tradingData"]
trades_collection = db["executed_trades"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def place_trade(symbol, qty, side, order_type="market", time_in_force="gtc"):
    """
    Places a trade on Alpaca Paper Trading account and logs it in MongoDB.
    """

    url = f"{BASE_URL}/orders"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
        "Content-Type": "application/json"
    }
    order_data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": order_type,
        "time_in_force": time_in_force
    }

    try:
        response = requests.post(url, json=order_data, headers=headers)
        response.raise_for_status()
        trade_info = response.json()
        
        logger.info(f"✅ Trade Successful: {trade_info}")

        # Store trade info in MongoDB
        trade_record = {
            "symbol": trade_info["symbol"],
            "qty": trade_info["qty"],
            "side": trade_info["side"],
            "order_type": trade_info["type"],
            "time_in_force": trade_info["time_in_force"],
            "filled_avg_price": trade_info.get("filled_avg_price", None),
            "status": trade_info["status"],
            "submitted_at": trade_info["submitted_at"],
            "created_at": datetime.utcnow()
        }
        trades_collection.insert_one(trade_record)
        logger.info(f"✅ Trade recorded in MongoDB: {trade_record}")

        return trade_info
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Trade Failed: {e}")
        return None

if __name__ == "__main__":
    # Example: Buy 1 share of AAPL and record it
    place_trade(symbol="AAPL", qty=1, side="buy")
