"""
PDF to DOCX conversion service
This module handles the conversion of PDF files to DOCX format using pdf2docx library.
"""

import os
import logging
from pdf2docx import Converter
from typing import Optional, List

logger = logging.getLogger(__name__)

class PDFToDocxConverter:
    """Handles conversion of PDF files to DOCX format."""
    
    def __init__(self, preserve_layout: bool = True):
        """
        Initialize the PDF to DOCX converter.
        
        Args:
            preserve_layout: Whether to preserve the original PDF layout in the DOCX file.
        """
        self.preserve_layout = preserve_layout
    
    def convert(
        self, 
        pdf_path: str, 
        output_path: Optional[str] = None,
        pages: Optional[List[int]] = None
    ) -> str:
        """
        Convert a PDF file to DOCX format.
        
        Args:
            pdf_path: Path to the PDF file
            output_path: Path for the output DOCX file (if None, uses the same filename with .docx extension)
            pages: Specific pages to convert (if None, converts all pages)
            
        Returns:
            Path to the generated DOCX file
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # If output path is not provided, use the same name with .docx extension
        if output_path is None:
            output_path = os.path.splitext(pdf_path)[0] + ".docx"
            
        try:
            # Create Converter instance with a timeout
            cv = Converter(pdf_path)
            
            # Set specific starting and ending pages if needed
            start_page = None
            end_page = None
            
            if pages and len(pages) > 0:
                pages_sorted = sorted(pages)
                # Convert specific pages
                cv.convert(output_path, pages=pages)
            else:
                # Convert all pages - more efficient than start/end for full document
                cv.convert(output_path)
                
            # Close the converter
            cv.close()
            
            logger.info(f"Successfully converted {pdf_path} to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting PDF to DOCX: {str(e)}")
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


def convert_pdf_to_docx(
    pdf_path: str,
    output_path: Optional[str] = None,
    page_string: Optional[str] = None,
    preserve_layout: bool = True
) -> str:
    """
    Convenience function to convert a PDF file to DOCX format.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path for the output DOCX file
        page_string: String representation of page ranges (e.g., "1,3-5,7")
        preserve_layout: Whether to preserve the original layout
        
    Returns:
        Path to the generated DOCX file
    """
    # Create converter instance
    converter = PDFToDocxConverter(preserve_layout=preserve_layout)
    
    # Parse page ranges if provided
    pages = None
    if page_string:
        pages = converter.parse_page_range(page_string)
        
    # Convert the PDF to DOCX
    return converter.convert(pdf_path, output_path, pages)
