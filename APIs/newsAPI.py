import requests
import datetime
from DB.dbConnection import news_collection 
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")

def fetch_financial_news():
    url = f"https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "language": "en",
        "apiKey": API_KEY,
        "pageSize": 5,  # Fetch latest 5 articles to avoid rate limit issues
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        news_articles = []

        for article in data["articles"]:
            news_data = {
                "title": article["title"],
                "description": article.get("description", ""),  
                "content": article.get("content", ""),  
                "source": article["source"]["name"],
                "published": article["publishedAt"],
                "url": article["url"],
                "timestamp": datetime.datetime.utcnow()
            }   
            news_articles.append(news_data)

        if news_articles:
            news_collection.insert_many(news_articles)  # Insert into MongoDB
            print(f"Inserted {len(news_articles)} news articles into MongoDB!")

    else:
        print(f"Error: {response.status_code}, {response.text}")

fetch_financial_news()
