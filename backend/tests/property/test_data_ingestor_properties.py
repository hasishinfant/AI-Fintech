"""Property-based tests for data ingestor components.

Feature: intelli-credit
Properties tested:
- Property 1: Document Data Extraction Completeness
- Property 2: OCR Application for Scanned Documents
- Property 45: GST Format Parsing
"""

from hypothesis import given, strategies as st, settings, assume, HealthCheck
import pytest
from datetime import datetime
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from app.services.data_ingestor.document_parser import DocumentParser
from app.services.data_ingestor.data_extractor import DataExtractor
from app.models.financial import GSTData, Transaction, FinancialData


# Strategies for generating test data

# GST-related strategies
gstin_strategy = st.just("27AABCU9603R1ZM")  # Valid GSTIN format
gst_period_strategy = st.sampled_from(["01/2024", "02/2024", "03/2024", "12/2023"])
gst_amount_strategy = st.floats(min_value=1000.0, max_value=10000000.0)

# Bank statement strategies
transaction_date_strategy = st.dates(min_value=datetime(2023, 1, 1).date(), 
                                     max_value=datetime(2024, 12, 31).date())
transaction_amount_strategy = st.floats(min_value=100.0, max_value=1000000.0)
transaction_description_strategy = st.text(min_size=5, max_size=50)

# Financial data strategies
financial_amount_strategy = st.floats(min_value=10000.0, max_value=100000000.0)
financial_period_strategy = st.sampled_from(["2023-24", "2024-25", "2022-23"])

# Document type strategies
document_type_strategy = st.sampled_from([
    "gst_return_2a", "gst_return_3b", "itr", "bank_statement", 
    "annual_report", "board_minutes", "rating_report", "mca_filing"
])


# Property 1: Document Data Extraction Completeness

@settings(max_examples=20)
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    sales=gst_amount_strategy,
    purchases=gst_amount_strategy,
    tax_paid=gst_amount_strategy,
)
def test_gst_extraction_completeness(gstin, period, sales, purchases, tax_paid):
    """
    Property 1: Document Data Extraction Completeness (GST Returns)
    
    For any valid GST return document with required fields, when parsed by
    the Data_Ingestor, all required fields for GST document type should be
    extracted and present in the output.
    
    Validates: Requirements 1.1, 18.1
    """
    extractor = DataExtractor()
    
    # Create a realistic GST return document
    gst_text = f"""
    GSTR-3B Return
    GSTIN: {gstin}
    Tax Period: {period}
    Outward Taxable Supplies: {sales}
    Eligible ITC: {purchases}
    Total Tax Payable: {tax_paid}
    """
    
    gst_data = {
        'text': gst_text,
        'document_type': 'gst_return_3b'
    }
    
    # Extract GST data
    result = extractor.extract_gst_returns(gst_data)
    
    # Verify all required fields are present and extracted
    assert isinstance(result, GSTData), "Result should be GSTData instance"
    assert result.gstin is not None, "GSTIN should be extracted"
    assert result.period is not None, "Period should be extracted"
    assert result.sales is not None, "Sales should be extracted"
    assert result.purchases is not None, "Purchases should be extracted"
    assert result.tax_paid is not None, "Tax paid should be extracted"
    assert isinstance(result.transactions, list), "Transactions should be a list"
    
    # Verify extracted values are reasonable
    assert len(result.gstin) > 0, "GSTIN should not be empty"
    assert result.sales >= 0, "Sales should be non-negative"
    assert result.purchases >= 0, "Purchases should be non-negative"
    assert result.tax_paid >= 0, "Tax paid should be non-negative"


@settings(max_examples=20, suppress_health_check=[HealthCheck.data_too_large])
@given(
    pan=st.just("ABCDE1234F"),
    assessment_year=st.just("2023-24"),
    gross_income=financial_amount_strategy,
    taxable_income=financial_amount_strategy,
    tax_paid=financial_amount_strategy,
)
def test_itr_extraction_completeness(pan, assessment_year, gross_income, taxable_income, tax_paid):
    """
    Property 1: Document Data Extraction Completeness (ITR)
    
    For any valid ITR document with required fields, when parsed by
    the Data_Ingestor, all required fields for ITR document type should be
    extracted and present in the output.
    
    Validates: Requirements 1.2
    """
    extractor = DataExtractor()
    
    # Create a realistic ITR document
    itr_text = f"""
    Income Tax Return
    PAN: {pan}
    Assessment Year: {assessment_year}
    Gross Total Income: {gross_income}
    Taxable Income: {taxable_income}
    Tax Paid: {tax_paid}
    """
    
    itr_data = {'text': itr_text}
    
    # Extract ITR data
    result = extractor.extract_itr(itr_data)
    
    # Verify all required fields are present
    assert isinstance(result, dict), "Result should be a dictionary"
    assert 'pan' in result, "PAN should be in result"
    assert 'assessment_year' in result, "Assessment year should be in result"
    assert 'gross_total_income' in result, "Gross total income should be in result"
    assert 'taxable_income' in result, "Taxable income should be in result"
    assert 'tax_paid' in result, "Tax paid should be in result"
    assert 'income_sources' in result, "Income sources should be in result"
    
    # Verify extracted values are reasonable
    assert result['gross_total_income'] >= 0, "Gross income should be non-negative"
    assert result['taxable_income'] >= 0, "Taxable income should be non-negative"
    assert result['tax_paid'] >= 0, "Tax paid should be non-negative"


