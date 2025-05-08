from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class ConversionFormat(str, Enum):
    """Supported conversion formats."""
    DOCX = "docx"
    JPEG = "jpeg"
    PPT = "ppt"
    HTML = "html"


class ConversionStatus(str, Enum):
    """Possible statuses for a conversion task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConversionOptions(BaseModel):
    """Options for PDF conversion."""
    format: ConversionFormat
    pages: Optional[str] = None
    quality: Optional[int] = Field(None, ge=1, le=100, description="Image quality for JPEG conversion (1-100)")
    dpi: Optional[int] = Field(None, ge=72, le=600, description="DPI for image conversion")
    preserve_layout: Optional[bool] = Field(True, description="Preserve original layout in DOCX and HTML conversion")


class ConversionTask(BaseModel):
    """Model representing a conversion task."""
    task_id: str
    status: ConversionStatus
    created_at: datetime
    updated_at: datetime
    file_name: str
    options: ConversionOptions
    progress: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Conversion progress percentage")
    error_message: Optional[str] = None
    result_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class ConversionRequest(BaseModel):
    """Request model for conversion API."""
    # Note: File upload is handled by FastAPI's File and Form, not in this model
    format: ConversionFormat
    pages: Optional[str] = None
    quality: Optional[int] = Field(None, ge=1, le=100)
    dpi: Optional[int] = Field(None, ge=72, le=600)
    preserve_layout: Optional[bool] = True


class ConversionResponse(BaseModel):
    """Response model for conversion API."""
    task_id: str
    status: ConversionStatus = ConversionStatus.PENDING
    message: Optional[str] = None


class ConversionStatusResponse(BaseModel):
    """Response model for conversion status API."""
    task_id: str
    status: ConversionStatus
    progress: float = Field(0.0, ge=0.0, le=100.0)
    message: Optional[str] = None
    result_url: Optional[str] = None
    expires_at: Optional[datetime] = None
