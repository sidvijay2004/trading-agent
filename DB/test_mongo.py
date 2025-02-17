from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get MongoDB URI from .env file
MONGO_URI = os.getenv("MONGO_URI")

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client["sentimentData"]

    # List collections in the database
    collections = db.list_collection_names()
    print("✅ Connected to MongoDB!")
    print("📂 Available collections:", collections)

except Exception as e:
    print(f"⚠️ Connection error: {e}")
