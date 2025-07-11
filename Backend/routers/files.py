from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
import uuid
from storage import StorageClient, get_storage_client
from database import MongoDBClient
from schemas import FileUploadResponse, FileMetadata, HealthResponse
from datetime import datetime
from config import CONFIG
from tenacity import retry, stop_after_attempt, wait_fixed
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["files"])

# Dependency injection for clients
def get_mongo_client():
    return MongoDBClient()

def get_storage_client_dep():
    return get_storage_client(CONFIG.STORAGE_BACKEND)

@router.post("/upload", response_model=FileUploadResponse)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
async def upload_file(file: UploadFile = File(...), storage_client: StorageClient = Depends(get_storage_client_dep), mongo_client: MongoDBClient = Depends(get_mongo_client)):
    """Upload a file to storage and save metadata in MongoDB."""
    logger.info(f"Received upload request for file: {file.filename}")
    
    # Validate file and extension
    if not file.filename:
        logger.warning("Upload attempted with no file")
        raise HTTPException(status_code=400, detail="No file provided")
    if not any(file.filename.lower().endswith(ext) for ext in CONFIG.ALLOWED_EXTENSIONS):
        logger.warning(f"Unsupported file type: {file.filename}")
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(CONFIG.ALLOWED_EXTENSIONS)}")
    
    try:
        object_name = f"{uuid.uuid4()}{file.filename}"
        file_content = await file.read()
        if len(file_content) == 0:
            logger.warning(f"Empty file uploaded: {file.filename}")
            raise HTTPException(status_code=400, detail="File is empty")
        
        file_size = len(file_content)
        storage_client.upload_file(object_name, file_content, file.content_type)
        
        file_metadata = {
            "filename": file.filename,
            "size": file_size,
            "content_type": file.content_type,
            "upload_date": datetime.utcnow(),
            "object_name": object_name
        }
        file_id = mongo_client.insert_file(file_metadata)
        
        logger.info(f"File uploaded successfully: {file.filename}, ID: {file_id}")
        return FileUploadResponse(file_id=file_id, filename=file.filename, size=file_size)
    except ValueError as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected file upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/files", response_model=List[FileMetadata])
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
async def list_files(mongo_client: MongoDBClient = Depends(get_mongo_client)):
    """Retrieve metadata for all files."""
    logger.info("Listing all files")
    try:
        files = mongo_client.get_files()
        return [
            FileMetadata(
                file_id=str(f["_id"]),
                filename=f["filename"],
                upload_date=f["upload_date"]
            ) for f in files
        ]
    except ValueError as e:
        logger.error(f"List files failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"List files failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected list files error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/download/{file_id}")
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
async def download_file(file_id: str, storage_client: StorageClient = Depends(get_storage_client_dep), mongo_client: MongoDBClient = Depends(get_mongo_client)):
    """Download a file by ID from storage."""
    logger.info(f"Download request for file ID: {file_id}")
    # Validate file_id format
    from bson import ObjectId
    if not ObjectId.is_valid(file_id):
        logger.warning(f"Invalid file ID format: {file_id}")
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    try:
        file_metadata = mongo_client.get_file_by_id(file_id)
        if not file_metadata:
            logger.warning(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found in database")
        
        # Verify file exists in storage
        if not storage_client.file_exists(file_metadata["object_name"]):
            logger.warning(f"File not found in storage: {file_metadata['object_name']}")
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        file_stream = storage_client.get_file(file_metadata["object_name"])
        logger.info(f"File downloaded: {file_metadata['filename']}")
        return StreamingResponse(
            file_stream,
            media_type=file_metadata["content_type"],
            headers={"Content-Disposition": f'attachment; filename="{file_metadata["filename"]}"'}
        )
    except ValueError as e:
        logger.error(f"File download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected file download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", response_model=HealthResponse)
async def health_check(storage_client: StorageClient = Depends(get_storage_client_dep), mongo_client: MongoDBClient = Depends(get_mongo_client)):
    """Check health of MongoDB and storage backend."""
    logger.info("Health check requested")
    try:
        mongo_status = mongo_client.check_health()
        storage_status = storage_client.check_health()
        # Combine statuses: overall status is healthy only if both components are healthy
        overall_status = CONFIG.HEALTHY if mongo_status["status"] == CONFIG.HEALTHY and storage_status["status"] == CONFIG.HEALTHY else CONFIG.UNHEALTHY
        logger.debug(f"Health check result: {overall_status}")
        return HealthResponse(
            status=overall_status,
            components={
                "mongodb": mongo_status,
                "storage": storage_status
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status=CONFIG.UNHEALTHY,
            components={
                "mongodb": {"status": CONFIG.UNHEALTHY, "error": str(e)},
                "storage": {"status": CONFIG.UNHEALTHY, "error": str(e)}
            }
        )