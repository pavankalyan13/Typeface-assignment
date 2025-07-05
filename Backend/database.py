from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId
from typing import Dict, List
import logging
from config import CONFIG
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for managing file metadata."""

    def __init__(self):
        """Initialize MongoDB connection using configuration."""
        try:
            self.client = MongoClient(CONFIG.MONGODB_URI)
            self.db = self.client[CONFIG.MONGODB_DATABASE]
            self.collection = self.db["files"]
            logger.info("MongoDB client initialized")
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise ValueError(f"MongoDB connection failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    def insert_file(self, file_metadata: Dict) -> str:
        """Insert file metadata and return its ID."""
        try:
            result = self.collection.insert_one(file_metadata)
            logger.debug(f"Inserted file metadata with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except OperationFailure as e:
            logger.error(f"Failed to insert file metadata: {str(e)}")
            raise ValueError(f"Database insert failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    def get_files(self) -> List[Dict]:
        """Retrieve metadata for all files."""
        try:
            files = list(self.collection.find())
            logger.debug(f"Retrieved {len(files)} files")
            return files
        except OperationFailure as e:
            logger.error(f"Failed to retrieve files: {str(e)}")
            raise ValueError(f"Database query failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    def get_file_by_id(self, file_id: str) -> Dict:
        """Retrieve file metadata by ID."""
        try:
            file = self.collection.find_one({"_id": ObjectId(file_id)})
            if not file:
                logger.warning(f"File not found: {file_id}")
            return file
        except OperationFailure as e:
            logger.error(f"Failed to retrieve file {file_id}: {str(e)}")
            raise ValueError(f"Database query failed: {str(e)}")

    def check_health(self) -> Dict:
        """Check MongoDB connection health."""
        try:
            self.db.command("ping")
            logger.debug("MongoDB health check passed")
            return {"status": CONFIG.HEALTHY}
        except ConnectionFailure as e:
            logger.error(f"MongoDB health check failed: {str(e)}")
            return {"status": CONFIG.UNHEALTHY, "error": str(e)}