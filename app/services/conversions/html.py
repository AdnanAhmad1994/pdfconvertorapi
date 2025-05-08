"""
PDF to HTML conversion service
This module handles the conversion of PDF files to HTML format using PyMuPDF.
"""

import os
import logging
import fitz  # PyMuPDF
import tempfile
import shutil
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

class PDFToHtmlConverter:
    """Handles conversion of PDF files to HTML format."""
    
    def __init__(self, preserve_layout: bool = True):
        """
        Initialize the PDF to HTML converter.
        
        Args:
            preserve_layout: Whether to preserve the original PDF layout in the HTML file.
        """
        self.preserve_layout = preserve_layout
    
    def convert(
        self, 
        pdf_path: str, 
        output_path: Optional[str] = None,
        pages: Optional[List[int]] = None
    ) -> str:
        """
        Convert a PDF file to HTML format.
        
        Args:
            pdf_path: Path to the PDF file
            output_path: Path for the output HTML file (if None, uses the same filename with .html extension)
            pages: Specific pages to convert (if None, converts all pages)
            
        Returns:
            Path to the generated HTML file
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # If output path is not provided, use the same name with .html extension
        if output_path is None:
            output_path = os.path.splitext(pdf_path)[0] + ".html"
            
        # Create output directory for HTML and assets
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create assets directory
        assets_dir = os.path.join(output_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        try:
            # Open the PDF file
            pdf = fitz.open(pdf_path)
            
            # Determine which pages to convert
            page_indices = list(range(pdf.page_count))
            if pages is not None:
                # Filter to only the requested pages (convert from 1-based to 0-based indices)
                page_indices = [i-1 for i in pages if 0 <= i-1 < pdf.page_count]
            
            # Start building the HTML content
            html_content = []
            html_content.append('<!DOCTYPE html>')
            html_content.append('<html lang="en">')
            html_content.append('<head>')
            html_content.append('    <meta charset="UTF-8">')
            html_content.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
            html_content.append(f'    <title>{os.path.basename(pdf_path)}</title>')
            html_content.append('    <style>')
            html_content.append('        body { font-family: Arial, sans-serif; line-height: 1.6; }')
            html_content.append('        .page { margin-bottom: 20px; padding: 20px; border: 1px solid #ddd; }')
            html_content.append('        .page-number { font-size: 0.8em; text-align: center; color: #777; }')
            
            if self.preserve_layout:
                html_content.append('        .pdf-text { position: absolute; }')
                html_content.append('        .pdf-image { position: absolute; }')
                html_content.append('        .page { position: relative; }')
            
            html_content.append('    </style>')
            html_content.append('</head>')
            html_content.append('<body>')
            
            # Process each page
            for i, page_idx in enumerate(page_indices):
                # Get the PDF page
                pdf_page = pdf.load_page(page_idx)
                
                # Page dimensions
                page_width = pdf_page.rect.width
                page_height = pdf_page.rect.height
                
                # Start page div
                html_content.append(f'<div class="page" id="page-{i+1}" style="width: {page_width}px; height: {page_height}px;">')
                
                if self.preserve_layout:
                    # Get text with position information
                    text_blocks = pdf_page.get_text("dict")["blocks"]
                    
                    # Process text blocks
                    for block in text_blocks:
                        if block.get("type") == 0:  # Text block
                            for line in block.get("lines", []):
                                for span in line.get("spans", []):
                                    text = span.get("text", "").strip()
                                    if text:
                                        font_size = span.get("size", 12)
                                        font_color = f"#{span.get('color', 0):06x}"
                                        x = span.get("origin")[0]
                                        y = span.get("origin")[1]
                                        
                                        # Add text with positioning
                                        style = f"left: {x}px; top: {y-font_size}px; font-size: {font_size}px; color: {font_color};"
                                        html_content.append(f'<div class="pdf-text" style="{style}">{text}</div>')
                    
                    # Extract and save images
                    image_list = pdf_page.get_images(full=True)
                    for img_idx, img_info in enumerate(image_list):
                        xref = img_info[0]
                        base_image = pdf.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        image_filename = f"page{page_idx+1}_img{img_idx+1}.{image_ext}"
                        image_path = os.path.join(assets_dir, image_filename)
                        
                        # Save the image
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # Get image position (this is simplified and may need adjustment)
                        # In a real implementation, you'd need to calculate exact positions
                        img_rect = pdf_page.get_image_bbox(img_info)
                        x, y = img_rect.x0, img_rect.y0
                        width, height = img_rect.width, img_rect.height
                        
                        # Add image with positioning
                        style = f"left: {x}px; top: {y}px; width: {width}px; height: {height}px;"
                        html_content.append(f'<img class="pdf-image" src="assets/{image_filename}" style="{style}" alt="Image from PDF" />')
                
                else:
                    # Simplified conversion without layout preservation
                    # Just extract text
                    text = pdf_page.get_text()
                    html_content.append(f'<pre>{text}</pre>')
                    
                    # Extract and save images
                    image_list = pdf_page.get_images(full=True)
                    for img_idx, img_info in enumerate(image_list):
                        xref = img_info[0]
                        base_image = pdf.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        image_filename = f"page{page_idx+1}_img{img_idx+1}.{image_ext}"
                        image_path = os.path.join(assets_dir, image_filename)
                        
                        # Save the image
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # Add image without positioning
                        html_content.append(f'<img src="assets/{image_filename}" alt="Image from PDF" />')
                
                # Add page number
                html_content.append(f'<div class="page-number">Page {page_idx + 1}</div>')
                
                # End page div
                html_content.append('</div>')
            
            # Finish HTML
            html_content.append('</body>')
            html_content.append('</html>')
            
            # Write the HTML file
            with open(output_path, 'w', encoding='utf-8') as html_file:
                html_file.write('\n'.join(html_content))
            
            # Close the PDF file
            pdf.close()
            
            logger.info(f"Successfully converted {pdf_path} to {output_path}")
            
            # For HTML, we need to return both the HTML file and the assets directory
            # Since our API expects a single file, create a zip file with everything
            zip_path = os.path.splitext(output_path)[0] + ".zip"
            
            # Get the parent directory of the output file
            output_parent_dir = os.path.dirname(output_path)
            
            # Get the filename without extension for the HTML file
            html_name = os.path.splitext(os.path.basename(output_path))[0]
            
            # Create a zip file
            import zipfile
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Add the HTML file
                zipf.write(output_path, os.path.basename(output_path))
                
                # Add all files from the assets directory
                for root, _, files in os.walk(assets_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate the arcname (path within the zip)
                        arcname = os.path.join("assets", os.path.basename(file_path))
                        zipf.write(file_path, arcname)
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Error converting PDF to HTML: {str(e)}")
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


def convert_pdf_to_html(
    pdf_path: str,
    output_path: Optional[str] = None,
    page_string: Optional[str] = None,
    preserve_layout: bool = True
) -> str:
    """
    Convenience function to convert a PDF file to HTML format.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path for the output HTML file
        page_string: String representation of page ranges (e.g., "1,3-5,7")
        preserve_layout: Whether to preserve the original layout
        
    Returns:
        Path to the generated ZIP file containing HTML and assets
    """
    # Create converter instance
    converter = PDFToHtmlConverter(preserve_layout=preserve_layout)
    
    # Parse page ranges if provided
    pages = None
    if page_string:
        pages = converter.parse_page_range(page_string)
        
    # Convert the PDF to HTML
    return converter.convert(pdf_path, output_path, pages)
