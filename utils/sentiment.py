from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze(self, text):
        """Compute sentiment score using both VADER and TextBlob."""
        if not text:
            return {"vader_score": 0, "textblob_polarity": 0, "textblob_subjectivity": 0}

        vader_score = self.vader.polarity_scores(text)["compound"]
        blob = TextBlob(text)
        return {
            "vader_score": vader_score,
            "textblob_polarity": blob.polarity,
            "textblob_subjectivity": blob.subjectivity
        }

    def calculate_expected_impact(self, text, sentiment, source=None):
        """
        Generic impact score formula based on sentiment strength, source influence, 
        and stock mentions (for news).
        """
        content_length_factor = len(text.split()) / 100  # Scale by article length
        sentiment_strength = abs(sentiment["vader_score"]) * 5  # Stronger sentiment → Higher impact
        source_factor = 2 if source and source.lower() in {"bloomberg", "cnbc", "reuters"} else 0  # News source weight
        keyword_count = text.lower().count("stock") + text.lower().count("market")  # Stock keyword emphasis

        expected_impact = round(sentiment_strength + content_length_factor + source_factor + keyword_count, 2)
        return expected_impact
