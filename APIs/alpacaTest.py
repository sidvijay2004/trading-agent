import os
import requests
from dotenv import load_dotenv

# Load API credentials
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")

# Alpaca News API endpoint
NEWS_URL = "https://data.alpaca.markets/v1beta1/news"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET
}

# Fetch news from Alpaca
response = requests.get(NEWS_URL, headers=headers)

# Print response
print(response.json())