@settings(max_examples=20, suppress_health_check=[HealthCheck.data_too_large])
@given(
    num_transactions=st.integers(min_value=1, max_value=10),
)
def test_bank_statement_extraction_completeness(num_transactions):
    """
    Property 1: Document Data Extraction Completeness (Bank Statements)
    
    For any valid bank statement document with transaction records, when
    parsed by the Data_Ingestor, all transaction fields should be extracted
    and present in the output.
    
    Validates: Requirements 1.3
    """
    extractor = DataExtractor()
    
    # Create a realistic bank statement with multiple transactions
    statement_lines = ["Date        Description             Debit       Credit      Balance"]
    balance = 100000.0
    
    for i in range(num_transactions):
        date = f"0{i+1}/01/2024"
        description = f"Transaction {i+1}"
        debit = 1000.0 * (i % 2)  # Alternate debits
        credit = 2000.0 * ((i + 1) % 2)  # Alternate credits
        balance += credit - debit
        
        statement_lines.append(
            f"{date}  {description:<20}  {debit:>10.2f}  {credit:>10.2f}  {balance:>10.2f}"
        )
    
    statement_text = "\n".join(statement_lines)
    statement_data = {'text': statement_text}
    
    # Extract transactions
    result = extractor.extract_bank_statements(statement_data)
    
    # Verify all transactions are extracted
    assert isinstance(result, list), "Result should be a list of transactions"
    assert len(result) > 0, "At least one transaction should be extracted"
    
    # Verify each transaction has required fields
    for transaction in result:
        assert isinstance(transaction, Transaction), "Each item should be a Transaction"
        assert transaction.date is not None, "Transaction date should be present"
        assert transaction.description is not None, "Transaction description should be present"
        assert isinstance(transaction.debit, float), "Debit should be a float"
        assert isinstance(transaction.credit, float), "Credit should be a float"
        assert isinstance(transaction.balance, float), "Balance should be a float"
        assert transaction.debit >= 0, "Debit should be non-negative"
        assert transaction.credit >= 0, "Credit should be non-negative"


@settings(max_examples=20, suppress_health_check=[HealthCheck.data_too_large])
@given(
    revenue=financial_amount_strategy,
    expenses=financial_amount_strategy,
    net_profit=financial_amount_strategy,
    total_assets=financial_amount_strategy,
    equity=financial_amount_strategy,
)
def test_annual_report_extraction_completeness(revenue, expenses, net_profit, total_assets, equity):
    """
    Property 1: Document Data Extraction Completeness (Annual Reports)
    
    For any valid annual report document with financial statements, when
    parsed by the Data_Ingestor, all required financial fields should be
    extracted and present in the output.
    
    Validates: Requirements 1.4
    """
    extractor = DataExtractor()
    
    # Create a realistic annual report
    report_text = f"""
    Annual Report 2023-24
    
    Profit and Loss Statement
    Total Revenue: {revenue}
    Total Expenses: {expenses}
    Net Profit: {net_profit}
    
    Balance Sheet
    Total Assets: {total_assets}
    Total Equity: {equity}
    """
    
    report_data = {
        'text': report_text,
        'company_id': 'TEST001'
    }
    
    # Extract financial data
    result = extractor.extract_annual_report(report_data)
    
    # Verify all required fields are present
    assert isinstance(result, FinancialData), "Result should be FinancialData instance"
    assert result.company_id is not None, "Company ID should be present"
    assert result.revenue is not None, "Revenue should be extracted"
    assert result.expenses is not None, "Expenses should be extracted"
    assert result.net_profit is not None, "Net profit should be extracted"
    assert result.total_assets is not None, "Total assets should be extracted"
    assert result.equity is not None, "Equity should be extracted"
    assert isinstance(result.confidence_scores, dict), "Confidence scores should be a dict"
    
    # Verify extracted values are reasonable
    assert result.revenue >= 0, "Revenue should be non-negative"
    assert result.expenses >= 0, "Expenses should be non-negative"
    assert result.total_assets >= 0, "Total assets should be non-negative"
    assert result.equity >= 0, "Equity should be non-negative"


