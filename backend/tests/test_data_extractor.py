"""
Unit tests for DataExtractor class.

These tests verify the format-specific extraction methods for GST returns,
ITR, bank statements, and annual reports.
"""

import pytest
from datetime import datetime
from app.services.data_ingestor.data_extractor import DataExtractor
from app.models.financial import GSTData, Transaction, FinancialData


class TestDataExtractor:
    """Test suite for DataExtractor class."""
    
    @pytest.fixture
    def extractor(self):
        """Create a DataExtractor instance for testing."""
        return DataExtractor()
    
    # GST Returns Tests
    
    def test_extract_gst_returns_gstr2a(self, extractor):
        """Test extraction of GSTR-2A format."""
        gst_data = {
            'text': """
            GSTR-2A
            GSTIN: 27AABCU9603R1ZM
            Tax Period: 01/2024
            Total Taxable Value: 500000.00
            Input Tax Credit: 90000.00
            Total Tax: 90000.00
            """,
            'document_type': 'gst_return_2a'
        }
        
        result = extractor.extract_gst_returns(gst_data)
        
        assert isinstance(result, GSTData)
        assert result.gstin == '27AABCU9603R1ZM'
        assert result.period == '2024-01'
        assert result.purchases == 500000.00
        assert result.tax_paid == 90000.00
        assert result.sales == 0.0  # GSTR-2A doesn't have sales
    
    def test_extract_gst_returns_gstr3b(self, extractor):
        """Test extraction of GSTR-3B format."""
        gst_data = {
            'text': """
            GSTR-3B
            GSTIN: 29AABCU9603R1ZM
            Tax Period: February-2024
            Outward Taxable Supplies: 1000000.00
            Eligible ITC: 150000.00
            Total Tax Payable: 180000.00
            """,
            'document_type': 'gst_return_3b'
        }
        
        result = extractor.extract_gst_returns(gst_data)
        
        assert isinstance(result, GSTData)
        assert result.gstin == '29AABCU9603R1ZM'
        assert result.period == '2024-02'
        assert result.sales == 1000000.00
        assert result.purchases == 150000.00
        assert result.tax_paid == 180000.00
    
    def test_extract_gst_returns_missing_gstin(self, extractor):
        """Test GST extraction when GSTIN is missing."""
        gst_data = {
            'text': """
            GSTR-3B
            Tax Period: 03/2024
            Outward Taxable Supplies: 500000.00
            """,
            'document_type': 'gst_return_3b'
        }
        
        result = extractor.extract_gst_returns(gst_data)
        
        assert result.gstin == ""  # Should handle missing GSTIN gracefully
        assert result.sales == 500000.00
    
    def test_extract_gst_returns_empty_text(self, extractor):
        """Test GST extraction with empty text."""
        gst_data = {
            'text': '',
            'document_type': 'gst_return'
        }
        
        with pytest.raises(ValueError, match="No text content provided"):
            extractor.extract_gst_returns(gst_data)
    
    # ITR Tests
    
    def test_extract_itr_basic(self, extractor):
        """Test basic ITR extraction."""
        itr_data = {
            'text': """
            Income Tax Return
            PAN: ABCDE1234F
            Assessment Year: 2023-24
            Filing Date: 31/07/2023
            Gross Total Income: 1500000.00
            Total Deductions: 150000.00
            Taxable Income: 1350000.00
            Tax Paid: 200000.00
            Refund Amount: 5000.00
            """
        }
        
        result = extractor.extract_itr(itr_data)
        
        assert result['pan'] == 'ABCDE1234F'
        assert result['assessment_year'] == '2023-24'
        assert result['gross_total_income'] == 1500000.00
        assert result['total_deductions'] == 150000.00
        assert result['taxable_income'] == 1350000.00
        assert result['tax_paid'] == 200000.00
        assert result['refund_amount'] == 5000.00
    
    def test_extract_itr_with_income_sources(self, extractor):
        """Test ITR extraction with multiple income sources."""
        itr_data = {
            'text': """
            Income Tax Return
            PAN: XYZAB5678C
            Assessment Year: 2023-24
            Income from Salary: 800000.00
            Income from Business: 500000.00
            Capital Gains: 200000.00
            Interest Income: 50000.00
            """
        }
        
        result = extractor.extract_itr(itr_data)
        
        assert result['pan'] == 'XYZAB5678C'
        assert len(result['income_sources']) > 0
        
        # Check that income sources were extracted
        source_types = [source['source_type'] for source in result['income_sources']]
        assert 'salary' in source_types
        assert 'business' in source_types
    
    def test_extract_itr_empty_text(self, extractor):
        """Test ITR extraction with empty text."""
        itr_data = {'text': ''}
        
        with pytest.raises(ValueError, match="No text content provided"):
            extractor.extract_itr(itr_data)
    
    # Bank Statement Tests
    
    def test_extract_bank_statements_basic(self, extractor):
        """Test basic bank statement extraction."""
        statement_data = {
            'text': """
            Account Statement
            Date        Description             Debit       Credit      Balance
            01/01/2024  Opening Balance                                 100000.00
            02/01/2024  Salary Credit                       50000.00    150000.00
            03/01/2024  ATM Withdrawal          5000.00                 145000.00
            04/01/2024  Online Transfer         10000.00                135000.00
            """
        }
        
        result = extractor.extract_bank_statements(statement_data)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check first transaction
        assert all(isinstance(txn, Transaction) for txn in result)
        
        # Verify transaction structure
        for txn in result:
            assert isinstance(txn.date, datetime)
            assert isinstance(txn.description, str)
            assert isinstance(txn.debit, float)
            assert isinstance(txn.credit, float)
            assert isinstance(txn.balance, float)
    
    def test_extract_bank_statements_with_indian_format(self, extractor):
        """Test bank statement with Indian number format (commas)."""
        statement_data = {
            'text': """
            Date        Description             Amount      Balance
            01/01/2024  Salary Credit           Rs. 1,50,000.00    Rs. 2,50,000.00
            02/01/2024  Rent Payment Dr         Rs. 25,000.00      Rs. 2,25,000.00
            """
        }
        
        result = extractor.extract_bank_statements(statement_data)
        
        assert len(result) >= 2  # Should extract at least 2 transactions
        # Verify amounts are parsed correctly (commas removed)
        # Check that we have transactions with reasonable balances
        assert any(txn.balance > 0 for txn in result)
    
    def test_extract_bank_statements_empty_text(self, extractor):
        """Test bank statement extraction with empty text."""
        statement_data = {'text': ''}
        
        with pytest.raises(ValueError, match="No text content provided"):
            extractor.extract_bank_statements(statement_data)
    
    # Annual Report Tests
    
    def test_extract_annual_report_basic(self, extractor):
        """Test basic annual report extraction."""
        report_data = {
            'text': """
            Annual Report 2023-24
            Financial Statements
            
            Profit and Loss Statement
            Total Revenue: 10000000.00
            Total Expenses: 7000000.00
            EBITDA: 3500000.00
            Net Profit: 2000000.00
            
            Balance Sheet
            Total Assets: 50000000.00
            Total Liabilities: 30000000.00
            Total Equity: 20000000.00
            
            Cash Flow Statement
            Cash Flow from Operating Activities: 2500000.00
            """,
            'company_id': 'COMP001'
        }
        
        result = extractor.extract_annual_report(report_data)
        
        assert isinstance(result, FinancialData)
        assert result.company_id == 'COMP001'
        assert result.revenue == 10000000.00
        assert result.expenses == 7000000.00
        assert result.ebitda == 3500000.00
        assert result.net_profit == 2000000.00
        assert result.total_assets == 50000000.00
        assert result.total_liabilities == 30000000.00
        assert result.equity == 20000000.00
        assert result.cash_flow == 2500000.00
    
    def test_extract_annual_report_confidence_scores(self, extractor):
        """Test that confidence scores are calculated."""
        report_data = {
            'text': """
            Annual Report
            Total Revenue: 5000000.00
            Net Profit: 500000.00
            """,
            'company_id': 'COMP002'
        }
        
        result = extractor.extract_annual_report(report_data)
        
        assert isinstance(result.confidence_scores, dict)
        assert 'revenue' in result.confidence_scores
        assert 'net_profit' in result.confidence_scores
        
        # High confidence for extracted fields
        assert result.confidence_scores['revenue'] > 0.5
        assert result.confidence_scores['net_profit'] > 0.5
        
        # Low confidence for missing fields
        assert result.confidence_scores['ebitda'] < 0.5
    
    def test_extract_annual_report_empty_text(self, extractor):
        """Test annual report extraction with empty text."""
        report_data = {'text': '', 'company_id': 'COMP003'}
        
        with pytest.raises(ValueError, match="No text content provided"):
            extractor.extract_annual_report(report_data)
    
    def test_extract_annual_report_partial_data(self, extractor):
        """Test annual report with only partial data available."""
        report_data = {
            'text': """
            Financial Report
            Revenue from Operations: 8000000.00
            Total Assets: 40000000.00
            """,
            'company_id': 'COMP004'
        }
        
        result = extractor.extract_annual_report(report_data)
        
        # Should extract available fields
        assert result.revenue == 8000000.00
        assert result.total_assets == 40000000.00
        
        # Missing fields should be 0
        assert result.expenses == 0.0
        assert result.ebitda == 0.0
    
    # Helper Method Tests
    
    def test_normalize_period_formats(self, extractor):
        """Test period normalization with various formats."""
        assert extractor._normalize_period('01/2024') == '2024-01'
        assert extractor._normalize_period('12-2023') == '2023-12'
        assert extractor._normalize_period('January-2024') == '2024-01'
        assert extractor._normalize_period('February 2024') == '2024-02'
    
    def test_extract_amount_with_keywords(self, extractor):
        """Test amount extraction with various keywords."""
        text = """
        Total Revenue: 1000000.00
        Sales: Rs. 500000.00
        Income: INR 750000
        """
        
        revenue = extractor._extract_amount(text, ['total revenue', 'revenue'])
        assert revenue == 1000000.00
        
        sales = extractor._extract_amount(text, ['sales'])
        assert sales == 500000.00
        
        income = extractor._extract_amount(text, ['income'])
        assert income == 750000.0
    
    def test_parse_date_formats(self, extractor):
        """Test date parsing with various formats."""
        date1 = extractor._parse_date('31/12/2023')
        assert date1.year == 2023
        assert date1.month == 12
        assert date1.day == 31
        
        date2 = extractor._parse_date('01-01-2024')
        assert date2.year == 2024
        assert date2.month == 1
        assert date2.day == 1
        
        date3 = extractor._parse_date('15/06/24')
        assert date3.year == 2024
        assert date3.month == 6
        assert date3.day == 15


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
