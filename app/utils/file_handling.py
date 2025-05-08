"""
File handling utilities for PDF Converter API
This module provides functions for handling file operations, validation, and cleanup.
"""

import os
import shutil
import tempfile
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def validate_pdf_file(file_path: str) -> bool:
    """
    Validate that a file is a valid PDF file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if the file is a valid PDF, False otherwise
    """
    # Basic validation - check extension and file existence
    if not file_path.lower().endswith('.pdf'):
        return False
        
    if not os.path.exists(file_path):
        return False
        
    # Check if file is too large
    if os.path.getsize(file_path) > settings.MAX_FILE_SIZE:
        return False
        
    # Add more sophisticated PDF validation using PyMuPDF
    try:
        import fitz  # PyMuPDF
        pdf = fitz.open(file_path)
        pdf.close()
        return True
    except Exception as e:
        logger.error(f"Error validating PDF file: {str(e)}")
        return False


def create_temp_dir() -> str:
    """
    Create a temporary directory for file processing.
    
    Returns:
        Path to the created directory
    """
    # Use the configured temp directory from settings
    base_temp_dir = settings.TEMP_DIR
    
    # Create the base temp directory if it doesn't exist
    os.makedirs(base_temp_dir, exist_ok=True)
    
    # Create a unique subdirectory using UUID
    temp_dir = os.path.join(base_temp_dir, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    
    logger.info(f"Created temporary directory: {temp_dir}")
    return temp_dir


def save_uploaded_file(file_content: bytes, file_name: str, directory: Optional[str] = None) -> str:
    """
    Save an uploaded file to disk.
    
    Args:
        file_content: The binary content of the file
        file_name: Name of the file
        directory: Directory to save the file (if None, uses a new temp directory)
        
    Returns:
        Path to the saved file
    """
    # Create directory if not provided
    if directory is None:
        directory = create_temp_dir()
    else:
        os.makedirs(directory, exist_ok=True)
    
    # Generate a safe filename
    safe_filename = os.path.basename(file_name)
    file_path = os.path.join(directory, safe_filename)
    
    # Write the file to disk
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    logger.info(f"Saved uploaded file to: {file_path}")
    return file_path


def cleanup_expired_files(max_age_hours: int = 24):
    """
    Delete temporary files that are older than the specified age.
    
    Args:
        max_age_hours: Maximum age of files in hours before deletion
    """
    base_temp_dir = settings.TEMP_DIR
    if not os.path.exists(base_temp_dir):
        return
        
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    # Walk through the temp directory
    for root, dirs, files in os.walk(base_temp_dir):
        # Delete old files
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff_time:
                    os.remove(file_path)
                    logger.info(f"Deleted expired file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {str(e)}")
        
        # Delete empty directories
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            try:
                # Check if directory is empty
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logger.info(f"Deleted empty directory: {dir_path}")
            except Exception as e:
                logger.error(f"Error deleting directory {dir_path}: {str(e)}")
