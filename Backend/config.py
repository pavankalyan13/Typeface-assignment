import os
from dotenv import load_dotenv

load_dotenv()

# Storage backend type (minio or local)
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "minio")

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "supersecret")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET", "myfiles")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

# Local storage directory
LOCAL_STORAGE_PATH = "./Uploads"