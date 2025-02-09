import requests

API_KEY = "ee3dba36a8bb4bfb9b1b45b940a5f685"

def fetch_financial_news():
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for article in data["articles"][:5]:  # Fetch latest 5 articles
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']['name']}")
            print(f"Published: {article['publishedAt']}")
            print(f"URL: {article['url']}\n")
    else:
        print(f"Error: {response.status_code}, {response.text}")

fetch_financial_news()
