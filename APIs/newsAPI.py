import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from DB.dbConnection import news_collection
from baseAPI import BaseAPI

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

class NewsAPI(BaseAPI):
    def fetch_financial_news(self):
        url = "https://newsapi.org/v2/everything"
        from_time = self.get_market_window_start().isoformat()
        news_articles = []

        for page in range(1, 3):
            params = {
                "q": "stock market OR investing OR trading",
                "language": "en",
                "sortBy": "publishedAt",
                "from": from_time,
                "apiKey": API_KEY,
                "pageSize": 50,
                "page": page,
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                for article in data.get("articles", []):
                    title = article.get("title", "")
                    url = article.get("url")

                    if news_collection.find_one({"$or": [{"url": url}, {"title": title}]}):
                        continue

                    description = article.get("description", "")
                    content = article.get("content", "")
                    source = article["source"]["name"]
                    full_text = f"{title} {description} {content}"

                    stock = self.get_tracked_stock(full_text)
                    if not stock:
                        continue

                    sentiment = self.analyze_sentiment(full_text)
                    expected_impact = self.calculate_expected_impact(full_text, sentiment, source)

                    news_data = {
                        "stock": stock,
                        "title": title,
                        "description": description,
                        "content": content,
                        "source": source,
                        "published": article["publishedAt"],
                        "url": url,
                        "timestamp": datetime.utcnow(),
                        "sentiment": sentiment,
                        "expected_impact": expected_impact
                    }

                    news_articles.append(news_data)

            else:
                print(f"❌ Error on page {page}: {response.status_code}, {response.text}")
                break

        if news_articles:
            news_collection.insert_many(news_articles)
            print(f"✅ Inserted {len(news_articles)} filtered news articles into MongoDB!")

if __name__ == "__main__":
    news_api = NewsAPI()
    news_api.fetch_financial_news()
