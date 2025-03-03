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
BASE_TRADE_URL = "https://paper-api.alpaca.markets/v2"
BASE_MARKET_URL = "https://data.alpaca.markets/v2" 

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

client = MongoClient(MONGO_URI)
db = client["tradingData"]
trades_collection = db["executed_trades"]
stock_data_collection = db["stock_data"]
account_data_collection = db["account_info"]
portfolio_collection = db["portfolio"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_account_info():
    """
    Retrieves account details including buying power and cash balance.
    """
    url = f"{BASE_TRADE_URL}/account"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        account_info = response.json()

        # Store in MongoDB
        account_data = {
            "cash": account_info["cash"],
            "buying_power": account_info["buying_power"],
            "portfolio_value": account_info["equity"],
            "timestamp": datetime.utcnow()
        }
        account_data_collection.insert_one(account_data)
        logger.info(f"✅ Account Info Stored: {account_data}")

        return account_info
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch account info: {e}")
        return None

def get_portfolio_positions():
    """
    Retrieves current holdings in the portfolio.
    """
    url = f"{BASE_TRADE_URL}/positions"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        positions = response.json()

        portfolio_data = []
        for position in positions:
            position_info = {
                "symbol": position["symbol"],
                "qty": position["qty"],
                "market_value": position["market_value"],
                "unrealized_pl": position["unrealized_pl"],
                "cost_basis": position["cost_basis"],
                "timestamp": datetime.utcnow()
            }
            portfolio_data.append(position_info)

        # Store in MongoDB
        if portfolio_data:
            portfolio_collection.insert_many(portfolio_data)
            logger.info(f"✅ Portfolio Positions Stored: {portfolio_data}")
        else:
            logger.info("📉 No open positions.")

        return positions
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch portfolio positions: {e}")
        return None

def get_stock_data(symbol):
    """
    Retrieves the latest stock market data for a given symbol from Alpaca.
    Returns additional useful trading metrics like volume and bid-ask spread.
    """
    url = f"{BASE_MARKET_URL}/stocks/{symbol}/quotes/latest"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extract stock price data and alternative trading metrics
        bid_price = data["quote"]["bp"]
        ask_price = data["quote"]["ap"]
        spread = round(ask_price - bid_price, 2)  # ✅ New metric: bid-ask spread
        last_trade_price = (bid_price + ask_price) / 2
        volume = data["quote"].get("bv", 0)  # ✅ New metric: trading volume

        stock_info = {
            "symbol": symbol,
            "bid_price": bid_price,
            "ask_price": ask_price,
            "last_trade_price": last_trade_price,
            "spread": spread,
            "volume": volume,
            "timestamp": datetime.utcnow()
        }

        # Store in MongoDB
        stock_data_collection.insert_one(stock_info)
        logger.info(f"✅ Stock Data Stored: {stock_info}")

        return stock_info
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to get stock data: {e}")
        return None

def place_trade(symbol, qty, side, order_type="market", time_in_force="gtc"):
    """
    Places a trade on Alpaca Paper Trading account and logs it in MongoDB.
    """
    url = f"{BASE_TRADE_URL}/orders"
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
    # ✅ Get account balance
    account_info = get_account_info()
    if account_info:
        print(f"\n💰 Account Balance: ${account_info['cash']}")
        print(f"📊 Buying Power: ${account_info['buying_power']}")
        print(f"📈 Portfolio Value: ${account_info['equity']}\n")

    # ✅ Get open positions in portfolio
    portfolio_positions = get_portfolio_positions()
    if portfolio_positions:
        print("\n📊 Current Portfolio Holdings:")
        for position in portfolio_positions:
            print(f"🔹 {position['symbol']}: {position['qty']} shares (${position['market_value']})")

    # ✅ Get stock data for AAPL
    stock_info = get_stock_data("AAPL")
    
    # ✅ Buy 1 share of AAPL
    place_trade(symbol="AAPL", qty=1, side="buy")
