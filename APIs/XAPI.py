import requests

# Replace with your own Twitter API Bearer Token
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEb8ygEAAAAA3gOt9vPddaM0Hzp738AXNQN0D94%3DLzJESTfjiUffLQeCmCnY3TR3sQ9BtB6XQkorEOy7VYnHCzWOoa"

# Define the search query
QUERY = "stock market"  # Change to any keyword you're tracking

# Define the API endpoint
URL = "https://api.twitter.com/2/tweets/search/recent"

# Define request headers
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# Define request parameters
PARAMS = {
    "query": QUERY,
    "max_results": 1,  # Number of tweets to retrieve (Max: 100)
    "tweet.fields": "created_at,author_id"
}

def fetch_tweets():
    response = requests.get(URL, headers=HEADERS, params=PARAMS)
    
    if response.status_code == 200:
        data = response.json()
        for tweet in data.get("data", []):
            print(f"{tweet['created_at']} - {tweet['id']}: {tweet['text']}\n")
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Run the function
fetch_tweets()
