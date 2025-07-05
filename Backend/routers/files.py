from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import uuid
from storage import get_storage_client
from database import MongoDBClient
from schemas import FileUploadResponse, FileMetadata, HealthResponse
from datetime import datetime
from config import STORAGE_BACKEND
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["files"])

# Initialize clients
storage_client = get_storage_client(STORAGE_BACKEND)
mongo_client = MongoDBClient()

# Supported file extensions
ALLOWED_EXTENSIONS = {".txt", ".jpg", ".png", ".json"}

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to storage and save metadata in MongoDB."""
    logger.info(f"Received upload request for file: {file.filename}")
    
    # Validate file and extension
    if not file.filename:
        logger.warning("Upload attempted with no file")
        raise HTTPException(status_code=400, detail="No file provided")
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        logger.warning(f"Unsupported file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: .txt, .jpg, .png, .json")
    
    try:
        object_name = f"{uuid.uuid4()}{file.filename}"
        content = await file.read()
        if len(content) == 0:
            logger.warning(f"Empty file uploaded: {file.filename}")
            raise HTTPException(status_code=400, detail="File is empty")
        
        file_size = len(content)
        storage_client.upload_file(object_name, content, file.content_type)
        
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
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/files", response_model=List[FileMetadata])
async def list_files():
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
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected list files error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a file by ID from storage."""
    logger.info(f"Download request for file ID: {file_id}")
    try:
        file_metadata = mongo_client.get_file_by_id(file_id)
        if not file_metadata:
            logger.warning(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")
        
        file_stream = storage_client.get_file(file_metadata["object_name"])
        logger.info(f"File downloaded: {file_metadata['filename']}")
        return StreamingResponse(
            file_stream,
            media_type=file_metadata["content_type"],
            headers={"Content-Disposition": f'attachment; filename="{file_metadata["filename"]}"'}
        )
    except ValueError as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check health of MongoDB and storage backend."""
    logger.info("Health check requested")
    try:
        mongo_status = mongo_client.check_health()
        storage_status = storage_client.check_health()
        # Determine overall status
        overall_status = "healthy" if mongo_status["status"] == "healthy" and storage_status["status"] == "healthy" else "unhealthy"
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
            status="unhealthy",
            components={
                "mongodb": {"status": "unhealthy", "error": str(e)},
                "storage": {"status": "unhealthy", "error": str(e)}
            }
        )