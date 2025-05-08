from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, FileResponse
from enum import Enum
from typing import Optional
import os
import uuid
import shutil
import logging
from datetime import datetime, timedelta
import zipfile

from app.core.config import settings
from app.models.conversion import (
    ConversionFormat, 
    ConversionStatus, 
    ConversionResponse, 
    ConversionStatusResponse
)
from app.services.conversions import docx, jpeg, ppt, html
from app.db import database
from app.api.endpoints.process_conversion import process_conversion

router = APIRouter()
logger = logging.getLogger(__name__)

# Database for task storage
# Initialize database on import
database.init_db()

@router.post("/", response_model=ConversionResponse)
async def convert_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    format: ConversionFormat = Form(...),
    pages: Optional[str] = Form(None),
    quality: Optional[int] = Form(90),
    dpi: Optional[int] = Form(300),
    preserve_layout: Optional[bool] = Form(True)
):
    """
    Convert a PDF file to the specified format.
    
    - **file**: The PDF file to convert
    - **format**: The target format (docx, jpeg, ppt, html)
    - **pages**: Optional. Specific pages to convert (e.g., "1,3-5,7")
    - **quality**: Optional. Image quality for JPEG conversion (1-100)
    - **dpi**: Optional. DPI for image conversion (72-600)
    - **preserve_layout**: Optional. Whether to preserve the original layout in DOCX and HTML conversion
    
    Returns a task ID for tracking the conversion status.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Generate a task ID
    task_id = str(uuid.uuid4())
    
    # Create a directory for the task
    task_dir = os.path.join(settings.TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    # Save the uploaded file
    pdf_path = os.path.join(task_dir, file.filename)
    with open(pdf_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Initialize task status
    task_data = {
        "task_id": task_id,
        "status": ConversionStatus.PENDING,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "file_name": file.filename,
        "format": format,
        "options": {
            "pages": pages,
            "quality": quality,
            "dpi": dpi,
            "preserve_layout": preserve_layout
        },
        "progress": 0.0,
        "error_message": None,
        "result_path": None,
        "expires_at": datetime.now() + timedelta(hours=settings.FILE_EXPIRY_HOURS)
    }
    
    # Save task to database
    database.save_task(task_data)
    
    # Add conversion task to background tasks
    background_tasks.add_task(
        process_conversion,
        task_id=task_id,
        pdf_path=pdf_path,
        format=format,
        options={
            "pages": pages,
            "quality": quality,
            "dpi": dpi,
            "preserve_layout": preserve_layout
        }
    )
    
    return {"task_id": task_id, "status": ConversionStatus.PENDING}


@router.get("/{task_id}", response_model=ConversionStatusResponse)
async def get_conversion_status(task_id: str):
    """
    Check the status of a conversion task.
    
    - **task_id**: The ID of the conversion task
    
    Returns the status of the task and download URL if completed.
    """
    # Get task from database
    task = database.get_task(task_id)
    
    # Check if task exists
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create response
    response = {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "message": task.get("error_message"),
        "result_url": f"/api/v1/conversion/{task_id}/download" if task["status"] == ConversionStatus.COMPLETED else None,
        "expires_at": task["expires_at"]
    }
    
    return response


@router.get("/{task_id}/download")
async def download_converted_file(task_id: str):
    """
    Download the converted file.
    
    - **task_id**: The ID of the conversion task
    
    Returns the converted file.
    """
    # Get task from database
    task = database.get_task(task_id)
    
    # Check if task exists
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task is completed
    if task["status"] != ConversionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Conversion not completed yet")
    
    # Check if result file exists
    if not task["result_path"] or not os.path.exists(task["result_path"]):
        raise HTTPException(status_code=404, detail="Converted file not found")
    
    # Return the file
    return FileResponse(
        path=task["result_path"],
        filename=os.path.basename(task["result_path"]),
        media_type="application/octet-stream"
    )


@router.delete("/{task_id}")
async def cancel_conversion(task_id: str):
    """
    Cancel a conversion task.
    
    - **task_id**: The ID of the conversion task to cancel
    """
    # Get task from database
    task = database.get_task(task_id)
    
    # Check if task exists
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task can be cancelled
    if task["status"] in [ConversionStatus.COMPLETED, ConversionStatus.FAILED, ConversionStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Task already {task['status']}")
    
    # Cancel the task
    database.update_task_status(task_id, ConversionStatus.CANCELLED)
    
    return {"task_id": task_id, "status": ConversionStatus.CANCELLED}


@router.get("", response_model=list)
async def get_supported_formats():
    """
    Get information about supported conversion formats.
    
    Returns:
        A list of supported conversion formats and their capabilities.
    """
    formats = [
        {
            "format": ConversionFormat.DOCX,
            "name": "Microsoft Word Document",
            "extension": ".docx",
            "description": "Convert PDF to editable Word document with layout preservation.",
            "options": [
                {"name": "pages", "type": "string", "description": "Specific pages to convert (e.g., '1,3-5,7')"},
                {"name": "preserve_layout", "type": "boolean", "description": "Whether to preserve the original layout"}
            ],
            "available": True
        },
        {
            "format": ConversionFormat.JPEG,
            "name": "JPEG Image",
            "extension": ".jpeg",
            "description": "Convert PDF pages to high-quality JPEG images.",
            "options": [
                {"name": "pages", "type": "string", "description": "Specific pages to convert (e.g., '1,3-5,7')"},
                {"name": "quality", "type": "integer", "description": "Image quality (1-100)"},
                {"name": "dpi", "type": "integer", "description": "Resolution in dots per inch (72-600)"}
            ],
            "available": True
        },
        {
            "format": ConversionFormat.PPT,
            "name": "PowerPoint Presentation",
            "extension": ".pptx",
            "description": "Convert PDF to PowerPoint presentation with text and images.",
            "options": [
                {"name": "pages", "type": "string", "description": "Specific pages to convert (e.g., '1,3-5,7')"}
            ],
            "available": True
        },
        {
            "format": ConversionFormat.HTML,
            "name": "HTML Webpage",
            "extension": ".html",
            "description": "Convert PDF to HTML with layout preservation and embedded images.",
            "options": [
                {"name": "pages", "type": "string", "description": "Specific pages to convert (e.g., '1,3-5,7')"},
                {"name": "preserve_layout", "type": "boolean", "description": "Whether to preserve the original layout"}
            ],
            "available": True
        }
    ]
    
    return formats


@router.post("/validate")
async def validate_pdf(file: UploadFile = File(...)):
    """
    Validate a PDF file and return information about it.
    
    - **file**: The PDF file to validate
    
    Returns:
        Information about the PDF file, such as number of pages and file size.
    """
    # Check file extension
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save to a temporary file
    temp_dir = os.path.join(settings.TEMP_DIR, "validate")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"temp_{uuid.uuid4()}.pdf")
    
    try:
        # Read and save file
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Check file size
        file_size = os.path.getsize(temp_path)
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds the maximum allowed size of {settings.MAX_FILE_SIZE/1024/1024:.1f} MB"
            )
        
        # Validate PDF and get information
        import fitz  # PyMuPDF
        try:
            pdf = fitz.open(temp_path)
            page_count = pdf.page_count
            
            # Get metadata
            metadata = pdf.metadata
            title = metadata.get("title", "")
            author = metadata.get("author", "")
            subject = metadata.get("subject", "")
            
            # Get basic statistics
            has_text = any(page.get_text().strip() for page in pdf)
            image_count = sum(len(page.get_images()) for page in pdf)
            
            pdf.close()
            
            return {
                "valid": True,
                "file_name": file.filename,
                "file_size": file_size,
                "file_size_human": f"{file_size/1024/1024:.2f} MB",
                "page_count": page_count,
                "metadata": {
                    "title": title,
                    "author": author,
                    "subject": subject
                },
                "has_text": has_text,
                "image_count": image_count
            }
            
        except Exception as e:
            # Invalid PDF
            raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")
            
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def cleanup_expired_tasks():
    """Remove expired conversion tasks and files."""
    # Get expired tasks from database
    expired_tasks = database.get_expired_tasks()
    
    for task in expired_tasks:
        task_id = task["task_id"]
        
        # Remove task data
        task_dir = os.path.join(settings.TEMP_DIR, task_id)
        if os.path.exists(task_dir):
            try:
                shutil.rmtree(task_dir)
                logger.info(f"Removed expired task directory: {task_dir}")
            except Exception as e:
                logger.error(f"Error removing task directory {task_dir}: {str(e)}")
        
        # Remove task from database
        database.delete_task(task_id)
        logger.info(f"Removed expired task: {task_id}")
