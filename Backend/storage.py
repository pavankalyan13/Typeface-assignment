from minio import Minio
from minio.error import S3Error
import io
import os
from typing import Any
from config import STORAGE_BACKEND, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, MINIO_SECURE, LOCAL_STORAGE_PATH

class StorageClient:
    """Abstract base class for storage operations."""

    def upload_file(self, object_name: str, data: bytes, content_type: str) -> None:
        raise NotImplementedError

    def get_file(self, object_name: str) -> Any:
        raise NotImplementedError

    def check_health(self) -> dict:
        raise NotImplementedError

class MinIOClient(StorageClient):
    """MinIO client for file storage operations."""

    def __init__(self):
        """Initialize MinIO client and create bucket if needed."""
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        self.bucket_name = MINIO_BUCKET_NAME
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, object_name: str, data: bytes, content_type: str) -> None:
        """Upload file to MinIO bucket."""
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type
            )
        except S3Error as e:
            raise ValueError(f"MinIO upload failed: {str(e)}")

    def get_file(self, object_name: str) -> Any:
        """Retrieve file from MinIO bucket."""
        try:
            return self.client.get_object(self.bucket_name, object_name)
        except S3Error as e:
            raise ValueError(f"MinIO download failed: {str(e)}")

    def check_health(self) -> dict:
        """Check MinIO bucket accessibility."""
        try:
            self.client.bucket_exists(self.bucket_name)
            return {"status": "healthy"}
        except S3Error as e:
            return {"status": "unhealthy", "error": str(e)}

class LocalStorageClient(StorageClient):
    """Local filesystem client for file storage operations."""

    def __init__(self):
        """Initialize local storage directory."""
        self.storage_path = LOCAL_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)

    def upload_file(self, object_name: str, data: bytes, content_type: str) -> None:
        """Save file to local storage."""
        try:
            file_path = os.path.join(self.storage_path, object_name)
            with open(file_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            raise ValueError(f"Local storage upload failed: {str(e)}")

    def get_file(self, object_name: str) -> Any:
        """Retrieve file from local storage."""
        try:
            file_path = os.path.join(self.storage_path, object_name)
            if not os.path.exists(file_path):
                raise ValueError("File not found")
            return open(file_path, 'rb')
        except Exception as e:
            raise ValueError(f"Local storage download failed: {str(e)}")

    def check_health(self) -> dict:
        """Check local storage directory accessibility."""
        try:
            if os.path.exists(self.storage_path) and os.access(self.storage_path, os.W_OK):
                return {"status": "healthy"}
            raise ValueError("Storage path inaccessible")
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

def get_storage_client(backend: str) -> StorageClient:
    """Return storage client for the specified backend."""
    if backend.lower() == "minio":
        return MinIOClient()
    if backend.lower() == "local":
        return LocalStorageClient()
    raise ValueError(f"Unknown storage backend: {backend}")