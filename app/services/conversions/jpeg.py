"""
PDF to JPEG conversion service
This module handles the conversion of PDF files to JPEG format using pdf2image library.
"""

import os
import logging
from pdf2image import convert_from_path
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

class PDFToJpegConverter:
    """Handles conversion of PDF files to JPEG format."""
    
    def __init__(
        self, 
        dpi: int = 200, 
        quality: int = 90,
        output_folder: Optional[str] = None,
        poppler_path: Optional[str] = None
    ):
        """
        Initialize the PDF to JPEG converter.
        
        Args:
            dpi: Resolution in dots per inch
            quality: Image quality (1-100)
            output_folder: Folder to save images (if None, uses a temporary folder)
            poppler_path: Path to the Poppler binaries
        """
        self.dpi = dpi
        self.quality = quality
        self.output_folder = output_folder
        self.poppler_path = poppler_path  # Leave this as None to let the library find Poppler automatically
    
    def convert(
        self, 
        pdf_path: str,
        pages: Optional[List[int]] = None,
        output_folder: Optional[str] = None,
        output_prefix: Optional[str] = None
    ) -> List[str]:
        """
        Convert a PDF file to JPEG images.
        
        Args:
            pdf_path: Path to the PDF file
            pages: Specific pages to convert (if None, converts all pages)
            output_folder: Folder to save images (overrides the one set in constructor)
            output_prefix: Prefix for output filenames
            
        Returns:
            List of paths to the generated JPEG files
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Use provided output folder or the one from constructor or create a new one
        folder = output_folder or self.output_folder
        if folder is None:
            # Create a directory next to the PDF file
            folder = os.path.join(os.path.dirname(pdf_path), "jpeg_output")
        
        os.makedirs(folder, exist_ok=True)
        
        # Set output prefix based on PDF filename if not provided
        if output_prefix is None:
            output_prefix = os.path.splitext(os.path.basename(pdf_path))[0]
        
        try:
            # Define page numbers
            first_page = None
            last_page = None
            
            if pages:
                # Sort pages to get first and last
                sorted_pages = sorted(pages)
                first_page = sorted_pages[0]
                last_page = sorted_pages[-1]
            
            # Convert PDF pages to JPEG images
            convert_args = {
                "dpi": self.dpi,
                "output_folder": folder,
                "fmt": "jpeg",
                "output_file": output_prefix,
                "paths_only": True,
                "thread_count": 4,  # Optimize for multicore systems
                "jpegopt": {"quality": self.quality, "progressive": True, "optimize": True},
                "first_page": first_page,
                "last_page": last_page
            }
            
            # Only add poppler_path if it's specified
            if self.poppler_path:
                convert_args["poppler_path"] = self.poppler_path
                
            images = convert_from_path(pdf_path, **convert_args)
            
            # Filter specific pages if needed
            image_paths = []
            if pages:
                # Check if we need to filter the images (when specific pages are not sequential)
                pdf_page_indices = [p - 1 for p in pages]  # Convert to 0-based indices
                
                # Get list of all generated images
                all_images = sorted(images)
                
                # Keep only requested pages
                for idx, img_path in enumerate(all_images):
                    if idx in pdf_page_indices:
                        image_paths.append(img_path)
            else:
                # Use all images
                image_paths = images
            
            logger.info(f"Successfully converted {pdf_path} to {len(image_paths)} JPEG images")
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF to JPEG: {str(e)}")
            raise
    
    @staticmethod
    def parse_page_range(page_string: str) -> List[int]:
        """
        Parse a page range string (e.g., "1,3-5,7") into a list of page numbers.
        
        Args:
            page_string: String representation of page ranges
            
        Returns:
            List of page numbers
        """
        if not page_string:
            return None
            
        pages = []
        parts = page_string.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Handle page range (e.g., "3-5")
                start, end = map(int, part.split('-'))
                pages.extend(range(start, end + 1))
            else:
                # Handle single page
                pages.append(int(part))
                
        return pages


def convert_pdf_to_jpeg(
    pdf_path: str,
    output_folder: Optional[str] = None,
    output_prefix: Optional[str] = None,
    page_string: Optional[str] = None,
    dpi: int = 200,
    quality: int = 90,
    poppler_path: Optional[str] = None
) -> List[str]:
    """
    Convenience function to convert a PDF file to JPEG images.
    
    Args:
        pdf_path: Path to the PDF file
        output_folder: Folder to save images
        output_prefix: Prefix for output filenames
        page_string: String representation of page ranges (e.g., "1,3-5,7")
        dpi: Resolution in dots per inch
        quality: Image quality (1-100)
        poppler_path: Path to the Poppler binaries
        
    Returns:
        List of paths to the generated JPEG files
    """
    # Create converter instance
    converter = PDFToJpegConverter(dpi=dpi, quality=quality, output_folder=output_folder, poppler_path=poppler_path)
    
    # Parse page ranges if provided
    pages = None
    if page_string:
        pages = converter.parse_page_range(page_string)
        
    # Convert the PDF to JPEG images
    return converter.convert(pdf_path, pages, output_folder, output_prefix)
