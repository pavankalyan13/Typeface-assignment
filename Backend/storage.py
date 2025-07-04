from minio import Minio
from minio.error import S3Error
import io
import os
from config import STORAGE_BACKEND, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, MINIO_SECURE, LOCAL_STORAGE_PATH

class StorageClient:
    def upload_file(self, object_name: str, data: bytes, content_type: str):
        raise NotImplementedError

    def get_file(self, object_name: str):
        raise NotImplementedError

    def check_health(self):
        raise NotImplementedError

class MinIOClient(StorageClient):
    def __init__(self):
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        self.bucket_name = MINIO_BUCKET_NAME
        if not self.client.bucket_exists(self.bucket_name):
            self.bucket = self.client.make_bucket(self.bucket_name)

    def upload_file(self, object_name: str, data: bytes, content_type: str):
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type
            )
        except S3Error as e:
            raise Exception(f"MinIO upload error: {str(e)}")

    def get_file(self, object_name: str):
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response
        except S3Error as e:
            raise Exception(f"MinIO download error: {str(e)}")

    def check_health(self):
        try:
            self.client.bucket_exists(self.bucket_name)
            return {"status": "healthy"}
        except S3Error as e:
            return {"status": "unhealthy", "error": str(e)}

class LocalStorageClient(StorageClient):
    def __init__(self):
        self.storage_path = LOCAL_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)

    def upload_file(self, object_name: str, data: bytes, content_type: str):
        try:
            file_path = os.path.join(self.storage_path, object_name)
            with open(file_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            raise Exception(f"Local storage upload error: {str(e)}")

    def get_file(self, object_name: str):
        try:
            file_path = os.path.join(self.storage_path, object_name)
            if not os.path.exists(file_path):
                raise Exception("File not found")
            return open(file_path, 'rb')
        except Exception as e:
            raise Exception(f"Local storage download error: {str(e)}")

    def check_health(self):
        try:
            if os.path.exists(self.storage_path) and os.access(self.storage_path, os.W_OK):
                return {"status": "healthy"}
            else:
                raise Exception("Storage path is not accessible")
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

def get_storage_client(backend: str) -> StorageClient:
    if backend.lower() == "minio":
        return MinIOClient()
    elif backend.lower() == "local":
        return LocalStorageClient()
    else:
        raise ValueError(f"Unknown storage backend: {backend}")