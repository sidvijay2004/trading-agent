from utils.sentiment import SentimentAnalyzer
from datetime import datetime, timedelta

class BaseAPI:
    TRACKED_STOCKS = ["TSLA", "NVDA", "META", "AMZN", "AAPL", "GME", "AMC", "PLTR", "MSFT", "GOOGL", "ARKK", "SPY"]

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()

    def analyze_sentiment(self, text):
        """Use shared sentiment analysis logic."""
        return self.sentiment_analyzer.analyze(text)

    def calculate_expected_impact(self, text, sentiment, source=None):
        """Default expected impact calculation (overridden in child classes if needed)."""
        return self.sentiment_analyzer.calculate_expected_impact(text, sentiment, source)

    def filter_stock_mentions(self, text):
        """Check if text mentions any tracked stock ticker."""
        return any(stock in text for stock in self.TRACKED_STOCKS)

    def get_tracked_stock(self, text):
        """
        Identify the first stock mentioned in the given text.
        Returns the stock ticker if found, otherwise None.
        """
        for stock in self.TRACKED_STOCKS:
            if stock in text:
                return stock  # ✅ Return the first matched stock
        return None  # ❌ No tracked stock found
    
    def get_market_window_start(self):
        """
        Returns the datetime to use as the start of the sentiment fetch window.
        - Monday → past 3 days (Fri + weekend)
        - Tues–Fri → past 24 hours
        """
        now = datetime.utcnow()
        weekday = now.weekday()

        if weekday == 0:
            return now - timedelta(days=3)
        else:
            return now - timedelta(days=1)
