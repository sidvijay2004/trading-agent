import requests
import datetime
import os
from dotenv import load_dotenv
from DB.dbConnection import news_collection
from baseAPI import BaseAPI  # ✅ Inherit from BaseAPI

# Load environment variables
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

class NewsAPI(BaseAPI):
    def fetch_financial_news(self):
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "stock market OR investing OR trading",
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
                source = article["source"]["name"]

                full_text = f"{title} {description} {content}"
                stock = self.get_tracked_stock(full_text)  # ✅ Identify stock
                if not stock:
                    continue  # Skip if no tracked stock is mentioned

                sentiment = self.analyze_sentiment(full_text)  # ✅ Use BaseAPI method
                expected_impact = self.calculate_expected_impact(full_text, sentiment, source)

                news_data = {
                    "stock": stock,  # ✅ Store stock symbol
                    "title": title,
                    "description": description,
                    "content": content,
                    "source": source,
                    "published": article["publishedAt"],
                    "url": article["url"],
                    "timestamp": datetime.datetime.utcnow(),
                    "sentiment": sentiment,
                    "expected_impact": expected_impact
                }
                news_articles.append(news_data)

            if news_articles:
                news_collection.insert_many(news_articles)
                print(f"✅ Inserted {len(news_articles)} filtered news articles into MongoDB!")

        else:
            print(f"❌ Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    news_api = NewsAPI()
    news_api.fetch_financial_news()
