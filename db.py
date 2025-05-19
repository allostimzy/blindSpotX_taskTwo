import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["drift_db"]

# Collections
snapshots_collection = db["snapshots"]
logs_collection = db["signin_logs"]

def save_snapshot(data):
    data["timestamp"] = datetime.utcnow()
    snapshots_collection.insert_one(data)

def get_snapshots():
    return list(snapshots_collection.find({}, {"_id": 0}).sort("timestamp", -1))

def save_signin_logs(logs):
    for log in logs:
        log["fetched_at"] = datetime.utcnow()
    if logs:
        logs_collection.insert_many(logs)

def get_signin_logs():
    return list(logs_collection.find({}, {"_id": 0}).sort("fetched_at", -1))
