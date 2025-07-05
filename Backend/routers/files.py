from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import uuid
from storage import get_storage_client
from database import MongoDBClient
from datetime import datetime
from config import STORAGE_BACKEND

router = APIRouter(prefix="/api", tags=["files"])

# Initialize clients
storage_client = get_storage_client(STORAGE_BACKEND)
mongo_client = MongoDBClient()

# Supported file extensions
ALLOWED_EXTENSIONS = {".txt", ".jpg", ".png", ".json"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to storage and save metadata in MongoDB."""
    # Validate file extension
    if not file.filename or not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: .txt, .jpg, .png, .json")
    
    try:
        object_name = f"{uuid.uuid4()}{file.filename}"
        content = await file.read()
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
        
        return {"file_id": file_id, "filename": file.filename, "size": file_size}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/files")
async def list_files():
    """Retrieve metadata for all files."""
    try:
        files = mongo_client.get_files()
        return [{"file_id": str(f["_id"]), "filename": f["filename"], "upload_date": f["upload_date"]} for f in files]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a file by ID from storage."""
    try:
        file_metadata = mongo_client.get_file_by_id(file_id)
        if not file_metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_stream = storage_client.get_file(file_metadata["object_name"])
        return StreamingResponse(
            file_stream,
            media_type=file_metadata["content_type"],
            headers={"Content-Disposition": f'attachment; filename="{file_metadata["filename"]}"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Check health of MongoDB and storage backend."""
    try:
        mongo_status = mongo_client.check_health()
        storage_status = storage_client.check_health()
        # Determine overall status
        overall_status = "healthy" if mongo_status["status"] == "healthy" and storage_status["status"] == "healthy" else "unhealthy"
        return {
            "status": overall_status,
            "components": {
                "mongodb": mongo_status,
                "storage": storage_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "components": {
                "mongodb": {"status": "unhealthy", "error": str(e)},
                "storage": {"status": "unhealthy", "error": str(e)}
            }
        }