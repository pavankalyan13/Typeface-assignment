from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, List
import os

class MongoDBClient:
    """MongoDB client for managing file metadata."""

    def __init__(self):
        """Initialize MongoDB connection using environment variables."""
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[os.getenv("MONGODB_DATABASE", "mydb")]
        self.collection = self.db["files"]

    def insert_file(self, file_metadata: Dict) -> str:
        """Insert file metadata and return its ID."""
        result = self.collection.insert_one(file_metadata)
        return str(result.inserted_id)

    def get_files(self) -> List[Dict]:
        """Retrieve metadata for all files."""
        return list(self.collection.find())

    def get_file_by_id(self, file_id: str) -> Dict:
        """Retrieve file metadata by ID."""
        try:
            return self.collection.find_one({"_id": ObjectId(file_id)})
        except ValueError:
            return None

    def check_health(self) -> Dict:
        """Check MongoDB connection health."""
        try:
            self.db.command("ping")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}