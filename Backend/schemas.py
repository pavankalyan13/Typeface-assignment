from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class FileUploadResponse(BaseModel):
    """Response schema for file upload."""
    file_id: str
    filename: str
    size: int

class FileMetadata(BaseModel):
    """Schema for file metadata in list response."""
    file_id: str
    filename: str
    upload_date: datetime

class HealthComponent(BaseModel):
    """Schema for health check component status."""
    status: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    components: Dict[str, HealthComponent]