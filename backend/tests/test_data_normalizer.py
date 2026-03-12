"""
Unit tests for DataNormalizer class.

Tests the normalization of financial data from various sources and
confidence score calculation.
"""

import pytest
from datetime import datetime

from app.services.data_ingestor.data_normalizer import DataNormalizer


class TestDataNormalizer:
    """Test suite for DataNormalizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = DataNormalizer()
    
    def test_normalize_gst_data(self):
        """Test normalization of GST return data."""
        raw_data = {
            'company_id': 'COMP123',
            'gstin': '22AAAAA0000A1Z5',
            'period': '01/2024',
            'sales': 1000000.0,
            'purchases': 600000.0,
            'tax_paid': 50000.0
        }
        
        result = self.normalizer.normalize_financial_data(raw_data, 'gst_return')
        
        assert result['company_id'] == 'COMP123'
        assert result['period'] == '2024-01'
        assert result['revenue'] == 1000000.0
        assert result['expenses'] == 600000.0
        assert result['source_type'] == 'gst_return'
        assert result['validation_status'] in ['valid', 'warning']
    
    def test_normalize_itr_data(self):
        """Test normalization of ITR data."""
        raw_data = {
            'company_id': 'COMP456',
            'pan': 'ABCDE1234F',
            'assessment_year': '2023-24',
            'gross_total_income': 5000000.0,
            'total_deductions': 500000.0,
            'taxable_income': 4500000.0
        }
        
        result = self.normalizer.normalize_financial_data(raw_data, 'itr')
        
        assert result['company_id'] == 'COMP456'
        assert result['period'] == '2023'  # Financial year normalized to first year
        assert result['revenue'] == 5000000.0
        assert result['expenses'] == 500000.0
        assert result['net_profit'] == 4500000.0
        assert result['source_type'] == 'itr'
    
    def test_normalize_annual_report_data(self):
        """Test normalization of annual report data."""
        raw_data = {
            'company_id': 'COMP789',
            'period': '2023',
            'revenue': 10000000.0,
            'expenses': 7000000.0,
            'ebitda': 3500000.0,
            'net_profit': 2000000.0,
            'total_assets': 50000000.0,
            'total_liabilities': 30000000.0,
            'equity': 20000000.0,
            'cash_flow': 2500000.0
        }
        
        result = self.normalizer.normalize_financial_data(raw_data, 'annual_report')
        
        assert result['company_id'] == 'COMP789'
        assert result['period'] == '2023'
        assert result['revenue'] == 10000000.0
        assert result['ebitda'] == 3500000.0
        assert result['total_assets'] == 50000000.0
        assert result['equity'] == 20000000.0
        assert result['validation_status'] == 'valid'
    
    def test_calculate_confidence_scores_high_quality(self):
        """Test confidence score calculation for high-quality data."""
        extracted_data = {
            'extraction_method': 'structured',
            'revenue': 1000000.0,
            'expenses': 600000.0,
            'ebitda': 400000.0,
            'net_profit': 300000.0,
            'total_assets': 5000000.0,
            'total_liabilities': 3000000.0,
            'equity': 2000000.0,
            'cash_flow': 350000.0,
            'gstin': '22AAAAA0000A1Z5',
            'period': '2024-01'
        }
        
        scores = self.normalizer.calculate_confidence_scores(extracted_data)
        
        assert scores['revenue'] >= 0.85
        assert scores['expenses'] >= 0.85
        assert scores['total_assets'] >= 0.85
        assert scores['gstin'] >= 0.90
        assert scores['period'] >= 0.85
    
    def test_calculate_confidence_scores_ocr_data(self):
        """Test confidence score calculation for OCR-extracted data."""
        extracted_data = {
            'extraction_method': 'ocr',
            'revenue': 1000000.0,
            'expenses': 600000.0,
            'total_assets': 5000000.0
        }
        
        scores = self.normalizer.calculate_confidence_scores(extracted_data)
        
        # OCR data should have lower base confidence
        assert scores['revenue'] < 0.85
        assert scores['revenue'] >= 0.70
    
    def test_calculate_confidence_scores_missing_fields(self):
        """Test confidence score calculation with missing fields."""
        extracted_data = {
            'revenue': 1000000.0,
            'expenses': 0,  # Zero value
        }
        
        scores = self.normalizer.calculate_confidence_scores(extracted_data)
        
        assert scores['revenue'] > 0.7
        assert scores['expenses'] == 0.3  # Zero gets low confidence
        assert scores['ebitda'] == 0.0  # Missing field
    
    def test_validation_rules_negative_revenue(self):
        """Test validation rule for negative revenue."""
        raw_data = {
            'company_id': 'COMP123',
            'period': '2024',
            'revenue': -1000000.0,
            'expenses': 500000.0
        }
        
        result = self.normalizer.normalize_financial_data(raw_data, 'manual_input')
        
        assert result['validation_status'] == 'warning'
        assert any('negative' in msg.lower() for msg in result['validation_messages'])
    
    def test_validation_rules_balance_sheet_equation(self):
        """Test validation rule for balance sheet equation."""
        raw_data = {
            'company_id': 'COMP123',
            'period': '2024',
            'total_assets': 10000000.0,
            'total_liabilities': 6000000.0,
            'equity': 3000000.0  # Should be 4000000
        }
        
        result = self.normalizer.normalize_financial_data(raw_data, 'manual_input')
        
        assert result['validation_status'] == 'warning'
        assert any('balance' in msg.lower() for msg in result['validation_messages'])
    
    def test_normalize_period_various_formats(self):
        """Test period normalization with various formats."""
        test_cases = [
            ('01/2024', '2024-01'),
            ('01-2024', '2024-01'),
            ('2024-01', '2024-01'),
            ('January-2024', '2024-01'),
            ('2023-24', '2023'),
            ('2024', '2024')
        ]
        
        for input_period, expected in test_cases:
            result = self.normalizer._normalize_period(input_period)
            assert result == expected, f"Failed for input: {input_period}"
    
    def test_validate_gstin(self):
        """Test GSTIN validation."""
        valid_gstin = '22AAAAA0000A1Z5'
        invalid_gstin = '22AAAAA0000'
        
        assert self.normalizer._validate_gstin(valid_gstin) is True
        assert self.normalizer._validate_gstin(invalid_gstin) is False
    
    def test_validate_pan(self):
        """Test PAN validation."""
        valid_pan = 'ABCDE1234F'
        invalid_pan = 'ABCDE1234'
        
        assert self.normalizer._validate_pan(valid_pan) is True
        assert self.normalizer._validate_pan(invalid_pan) is False
    
    def test_validate_cin(self):
        """Test CIN validation."""
        valid_cin = 'L12345MH2020PLC123456'
        invalid_cin = 'L12345MH2020'
        
        assert self.normalizer._validate_cin(valid_cin) is True
        assert self.normalizer._validate_cin(invalid_cin) is False
    
    def test_invalid_source_type(self):
        """Test error handling for invalid source type."""
        raw_data = {'company_id': 'COMP123'}
        
        with pytest.raises(ValueError, match="Unknown source type"):
            self.normalizer.normalize_financial_data(raw_data, 'invalid_type')
    
    def test_empty_raw_data(self):
        """Test error handling for empty raw data."""
        with pytest.raises(ValueError, match="Raw data cannot be empty"):
            self.normalizer.normalize_financial_data({}, 'gst_return')
