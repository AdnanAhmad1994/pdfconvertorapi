"""
Conversion processing module for the PDF Converter API.
Contains the asynchronous task processing logic with timeout support.
"""

import os
import asyncio
import zipfile
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models.conversion import ConversionFormat, ConversionStatus
from app.services.conversions import docx, jpeg, ppt, html
from app.db import database
from app.core.config import settings

logger = logging.getLogger(__name__)

async def process_conversion(task_id: str, pdf_path: str, format: ConversionFormat, options: dict):
    """
    Process the conversion task in the background with timeout support.
    
    Args:
        task_id: ID of the conversion task
        pdf_path: Path to the PDF file
        format: Target format
        options: Conversion options
    """
    # Get task from database
    task = database.get_task(task_id)
    
    if task is None:
        logger.error(f"Task {task_id} not found")
        return
    
    try:
        # Update task status
        database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=10.0)
        
        # Get options
        pages = options.get("pages")
        quality = options.get("quality", 90)
        dpi = options.get("dpi", 300)
        preserve_layout = options.get("preserve_layout", True)
        
        # Generate output path
        output_dir = os.path.join(settings.TEMP_DIR, task_id)
        file_base = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Set a timeout for conversion (5 minutes)
        timeout = 300  # seconds
        
        # Perform conversion based on format with timeout
        try:
            if format == ConversionFormat.DOCX:
                output_path = os.path.join(output_dir, f"{file_base}.docx")
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=30.0)
                
                # Run in a separate thread with timeout
                result_path = await asyncio.to_thread(
                    docx.convert_pdf_to_docx,
                    pdf_path=pdf_path,
                    output_path=output_path,
                    page_string=pages,
                    preserve_layout=preserve_layout
                )
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=90.0)
                
            elif format == ConversionFormat.JPEG:
                output_dir = os.path.join(output_dir, f"{file_base}_jpeg")
                os.makedirs(output_dir, exist_ok=True)
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=30.0)
                
                # Run in a separate thread with timeout
                result_paths = await asyncio.to_thread(
                    jpeg.convert_pdf_to_jpeg,
                    pdf_path=pdf_path,
                    output_folder=output_dir,
                    page_string=pages,
                    quality=quality,
                    dpi=dpi
                )
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=90.0)
                
                # For JPEGs, create a zip file with all images
                if len(result_paths) > 1:
                    zip_path = os.path.join(output_dir, f"{file_base}.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for img_path in result_paths:
                            zipf.write(img_path, os.path.basename(img_path))
                    result_path = zip_path
                else:
                    result_path = result_paths[0]
                    
            elif format == ConversionFormat.PPT:
                output_path = os.path.join(output_dir, f"{file_base}.pptx")
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=30.0)
                
                # Run in a separate thread with timeout
                result_path = await asyncio.to_thread(
                    ppt.convert_pdf_to_ppt,
                    pdf_path=pdf_path,
                    output_path=output_path,
                    page_string=pages
                )
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=90.0)
                
            elif format == ConversionFormat.HTML:
                output_path = os.path.join(output_dir, f"{file_base}.html")
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=30.0)
                
                # Run in a separate thread with timeout
                result_path = await asyncio.to_thread(
                    html.convert_pdf_to_html,
                    pdf_path=pdf_path,
                    output_path=output_path,
                    page_string=pages,
                    preserve_layout=preserve_layout
                )
                database.update_task_status(task_id, ConversionStatus.PROCESSING, progress=90.0)
                
            # Update task status on success
            database.update_task_status(
                task_id, 
                ConversionStatus.COMPLETED, 
                progress=100.0, 
                result_path=result_path
            )
            
        except asyncio.TimeoutError:
            # Handle timeout
            logger.error(f"Conversion timeout for task {task_id}")
            database.update_task_status(
                task_id, 
                ConversionStatus.FAILED, 
                progress=0.0, 
                error_message="Conversion timed out after 5 minutes. The PDF may be too large or complex."
            )
            
    except Exception as e:
        # Update task status on error
        logger.error(f"Error processing conversion task {task_id}: {str(e)}")
        database.update_task_status(
            task_id, 
            ConversionStatus.FAILED, 
            progress=0.0, 
            error_message=str(e)
        )
