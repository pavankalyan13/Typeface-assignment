from minio import Minio
from minio.error import S3Error
import io
import os
from typing import Any
from config import STORAGE_BACKEND, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, MINIO_SECURE, LOCAL_STORAGE_PATH
import logging

logger = logging.getLogger(__name__)

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
        try:
            self.client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )
            self.bucket_name = MINIO_BUCKET_NAME
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            logger.info("MinIO client initialized")
        except S3Error as e:
            logger.error(f"MinIO initialization failed: {str(e)}")
            raise

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
            logger.debug(f"Uploaded file to MinIO: {object_name}")
        except S3Error as e:
            logger.error(f"MinIO upload failed for {object_name}: {str(e)}")
            raise ValueError(f"MinIO upload failed: {str(e)}")

    def get_file(self, object_name: str) -> Any:
        """Retrieve file from MinIO bucket."""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            logger.debug(f"Retrieved file from MinIO: {object_name}")
            return response
        except S3Error as e:
            logger.error(f"MinIO download failed for {object_name}: {str(e)}")
            raise ValueError(f"MinIO download failed: {str(e)}")

    def check_health(self) -> dict:
        """Check MinIO bucket accessibility."""
        try:
            self.client.bucket_exists(self.bucket_name)
            logger.debug("MinIO health check passed")
            return {"status": "healthy"}
        except S3Error as e:
            logger.error(f"MinIO health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

class LocalStorageClient(StorageClient):
    """Local filesystem client for file storage operations."""

    def __init__(self):
        """Initialize local storage directory."""
        try:
            self.storage_path = LOCAL_STORAGE_PATH
            os.makedirs(self.storage_path, exist_ok=True)
            logger.info("Local storage client initialized")
        except OSError as e:
            logger.error(f"Local storage initialization failed: {str(e)}")
            raise

    def upload_file(self, object_name: str, data: bytes, content_type: str) -> None:
        """Save file to local storage."""
        try:
            file_path = os.path.join(self.storage_path, object_name)
            with open(file_path, 'wb') as f:
                f.write(data)
            logger.debug(f"Uploaded file to local storage: {object_name}")
        except OSError as e:
            logger.error(f"Local storage upload failed for {object_name}: {str(e)}")
            raise ValueError(f"Local storage upload failed: {str(e)}")

    def get_file(self, object_name: str) -> Any:
        """Retrieve file from local storage."""
        try:
            file_path = os.path.join(self.storage_path, object_name)
            if not os.path.exists(file_path):
                logger.warning(f"File not found in local storage: {object_name}")
                raise ValueError("File not found")
            logger.debug(f"Retrieved file from local storage: {object_name}")
            return open(file_path, 'rb')
        except OSError as e:
            logger.error(f"Local storage download failed for {object_name}: {str(e)}")
            raise ValueError(f"Local storage download failed: {str(e)}")

    def check_health(self) -> dict:
        """Check local storage directory accessibility."""
        try:
            if os.path.exists(self.storage_path) and os.access(self.storage_path, os.W_OK):
                logger.debug("Local storage health check passed")
                return {"status": "healthy"}
            raise ValueError("Storage path inaccessible")
        except Exception as e:
            logger.error(f"Local storage health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

def get_storage_client(backend: str) -> StorageClient:
    """Return storage client for the specified backend."""
    if backend.lower() == "minio":
        return MinIOClient()
    if backend.lower() == "local":
        return LocalStorageClient()
    logger.error(f"Invalid storage backend: {backend}")
    raise ValueError(f"Unknown storage backend: {backend}")