from typing import Set
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration for the application."""
    # Default to MinIO for storage backend; set to "local" for filesystem storage
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "minio")
    
    # MinIO configuration
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "admin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "supersecret")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET", "myfiles")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"
    
    # Local storage directory
    LOCAL_STORAGE_PATH: str = "./Uploads"
    
    # Logging level (e.g., DEBUG, INFO, WARNING, ERROR)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # MongoDB configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "mydb")
    
    # Supported file extensions
    ALLOWED_EXTENSIONS: Set[str] = {".txt", ".jpg", ".png", ".json"}
    
    # Health check status constants
    HEALTHY: str = "healthy"
    UNHEALTHY: str = "unhealthy"
    
    # CORS origin for frontend; default matches README's frontend URL
    CORS_ORIGIN: str = os.getenv("CORS_ORIGIN", "http://localhost:3000")

CONFIG = Config()