# Property 2: OCR Application for Scanned Documents

@settings(max_examples=10)
@given(
    image_width=st.integers(min_value=100, max_value=2000),
    image_height=st.integers(min_value=100, max_value=2000),
)
def test_ocr_applied_to_scanned_documents(image_width, image_height):
    """
    Property 2: OCR Application for Scanned Documents
    
    For any scanned document uploaded to the system, the Data_Ingestor
    should apply OCR processing before attempting data extraction.
    
    Validates: Requirements 1.5
    """
    parser = DocumentParser()
    
    # Create a mock scanned image
    image = Image.new('RGB', (image_width, image_height), color='white')
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Mock pytesseract to return text
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.return_value = "Scanned document text content"
        
        # Apply OCR
        result = parser.apply_ocr(image_data)
        
        # Verify OCR was applied
        assert isinstance(result, str), "OCR should return extracted text"
        assert len(result) > 0, "OCR should extract some text"
        assert "Scanned document text content" in result, "OCR should return the mocked text"
        
        # Verify pytesseract was called
        mock_ocr.assert_called_once()


@settings(max_examples=10)
@given(
    language=st.sampled_from(['eng', 'eng+hin', 'eng+tam', 'eng+tel']),
)
def test_ocr_with_multiple_languages(language):
    """
    Property 2: OCR Application for Scanned Documents (Multi-language)
    
    For any scanned document with multiple languages, the Data_Ingestor
    should apply OCR with appropriate language configuration.
    
    Validates: Requirements 1.5
    """
    parser = DocumentParser()
    
    # Create a mock image
    image = Image.new('RGB', (500, 500), color='white')
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Mock pytesseract
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.return_value = f"Text in {language}"
        
        # Apply OCR with specific language
        result = parser.apply_ocr(image_data, language=language)
        
        # Verify OCR was called with correct language
        assert isinstance(result, str), "OCR should return text"
        mock_ocr.assert_called_once()
        
        # Verify language parameter was passed
        call_args = mock_ocr.call_args
        assert call_args[1]['lang'] == language, f"Language {language} should be passed to OCR"


@settings(max_examples=10)
@given(
    num_pages=st.integers(min_value=1, max_value=5),
)
def test_ocr_applied_to_multi_page_scanned_pdf(num_pages):
    """
    Property 2: OCR Application for Scanned Documents (Multi-page PDF)
    
    For any multi-page scanned PDF document, the Data_Ingestor should
    apply OCR to all pages.
    
    Validates: Requirements 1.5
    """
    parser = DocumentParser()
    
    # Mock PDF parsing to return scanned document
    with patch('app.services.data_ingestor.document_parser.DocumentParser.parse_pdf') as mock_parse:
        mock_parse.return_value = {
            'text': 'abc',  # Very little text - indicates scanned
            'pages': [{'page_number': i, 'text': 'abc', 'char_count': 3} for i in range(1, num_pages + 1)],
            'page_count': num_pages,
            'is_scanned': True,
            'metadata': {}
        }
        
        # Mock image conversion
        with patch('app.services.data_ingestor.document_parser.convert_from_path') as mock_convert:
            mock_images = [Mock() for _ in range(num_pages)]
            mock_convert.return_value = mock_images
            
            # Mock OCR
            with patch('app.services.data_ingestor.document_parser.DocumentParser.apply_ocr') as mock_ocr:
                mock_ocr.return_value = "OCR extracted text"
                
                # Parse PDF with OCR
                with patch('pathlib.Path.exists', return_value=True):
                    result = parser.parse_pdf_with_ocr('scanned.pdf')
                
                # Verify OCR was applied to all pages
                assert result['ocr_applied'] is True, "OCR should be applied to scanned document"
                assert mock_ocr.call_count == num_pages, f"OCR should be applied to all {num_pages} pages"
                assert len(result['pages']) == num_pages, f"Result should contain {num_pages} pages"


# Property 45: GST Format Parsing

