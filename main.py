import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from APIs.newsAPI import NewsAPI
from APIs.redditAPI import RedditAPI
from utils.tradingModel import execute_trades  # Import trading function

def run_sentiment_analysis():
    """
    Fetches financial news, Reddit posts, and tweets and stores them in MongoDB.
    """
    news_api = NewsAPI()
    reddit_api = RedditAPI()

    news_api.fetch_financial_news()
    reddit_api.fetch_reddit_posts()

if __name__ == "__main__":
    print("🚀 Running sentiment analysis...")
    run_sentiment_analysis()

    print("📈 Running trading model based on sentiment data...")
    execute_trades()

def lambda_handler(event=None, context=None):
    run_sentiment_analysis()
    return {"status": "success"}

