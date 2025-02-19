from utils.sentiment import SentimentAnalyzer

class BaseAPI:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()

    def analyze_sentiment(self, text):
        """Use shared sentiment analysis logic."""
        return self.sentiment_analyzer.analyze(text)

    def calculate_expected_impact(self, text, sentiment, source=None):
        """Default expected impact calculation (overridden in child classes if needed)."""
        return self.sentiment_analyzer.calculate_expected_impact(text, sentiment, source)