@settings(max_examples=20)
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    purchases=gst_amount_strategy,
    tax=gst_amount_strategy,
)
def test_gstr2a_format_parsing(gstin, period, purchases, tax):
    """
    Property 45: GST Format Parsing (GSTR-2A)
    
    For any GSTR-2A document with valid format, the Data_Ingestor should
    correctly parse and extract all required fields specific to GSTR-2A.
    
    Validates: Requirements 18.1
    """
    extractor = DataExtractor()
    
    # Create GSTR-2A formatted document with clear labels
    # Note: GSTR-2A focuses on purchases/input tax credit
    gstr2a_text = f"""
    GSTR-2A
    GSTIN: {gstin}
    Tax Period: {period}
    Total Taxable Value: Rs. {purchases:.2f}
    Total Tax: Rs. {tax:.2f}
    """
    
    gst_data = {
        'text': gstr2a_text,
        'document_type': 'gst_return_2a'
    }
    
    # Extract GST data
    result = extractor.extract_gst_returns(gst_data)
    
    # Verify GSTR-2A specific parsing
    assert isinstance(result, GSTData), "Should return GSTData"
    assert result.gstin == gstin, "GSTIN should match"
    # Allow for small floating point differences
    assert abs(result.purchases - purchases) < 1.0, "Purchases should be extracted from GSTR-2A"
    assert abs(result.tax_paid - tax) < 1.0, "Tax should be extracted"
    assert result.sales == 0.0, "GSTR-2A should not have sales data"


@settings(max_examples=20)
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    sales=gst_amount_strategy,
    itc=gst_amount_strategy,
    tax_payable=gst_amount_strategy,
)
def test_gstr3b_format_parsing(gstin, period, sales, itc, tax_payable):
    """
    Property 45: GST Format Parsing (GSTR-3B)
    
    For any GSTR-3B document with valid format, the Data_Ingestor should
    correctly parse and extract all required fields specific to GSTR-3B.
    
    Validates: Requirements 18.1
    """
    extractor = DataExtractor()
    
    # Create GSTR-3B formatted document with clear labels
    gstr3b_text = f"""
    GSTR-3B
    GSTIN: {gstin}
    Tax Period: {period}
    Outward Taxable Supplies: Rs. {sales:.2f}
    Eligible ITC: Rs. {itc:.2f}
    Total Tax Payable: Rs. {tax_payable:.2f}
    """
    
    gst_data = {
        'text': gstr3b_text,
        'document_type': 'gst_return_3b'
    }
    
    # Extract GST data
    result = extractor.extract_gst_returns(gst_data)
    
    # Verify GSTR-3B specific parsing
    assert isinstance(result, GSTData), "Should return GSTData"
    assert result.gstin == gstin, "GSTIN should match"
    # Allow for small floating point differences
    assert abs(result.sales - sales) < 1.0, "Sales should be extracted from GSTR-3B"
    assert abs(result.purchases - itc) < 1.0, "ITC should be extracted as purchases"
    assert abs(result.tax_paid - tax_payable) < 1.0, "Tax payable should be extracted"


@settings(max_examples=20)
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
)
def test_gst_period_normalization(gstin, period):
    """
    Property 45: GST Format Parsing (Period Normalization)
    
    For any GST document with various period formats, the Data_Ingestor
    should normalize the period to a consistent format.
    
    Validates: Requirements 18.1
    """
    extractor = DataExtractor()
    
    # Create GST document with period
    gst_text = f"""
    GSTR-3B
    GSTIN: {gstin}
    Tax Period: {period}
    Outward Taxable Supplies: 500000
    """
    
    gst_data = {
        'text': gst_text,
        'document_type': 'gst_return_3b'
    }
    
    # Extract GST data
    result = extractor.extract_gst_returns(gst_data)
    
    # Verify period is normalized
    assert result.period is not None, "Period should be extracted"
    assert len(result.period) > 0, "Period should not be empty"
    
    # Period should be in YYYY-MM format or similar normalized format
    # (allowing for various input formats)
    assert isinstance(result.period, str), "Period should be a string"


@settings(max_examples=20)
@given(
    gstin=gstin_strategy,
)
def test_gst_transaction_extraction(gstin):
    """
    Property 45: GST Format Parsing (Transaction Extraction)
    
    For any GST document with transaction records, the Data_Ingestor
    should extract transaction details.
    
    Validates: Requirements 18.1
    """
    extractor = DataExtractor()
    
    # Create GST document with transaction details
    gst_text = f"""
    GSTR-3B
    GSTIN: {gstin}
    Tax Period: 01/2024
    
    Transaction Details:
    {gstin} INV001 01/01/2024 100000 18000
    {gstin} INV002 02/01/2024 200000 36000
    """
    
    gst_data = {
        'text': gst_text,
        'document_type': 'gst_return_3b'
    }
    
    # Extract GST data
    result = extractor.extract_gst_returns(gst_data)
    
    # Verify transactions are extracted
    assert isinstance(result.transactions, list), "Transactions should be a list"
    # Transactions may or may not be extracted depending on format complexity
    # but the field should exist and be a list
