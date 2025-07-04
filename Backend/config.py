import os
from dotenv import load_dotenv

load_dotenv()

# Configuration for storage backend
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "minio")  # Options: "minio" or "local"

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "supersecret")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET", "myfiles")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

# Local storage configuration
LOCAL_STORAGE_PATH = "./uploads"