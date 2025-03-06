from APIs.newsAPI import NewsAPI
from APIs.redditAPI import RedditAPI
from APIs.XAPI import XAPI
from utils.tradingModel import execute_trades  # Import trading function

def run_sentiment_analysis():
    """
    Fetches financial news, Reddit posts, and tweets and stores them in MongoDB.
    """
    news_api = NewsAPI()
    reddit_api = RedditAPI()
    x_api = XAPI()

    news_api.fetch_financial_news()
    reddit_api.fetch_reddit_posts()
    x_api.fetch_tweets()

if __name__ == "__main__":
    print("🚀 Running sentiment analysis...")
    run_sentiment_analysis()

    print("📈 Running trading model based on sentiment data...")
    execute_trades()
