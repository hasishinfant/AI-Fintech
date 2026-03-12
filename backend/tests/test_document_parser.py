"""
Unit tests for DocumentParser class

Tests cover:
- PDF parsing functionality
- OCR application
- Document type detection
- Error handling
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from app.services.data_ingestor.document_parser import DocumentParser


class TestDocumentParser:
    """Test suite for DocumentParser class"""
    
    @pytest.fixture
    def parser(self):
        """Create a DocumentParser instance for testing"""
        return DocumentParser()
    
    def test_init_default(self):
        """Test DocumentParser initialization with default settings"""
        parser = DocumentParser()
        assert parser.supported_formats == {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    def test_init_with_tesseract_cmd(self):
        """Test DocumentParser initialization with custom tesseract command"""
        with patch('pytesseract.pytesseract') as mock_pytesseract:
            parser = DocumentParser(tesseract_cmd='/usr/bin/tesseract')
            assert mock_pytesseract.tesseract_cmd == '/usr/bin/tesseract'
    
    @patch('pdfplumber.open')
    def test_parse_pdf_success(self, mock_pdfplumber, parser):
        """Test successful PDF parsing with extractable text"""
        # Mock PDF with text content (needs >50 chars to not be detected as scanned)
        mock_page = Mock()
        mock_page.extract_text.return_value = "This is page 1 content with sufficient text to avoid scanned detection threshold."
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {
            'Author': 'Test Author',
            'Title': 'Test Document',
            'CreationDate': '2024-01-01'
        }
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        
        mock_pdfplumber.return_value = mock_pdf
        
        # Create a temporary file path (doesn't need to exist due to mocking)
        with patch('pathlib.Path.exists', return_value=True):
            result = parser.parse_pdf('test.pdf')
        
        assert result['text'] == "This is page 1 content with sufficient text to avoid scanned detection threshold."
        assert result['page_count'] == 1
        assert result['is_scanned'] is False
        assert len(result['pages']) == 1
        assert result['pages'][0]['page_number'] == 1
        assert result['metadata']['author'] == 'Test Author'
    
    @patch('pdfplumber.open')
    def test_parse_pdf_scanned_detection(self, mock_pdfplumber, parser):
        """Test detection of scanned PDFs with minimal text"""
        # Mock PDF with very little text (scanned document)
        mock_page = Mock()
        mock_page.extract_text.return_value = "abc"  # Very little text
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {}
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        
        mock_pdfplumber.return_value = mock_pdf
        
        with patch('pathlib.Path.exists', return_value=True):
            result = parser.parse_pdf('scanned.pdf')
        
        assert result['is_scanned'] is True
    
    def test_parse_pdf_file_not_found(self, parser):
        """Test error handling when PDF file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            parser.parse_pdf('nonexistent.pdf')
    
    def test_parse_pdf_invalid_format(self, parser):
        """Test error handling for non-PDF files"""
        with patch('pathlib.Path.exists', return_value=True):
            with pytest.raises(ValueError, match="File is not a PDF"):
                parser.parse_pdf('document.txt')
    
    @patch('pytesseract.image_to_string')
    @patch('PIL.Image.open')
    def test_apply_ocr_success(self, mock_image_open, mock_ocr, parser):
        """Test successful OCR application"""
        mock_image = Mock()
        mock_image_open.return_value = mock_image
        mock_ocr.return_value = "OCR extracted text"
        
        image_data = b"fake_image_data"
        result = parser.apply_ocr(image_data)
        
        assert result == "OCR extracted text"
        mock_ocr.assert_called_once_with(mock_image, lang='eng')
    
    @patch('pytesseract.image_to_string')
    @patch('PIL.Image.open')
    def test_apply_ocr_with_language(self, mock_image_open, mock_ocr, parser):
        """Test OCR with custom language"""
        mock_image = Mock()
        mock_image_open.return_value = mock_image
        mock_ocr.return_value = "Hindi and English text"
        
        image_data = b"fake_image_data"
        result = parser.apply_ocr(image_data, language='eng+hin')
        
        assert result == "Hindi and English text"
        mock_ocr.assert_called_once_with(mock_image, lang='eng+hin')
    
    def test_apply_ocr_empty_data(self, parser):
        """Test error handling for empty image data"""
        with pytest.raises(ValueError, match="Image data is empty"):
            parser.apply_ocr(b"")
    
    @patch('pytesseract.image_to_string')
    @patch('PIL.Image.open')
    def test_apply_ocr_failure(self, mock_image_open, mock_ocr, parser):
        """Test error handling when OCR fails"""
        mock_image_open.side_effect = Exception("Invalid image format")
        
        with pytest.raises(ValueError, match="Failed to apply OCR"):
            parser.apply_ocr(b"invalid_data")
    
    def test_detect_document_type_gst_return_2a(self, parser):
        """Test detection of GSTR-2A document"""
        text = "GSTR-2A Return for the month of January 2024. GSTIN: 29ABCDE1234F1Z5"
        result = parser.detect_document_type(text)
        assert result == 'gst_return_2a'
    
    def test_detect_document_type_gst_return_3b(self, parser):
        """Test detection of GSTR-3B document"""
        text = "GSTR-3B Summary Return. Goods and Services Tax. GSTIN: 29ABCDE1234F1Z5"
        result = parser.detect_document_type(text)
        assert result == 'gst_return_3b'
    
    def test_detect_document_type_itr(self, parser):
        """Test detection of Income Tax Return"""
        text = "Income Tax Return for Assessment Year 2023-24. PAN: ABCDE1234F. Acknowledgement Number: 123456789"
        result = parser.detect_document_type(text)
        assert result == 'itr'
    
    def test_detect_document_type_bank_statement(self, parser):
        """Test detection of bank statement"""
        text = """
        Bank Statement
        Account Statement for Account No: 1234567890
        Opening Balance: 100000
        Transaction Date | Description | Debit | Credit | Balance
        Closing Balance: 150000
        IFSC: SBIN0001234
        """
        result = parser.detect_document_type(text)
        assert result == 'bank_statement'
    
    def test_detect_document_type_annual_report(self, parser):
        """Test detection of annual report"""
        text = """
        Annual Report 2023
        Balance Sheet as on 31st March 2023
        Profit and Loss Statement
        Cash Flow Statement
        Auditor's Report
        """
        result = parser.detect_document_type(text)
        assert result == 'annual_report'
    
    def test_detect_document_type_board_minutes(self, parser):
        """Test detection of board minutes"""
        text = """
        Minutes of Board Meeting
        Board of Directors Meeting held on 15th January 2024
        Quorum was present
        Resolution passed
        """
        result = parser.detect_document_type(text)
        assert result == 'board_minutes'
    
    def test_detect_document_type_rating_report(self, parser):
        """Test detection of credit rating report"""
        text = "Credit Rating Report by CRISIL. Rating Rationale and Key Rating Drivers."
        result = parser.detect_document_type(text)
        assert result == 'rating_report'
    
    def test_detect_document_type_mca_filing(self, parser):
        """Test detection of MCA filing"""
        text = """
        Ministry of Corporate Affairs
        Form No. MGT-7
        CIN: U12345MH2020PTC123456
        Registrar of Companies, Maharashtra
        """
        result = parser.detect_document_type(text)
        assert result == 'mca_filing'
    
    def test_detect_document_type_unknown(self, parser):
        """Test unknown document type detection"""
        text = "This is some random text that doesn't match any document type."
        result = parser.detect_document_type(text)
        assert result == 'unknown'
    
    def test_detect_document_type_empty_text(self, parser):
        """Test document type detection with empty text"""
        result = parser.detect_document_type("")
        assert result == 'unknown'
    
    @patch('app.services.data_ingestor.document_parser.DocumentParser.parse_pdf')
    @patch('app.services.data_ingestor.document_parser.DocumentParser.detect_document_type')
    def test_parse_document_without_ocr(self, mock_detect, mock_parse_pdf, parser):
        """Test parse_document without OCR"""
        mock_parse_pdf.return_value = {
            'text': 'Test content',
            'pages': [{'page_number': 1, 'text': 'Test content', 'char_count': 12}],
            'page_count': 1,
            'is_scanned': False,
            'metadata': {},
            'ocr_applied': False
        }
        mock_detect.return_value = 'annual_report'
        
        with patch('pathlib.Path.exists', return_value=True):
            result = parser.parse_document('test.pdf', apply_ocr_if_needed=False)
        
        assert result['document_type'] == 'annual_report'
        assert result['file_path'] == 'test.pdf'
    
    @patch('app.services.data_ingestor.document_parser.convert_from_path')
    @patch('app.services.data_ingestor.document_parser.DocumentParser.apply_ocr')
    @patch('app.services.data_ingestor.document_parser.DocumentParser.parse_pdf')
    def test_parse_pdf_with_ocr_scanned_document(self, mock_parse_pdf, mock_apply_ocr, 
                                                  mock_convert, parser):
        """Test parse_pdf_with_ocr for scanned documents"""
        # Mock parse_pdf to return scanned document
        mock_parse_pdf.return_value = {
            'text': 'abc',
            'pages': [{'page_number': 1, 'text': 'abc', 'char_count': 3}],
            'page_count': 1,
            'is_scanned': True,
            'metadata': {}
        }
        
        # Mock image conversion
        mock_image = Mock()
        mock_convert.return_value = [mock_image]
        
        # Mock OCR
        mock_apply_ocr.return_value = "OCR extracted text from scanned page"
        
        with patch('pathlib.Path.exists', return_value=True):
            result = parser.parse_pdf_with_ocr('scanned.pdf')
        
        assert result['ocr_applied'] is True
        assert result['text'] == "OCR extracted text from scanned page"
        assert len(result['pages']) == 1
        mock_apply_ocr.assert_called_once()
    
    @patch('app.services.data_ingestor.document_parser.DocumentParser.parse_pdf')
    def test_parse_pdf_with_ocr_regular_document(self, mock_parse_pdf, parser):
        """Test parse_pdf_with_ocr for regular (non-scanned) documents"""
        mock_parse_pdf.return_value = {
            'text': 'Regular text content with sufficient characters',
            'pages': [{'page_number': 1, 'text': 'Regular text content', 'char_count': 100}],
            'page_count': 1,
            'is_scanned': False,
            'metadata': {}
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            result = parser.parse_pdf_with_ocr('regular.pdf')
        
        assert result['ocr_applied'] is False
        assert result['is_scanned'] is False
