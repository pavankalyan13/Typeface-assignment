from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBClient:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[os.getenv("MONGODB_DATABASE", "mydb")]
        self.collection = self.db["files"]

    def insert_file(self, file_metadata: dict) -> str:
        result = self.collection.insert_one(file_metadata)
        return str(result.inserted_id)

    def get_files(self) -> list:
        files = list(self.collection.find())
        return files

    def get_file_by_id(self, file_id: str) -> dict:
        file = self.collection.find_one({"_id": ObjectId(file_id)})
        return file

    def check_health(self):
        try:
            self.db.command("ping")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}