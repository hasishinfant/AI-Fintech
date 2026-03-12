"""
Document Parser Module

This module provides document parsing capabilities including PDF parsing,
OCR for scanned documents, and document type detection.

Requirements: 1.4, 1.5
"""

from typing import Dict, Any, Optional, BinaryIO
from pathlib import Path
import io
import logging

import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Handles parsing of various document formats with OCR support.
    
    This class provides methods to:
    - Parse PDF documents and extract text content
    - Apply OCR to scanned documents
    - Detect document types based on content
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the DocumentParser.
        
        Args:
            tesseract_cmd: Optional path to tesseract executable.
                          If not provided, assumes tesseract is in PATH.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self.supported_formats = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Parse PDF and extract text content.
        
        This method extracts text from PDF files using pdfplumber. If the PDF
        contains scanned images with no extractable text, it will be detected
        and flagged for OCR processing.
        
        Args:
            file_path: Path to the PDF file to parse
            
        Returns:
            Dictionary containing:
                - text: Extracted text content from all pages
                - pages: List of text content per page
                - page_count: Total number of pages
                - is_scanned: Boolean indicating if document appears to be scanned
                - metadata: PDF metadata (author, title, etc.)
                
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid PDF
            
        Requirements: 1.4
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path_obj.suffix.lower() != '.pdf':
            raise ValueError(f"File is not a PDF: {file_path}")
        
        try:
            with pdfplumber.open(file_path) as pdf:
                pages_text = []
                total_text = []
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    pages_text.append({
                        'page_number': page_num,
                        'text': page_text,
                        'char_count': len(page_text.strip())
                    })
                    total_text.append(page_text)
                
                # Combine all text
                full_text = "\n\n".join(total_text)
                
                # Detect if document is scanned (very little or no text extracted)
                avg_chars_per_page = sum(p['char_count'] for p in pages_text) / len(pages_text) if pages_text else 0
                is_scanned = avg_chars_per_page < 50  # Threshold for scanned documents
                
                # Extract metadata
                metadata = pdf.metadata or {}
                
                result = {
                    'text': full_text,
                    'pages': pages_text,
                    'page_count': len(pdf.pages),
                    'is_scanned': is_scanned,
                    'metadata': {
                        'author': metadata.get('Author', ''),
                        'title': metadata.get('Title', ''),
                        'subject': metadata.get('Subject', ''),
                        'creator': metadata.get('Creator', ''),
                        'producer': metadata.get('Producer', ''),
                        'creation_date': metadata.get('CreationDate', ''),
                    }
                }
                
                logger.info(f"Parsed PDF: {file_path}, pages: {result['page_count']}, "
                           f"is_scanned: {is_scanned}, chars: {len(full_text)}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def apply_ocr(self, image_data: bytes, language: str = 'eng') -> str:
        """
        Apply OCR to scanned document images.
        
        This method uses pytesseract to extract text from image data.
        Supports multiple languages and can handle various image formats.
        
        Args:
            image_data: Binary image data (PNG, JPEG, TIFF, etc.)
            language: Tesseract language code (default: 'eng' for English)
                     Can use 'eng+hin' for English and Hindi
            
        Returns:
            Extracted text content from the image
            
        Raises:
            ValueError: If image data is invalid or OCR fails
            
        Requirements: 1.5
        """
        if not image_data:
            raise ValueError("Image data is empty")
        
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Apply OCR
            text = pytesseract.image_to_string(image, lang=language)
            
            logger.info(f"OCR completed: extracted {len(text)} characters")
            
            return text
            
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise ValueError(f"Failed to apply OCR: {str(e)}")
    
    def parse_pdf_with_ocr(self, file_path: str, language: str = 'eng') -> Dict[str, Any]:
        """
        Parse PDF and apply OCR if needed.
        
        This method first attempts to extract text from the PDF. If the document
        appears to be scanned (minimal text extracted), it converts pages to
        images and applies OCR.
        
        Args:
            file_path: Path to the PDF file
            language: Tesseract language code for OCR
            
        Returns:
            Dictionary with same structure as parse_pdf(), but with OCR-extracted
            text if the document was scanned
            
        Requirements: 1.4, 1.5
        """
        # First, try regular PDF parsing
        result = self.parse_pdf(file_path)
        
        # If document is scanned, apply OCR
        if result['is_scanned']:
            logger.info(f"Document appears to be scanned, applying OCR: {file_path}")
            
            try:
                # Convert PDF pages to images
                images = convert_from_path(file_path, dpi=300)
                
                ocr_pages = []
                ocr_text_parts = []
                
                for page_num, image in enumerate(images, start=1):
                    # Convert PIL Image to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    # Apply OCR
                    page_text = self.apply_ocr(img_bytes, language=language)
                    
                    ocr_pages.append({
                        'page_number': page_num,
                        'text': page_text,
                        'char_count': len(page_text.strip())
                    })
                    ocr_text_parts.append(page_text)
                
                # Update result with OCR text
                result['text'] = "\n\n".join(ocr_text_parts)
                result['pages'] = ocr_pages
                result['ocr_applied'] = True
                
                logger.info(f"OCR completed for {len(images)} pages, "
                           f"extracted {len(result['text'])} characters")
                
            except Exception as e:
                logger.error(f"OCR processing failed: {str(e)}")
                result['ocr_applied'] = False
                result['ocr_error'] = str(e)
        else:
            result['ocr_applied'] = False
        
        return result
    
    def detect_document_type(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Detect document type based on content and metadata.
        
        This method analyzes the extracted text and metadata to identify
        the type of financial document (GST return, ITR, bank statement, etc.).
        
        Args:
            text: Extracted text content from the document
            metadata: Optional metadata from the document
            
        Returns:
            Document type as string. Possible values:
                - 'gst_return': GST return (GSTR-2A, GSTR-3B)
                - 'itr': Income Tax Return
                - 'bank_statement': Bank statement
                - 'annual_report': Annual report with financial statements
                - 'board_minutes': Board meeting minutes
                - 'rating_report': Credit rating report
                - 'mca_filing': MCA filing document
                - 'unknown': Unable to determine type
                
        Requirements: 1.4
        """
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # GST Return detection
        gst_keywords = ['gstr', 'gst return', 'gstin', 'goods and services tax']
        if any(keyword in text_lower for keyword in gst_keywords):
            if 'gstr-2a' in text_lower or 'gstr 2a' in text_lower:
                return 'gst_return_2a'
            elif 'gstr-3b' in text_lower or 'gstr 3b' in text_lower:
                return 'gst_return_3b'
            return 'gst_return'
        
        # Income Tax Return detection
        itr_keywords = ['income tax return', 'itr-', 'acknowledgement number', 'pan:', 'assessment year']
        if any(keyword in text_lower for keyword in itr_keywords):
            return 'itr'
        
        # Bank Statement detection
        bank_keywords = ['bank statement', 'account statement', 'opening balance', 'closing balance', 
                        'transaction date', 'debit', 'credit', 'ifsc']
        if sum(keyword in text_lower for keyword in bank_keywords) >= 3:
            return 'bank_statement'
        
        # Annual Report detection
        annual_report_keywords = ['balance sheet', 'profit and loss', 'cash flow statement', 
                                 'annual report', 'financial statements', 'auditor']
        if sum(keyword in text_lower for keyword in annual_report_keywords) >= 2:
            return 'annual_report'
        
        # Board Minutes detection
        board_keywords = ['board meeting', 'board of directors', 'minutes of meeting', 
                         'resolution', 'quorum']
        if sum(keyword in text_lower for keyword in board_keywords) >= 2:
            return 'board_minutes'
        
        # Rating Report detection
        rating_keywords = ['credit rating', 'rating agency', 'crisil', 'icra', 'care ratings', 
                          'rating rationale']
        if any(keyword in text_lower for keyword in rating_keywords):
            return 'rating_report'
        
        # MCA Filing detection
        mca_keywords = ['ministry of corporate affairs', 'mca', 'cin:', 'form no.', 
                       'registrar of companies']
        if sum(keyword in text_lower for keyword in mca_keywords) >= 2:
            return 'mca_filing'
        
        logger.warning(f"Unable to detect document type from content")
        return 'unknown'
    
    def parse_document(self, file_path: str, apply_ocr_if_needed: bool = True, 
                      language: str = 'eng') -> Dict[str, Any]:
        """
        Parse document with automatic type detection and OCR if needed.
        
        This is the main entry point for document parsing. It handles:
        - PDF parsing with optional OCR
        - Document type detection
        - Comprehensive result packaging
        
        Args:
            file_path: Path to the document file
            apply_ocr_if_needed: Whether to apply OCR for scanned documents
            language: Language code for OCR
            
        Returns:
            Dictionary containing:
                - text: Extracted text content
                - pages: Per-page text content
                - page_count: Number of pages
                - is_scanned: Whether document was scanned
                - ocr_applied: Whether OCR was used
                - document_type: Detected document type
                - metadata: Document metadata
                - file_path: Original file path
                
        Requirements: 1.4, 1.5
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Parse PDF (with OCR if needed)
        if apply_ocr_if_needed:
            result = self.parse_pdf_with_ocr(file_path, language=language)
        else:
            result = self.parse_pdf(file_path)
        
        # Detect document type
        document_type = self.detect_document_type(result['text'], result.get('metadata'))
        result['document_type'] = document_type
        result['file_path'] = str(file_path)
        
        logger.info(f"Document parsing complete: {file_path}, type: {document_type}")
        
        return result
