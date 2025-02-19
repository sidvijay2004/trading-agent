from APIs.newsAPI import NewsAPI
from APIs.redditAPI import RedditAPI
from APIs.XAPI import XAPI

def run_all():
    news_api = NewsAPI()
    reddit_api = RedditAPI()
    x_api = XAPI()

    news_api.fetch_financial_news()
    reddit_api.fetch_reddit_posts()
    x_api.fetch_tweets()

if __name__ == "__main__":
    run_all()
