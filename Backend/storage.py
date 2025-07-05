from minio import Minio
from minio.error import S3Error
import io
import os
from typing import Any
from config import CONFIG
from tenacity import retry, stop_after_attempt, wait_fixed
import logging

logger = logging.getLogger(__name__)

class StorageClient:
    """Abstract base class to support multiple storage backends (e.g., MinIO, local filesystem)."""

    def upload_file(self, object_name: str, file_content: bytes, content_type: str) -> None:
        raise NotImplementedError

    def get_file(self, object_name: str) -> Any:
        raise NotImplementedError

    def file_exists(self, object_name: str) -> bool:
        raise NotImplementedError

    def check_health(self) -> dict:
        raise NotImplementedError

class MinIOClient(StorageClient):
    """MinIO client for file storage operations."""

    def __init__(self):
        """Initialize MinIO client and create bucket if needed."""
        try:
            self.client = Minio(
                CONFIG.MINIO_ENDPOINT,
                access_key=CONFIG.MINIO_ACCESS_KEY,
                secret_key=CONFIG.MINIO_SECRET_KEY,
                secure=CONFIG.MINIO_SECURE
            )
            self.bucket_name = CONFIG.MINIO_BUCKET_NAME
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            logger.info("MinIO client initialized")
        except S3Error as e:
            logger.error(f"MinIO initialization failed: {str(e)}")
            raise ValueError(f"MinIO initialization failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    def upload_file(self, object_name: str, file_content: bytes, content_type: str) -> None:
        """Upload file to MinIO bucket."""
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(file_content),
                length=len(file_content),
                content_type=content_type
            )
            logger.debug(f"Uploaded file to MinIO: {object_name}")
        except S3Error as e:
            logger.error(f"MinIO upload failed for {object_name}: {str(e)}")
            raise ValueError(f"MinIO upload failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    def get_file(self, object_name: str) -> Any:
        """Retrieve file from MinIO bucket."""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            logger.debug(f"Retrieved file from MinIO: {object_name}")
            return response
        except S3Error as e:
            logger.error(f"MinIO download failed for {object_name}: {str(e)}")
            raise ValueError(f"MinIO download failed: {str(e)}")

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in MinIO bucket."""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    def check_health(self) -> dict:
        """Check MinIO bucket accessibility."""
        try:
            self.client.bucket_exists(self.bucket_name)
            logger.debug("MinIO health check passed")
            return {"status": CONFIG.HEALTHY}
        except S3Error as e:
            logger.error(f"MinIO health check failed: {str(e)}")
            return {"status": CONFIG.UNHEALTHY, "error": str(e)}

class LocalStorageClient(StorageClient):
    """Local filesystem client for file storage operations."""

    def __init__(self):
        """Initialize local storage directory."""
        try:
            self.storage_path = CONFIG.LOCAL_STORAGE_PATH
            os.makedirs(self.storage_path, exist_ok=True)
            logger.info("Local storage client initialized")
        except OSError as e:
            logger.error(f"Local storage initialization failed: {str(e)}")
            raise ValueError(f"Local storage initialization failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
    def upload_file(self, object_name: str, file_content: bytes, content_type: str) -> None:
        """Save file to local storage."""
        try:
            file_path = os.path.join(self.storage_path, object_name)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            logger.debug(f"Uploaded file to local storage: {object_name}")
        except OSError as e:
            logger.error(f"Local storage upload failed for {object_name}: {str(e)}")
            raise ValueError(f"Local storage upload failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
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

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in local storage."""
        file_path = os.path.join(self.storage_path, object_name)
        return os.path.exists(file_path)

    def check_health(self) -> dict:
        """Check local storage directory accessibility."""
        try:
            if os.path.exists(self.storage_path) and os.access(self.storage_path, os.W_OK):
                logger.debug("Local storage health check passed")
                return {"status": CONFIG.HEALTHY}
            raise ValueError("Storage path inaccessible")
        except Exception as e:
            logger.error(f"Local storage health check failed: {str(e)}")
            return {"status": CONFIG.UNHEALTHY, "error": str(e)}

def get_storage_client(backend: str) -> StorageClient:
    """Return storage client for the specified backend."""
    if backend.lower() == "minio":
        return MinIOClient()
    if backend.lower() == "local":
        return LocalStorageClient()
    logger.error(f"Invalid storage backend: {backend}")
    raise ValueError(f"Unknown storage backend: {backend}")