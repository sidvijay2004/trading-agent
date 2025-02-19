import requests
import datetime
import os
from dotenv import load_dotenv
from DB.dbConnection import news_collection
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

# Stocks to track
TRACKED_STOCKS = {
    "TSLA": "Tesla",
    "NVDA": "Nvidia",
    "META": "Meta",
    "AMZN": "Amazon",
    "AAPL": "Apple",
    "GME": "GameStop",
    "AMC": "AMC",
    "PLTR": "Palantir",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet"
}

# Reputable sources with market influence
HIGH_IMPACT_SOURCES = {"bloomberg", "cnbc", "reuters", "marketwatch", "the-wall-street-journal"}

vader = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """Calculate sentiment score using both VADER and TextBlob."""
    if not text:
        return {"vader_score": 0, "textblob_polarity": 0, "textblob_subjectivity": 0}

    vader_score = vader.polarity_scores(text)["compound"]
    blob = TextBlob(text)
    return {
        "vader_score": vader_score,
        "textblob_polarity": blob.polarity,
        "textblob_subjectivity": blob.subjectivity
    }

def calculate_expected_impact(title, description, content, sentiment, source, matched_stock):
    """
    Quantifies the expected impact of the news article on the stock price 
    based on sentiment strength, article length, source reputation, 
    and keyword emphasis.
    """
    content_length_factor = len(content.split()) / 100 
    sentiment_strength = abs(sentiment["vader_score"]) * 5 
    source_factor = 2 if source.lower() in HIGH_IMPACT_SOURCES else 0 
    keyword_count = (
        title.lower().count(matched_stock.lower()) * 2 + description.lower().count(matched_stock.lower())
    ) 

    expected_impact = round(sentiment_strength + content_length_factor + source_factor + keyword_count, 2)
    return expected_impact

def fetch_financial_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": " OR ".join(TRACKED_STOCKS.values()),
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": API_KEY,
        "pageSize": 20,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        news_articles = []

        for article in data.get("articles", []):
            title = article.get("title", "")
            description = article.get("description", "")
            content = article.get("content", "")
            source = article["source"]["name"].lower()

            matched_stock = None
            matched_ticker = None
            for ticker, name in TRACKED_STOCKS.items():
                if name.lower() in (title + " " + description).lower():
                    matched_stock = name
                    matched_ticker = ticker
                    break

            if not matched_stock:
                continue

            sentiment = get_sentiment(f"{title} {description} {content}")

            expected_impact = calculate_expected_impact(title, description, content, sentiment, source, matched_stock)

            news_data = {
                "title": title,
                "description": description,
                "content": content,
                "source": article["source"]["name"],
                "published": article["publishedAt"],
                "url": article["url"],
                "timestamp": datetime.datetime.utcnow(),
                "sentiment": sentiment,
                "tracked_stock": matched_stock,
                "expected_impact": expected_impact
            }
            news_articles.append(news_data)

        if news_articles:
            news_collection.insert_many(news_articles)
            print(f"Inserted {len(news_articles)} filtered news articles into MongoDB!")

    else:
        print(f"Error: {response.status_code}, {response.text}")

fetch_financial_news()
