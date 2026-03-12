"""
Data Normalizer Module

This module provides data normalization and confidence scoring for extracted financial data.
It converts various formats to a unified schema and validates data quality.

Requirements: 2.5, 17.4
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re

from app.models.financial import FinancialData, GSTData, Transaction

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Handles normalization of extracted financial data to unified schema.
    
    This class provides:
    - Data format normalization across different source types
    - Confidence score calculation for extracted fields
    - Data validation rules for financial data
    """
    
    # Validation thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.7
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    
    # Expected ranges for financial data (in INR)
    REVENUE_MIN = 0
    REVENUE_MAX = 1e12  # 1 trillion
    ASSET_MIN = 0
    ASSET_MAX = 1e12
    
    def __init__(self):
        """Initialize the DataNormalizer."""
        self.validation_rules = self._initialize_validation_rules()

    def normalize_financial_data(self, raw_data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """
        Convert various formats to unified schema.
        
        Args:
            raw_data: Dictionary containing extracted data from any source
            source_type: Type of source document - one of:
                - "gst_return": GST return data
                - "itr": Income Tax Return data
                - "bank_statement": Bank statement data
                - "annual_report": Annual report financial data
                - "manual_input": Manually entered data
                
        Returns:
            Dictionary with normalized data in unified schema
            
        Requirements: 2.5
        """
        if not raw_data:
            raise ValueError("Raw data cannot be empty")
        
        if source_type not in ["gst_return", "itr", "bank_statement", "annual_report", "manual_input"]:
            raise ValueError(f"Unknown source type: {source_type}")
        
        logger.info(f"Normalizing data from source type: {source_type}")
        
        # Initialize normalized data structure
        normalized = {
            'company_id': '',
            'period': '',
            'revenue': 0.0,
            'expenses': 0.0,
            'ebitda': 0.0,
            'net_profit': 0.0,
            'total_assets': 0.0,
            'total_liabilities': 0.0,
            'equity': 0.0,
            'cash_flow': 0.0,
            'source_type': source_type,
            'normalized_at': datetime.now().isoformat(),
            'validation_status': 'valid',
            'validation_messages': []
        }
        
        # Apply source-specific normalization
        if source_type == "gst_return":
            normalized = self._normalize_gst_data(raw_data, normalized)
        elif source_type == "itr":
            normalized = self._normalize_itr_data(raw_data, normalized)
        elif source_type == "bank_statement":
            normalized = self._normalize_bank_statement_data(raw_data, normalized)
        elif source_type == "annual_report":
            normalized = self._normalize_annual_report_data(raw_data, normalized)
        elif source_type == "manual_input":
            normalized = self._normalize_manual_input(raw_data, normalized)
        
        # Apply validation rules
        normalized = self._apply_validation_rules(normalized)
        
        logger.info(f"Normalization complete. Status: {normalized['validation_status']}")
        
        return normalized

    def calculate_confidence_scores(self, extracted_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Assign confidence scores to extracted fields.
        
        This method analyzes extracted data and calculates confidence scores
        for each field based on multiple factors:
        - Presence of data (field is not empty/zero)
        - Data format validity (matches expected patterns)
        - Data range validity (within expected bounds)
        - Cross-field consistency (related fields are consistent)
        - Extraction method quality (OCR vs structured parsing)
        
        Args:
            extracted_data: Dictionary containing extracted field values
                
        Returns:
            Dictionary mapping field names to confidence scores (0.0 to 1.0)
                
        Requirements: 17.4
        """
        confidence_scores = {}
        extraction_method = extracted_data.get('extraction_method', 'structured')
        
        # Base confidence by extraction method
        base_confidence = {
            'manual': 0.95,
            'structured': 0.90,
            'ocr': 0.75
        }.get(extraction_method, 0.80)
        
        # Financial fields to score
        financial_fields = [
            'revenue', 'expenses', 'ebitda', 'net_profit',
            'total_assets', 'total_liabilities', 'equity', 'cash_flow'
        ]
        
        for field in financial_fields:
            if field not in extracted_data:
                confidence_scores[field] = 0.0
                continue
            
            value = extracted_data[field]
            score = base_confidence
            
            # Factor 1: Presence check
            if value is None or value == '':
                score = 0.0
            elif isinstance(value, (int, float)) and value == 0:
                score = 0.3  # Zero might be valid but lower confidence
            
            # Factor 2: Data type validity
            if score > 0:
                try:
                    float_value = float(value) if not isinstance(value, float) else value
                    score = min(score, base_confidence)
                except (ValueError, TypeError):
                    score = 0.2
                    float_value = 0
            else:
                float_value = 0
            
            # Factor 3: Range validity
            if score > 0 and float_value != 0:
                if field in ['revenue', 'total_assets']:
                    if not (self.REVENUE_MIN <= float_value <= self.REVENUE_MAX):
                        score *= 0.7
                elif field in ['expenses', 'total_liabilities']:
                    if float_value < 0:
                        score *= 0.5
            
            # Factor 4: Pattern matching (if available)
            field_patterns = extracted_data.get('field_patterns', {})
            if field in field_patterns and field_patterns[field]:
                score = min(score + 0.05, 1.0)
            
            confidence_scores[field] = round(score, 2)
        
        # Identifier fields
        identifier_fields = ['company_id', 'period', 'gstin', 'pan', 'cin']
        for field in identifier_fields:
            if field in extracted_data:
                value = extracted_data[field]
                if value and isinstance(value, str) and len(value) > 0:
                    if field == 'gstin' and self._validate_gstin(value):
                        confidence_scores[field] = 0.95
                    elif field == 'pan' and self._validate_pan(value):
                        confidence_scores[field] = 0.95
                    elif field == 'cin' and self._validate_cin(value):
                        confidence_scores[field] = 0.95
                    elif field == 'period' and self._validate_period(value):
                        confidence_scores[field] = 0.90
                    elif field == 'company_id':
                        confidence_scores[field] = 0.85
                    else:
                        confidence_scores[field] = 0.60
                else:
                    confidence_scores[field] = 0.0
        
        # Cross-field consistency checks
        if 'revenue' in confidence_scores and 'expenses' in confidence_scores:
            if confidence_scores['revenue'] > 0.7 and confidence_scores['expenses'] > 0.7:
                revenue = float(extracted_data.get('revenue', 0))
                expenses = float(extracted_data.get('expenses', 0))
                if revenue > 0 and expenses > revenue * 2:
                    confidence_scores['expenses'] *= 0.8
        
        if 'total_assets' in confidence_scores and 'total_liabilities' in confidence_scores:
            if confidence_scores['total_assets'] > 0.7 and confidence_scores['total_liabilities'] > 0.7:
                assets = float(extracted_data.get('total_assets', 0))
                liabilities = float(extracted_data.get('total_liabilities', 0))
                if liabilities > assets * 1.5:
                    confidence_scores['total_liabilities'] *= 0.85
        
        logger.info(f"Calculated confidence scores for {len(confidence_scores)} fields")
        
        return confidence_scores

    def _normalize_gst_data(self, raw_data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize GST return data to unified schema."""
        if isinstance(raw_data, dict):
            normalized['company_id'] = raw_data.get('company_id', '')
            normalized['period'] = self._normalize_period(raw_data.get('period', ''))
            normalized['revenue'] = float(raw_data.get('sales', 0))
            normalized['expenses'] = float(raw_data.get('purchases', 0))
            
            if 'gstin' in raw_data:
                normalized['gstin'] = raw_data['gstin']
        
        return normalized
    
    def _normalize_itr_data(self, raw_data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ITR data to unified schema."""
        if isinstance(raw_data, dict):
            normalized['company_id'] = raw_data.get('company_id', '')
            normalized['period'] = self._normalize_period(raw_data.get('assessment_year', ''))
            normalized['revenue'] = float(raw_data.get('gross_total_income', 0))
            normalized['expenses'] = float(raw_data.get('total_deductions', 0))
            normalized['net_profit'] = float(raw_data.get('taxable_income', 0))
            
            if 'pan' in raw_data:
                normalized['pan'] = raw_data['pan']
        
        return normalized
    
    def _normalize_bank_statement_data(self, raw_data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize bank statement data to unified schema."""
        if isinstance(raw_data, dict):
            normalized['company_id'] = raw_data.get('company_id', '')
            
            transactions = raw_data.get('transactions', [])
            if transactions:
                total_credits = sum(t.credit if hasattr(t, 'credit') else t.get('credit', 0) for t in transactions)
                total_debits = sum(t.debit if hasattr(t, 'debit') else t.get('debit', 0) for t in transactions)
                
                normalized['revenue'] = float(total_credits)
                normalized['expenses'] = float(total_debits)
                normalized['cash_flow'] = float(total_credits - total_debits)
                
                if transactions:
                    first_transaction = transactions[0]
                    if hasattr(first_transaction, 'date'):
                        date = first_transaction.date
                    else:
                        date = first_transaction.get('date')
                    
                    if isinstance(date, datetime):
                        normalized['period'] = date.strftime('%Y-%m')
                    elif isinstance(date, str):
                        normalized['period'] = self._normalize_period(date)
        
        return normalized
    
    def _normalize_annual_report_data(self, raw_data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize annual report data to unified schema."""
        if isinstance(raw_data, dict):
            normalized['company_id'] = raw_data.get('company_id', '')
            normalized['period'] = self._normalize_period(raw_data.get('period', ''))
            normalized['revenue'] = float(raw_data.get('revenue', 0))
            normalized['expenses'] = float(raw_data.get('expenses', 0))
            normalized['ebitda'] = float(raw_data.get('ebitda', 0))
            normalized['net_profit'] = float(raw_data.get('net_profit', 0))
            normalized['total_assets'] = float(raw_data.get('total_assets', 0))
            normalized['total_liabilities'] = float(raw_data.get('total_liabilities', 0))
            normalized['equity'] = float(raw_data.get('equity', 0))
            normalized['cash_flow'] = float(raw_data.get('cash_flow', 0))
        
        return normalized
    
    def _normalize_manual_input(self, raw_data: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize manually entered data to unified schema."""
        field_mapping = {
            'company_id': 'company_id',
            'period': 'period',
            'revenue': 'revenue',
            'expenses': 'expenses',
            'ebitda': 'ebitda',
            'net_profit': 'net_profit',
            'total_assets': 'total_assets',
            'total_liabilities': 'total_liabilities',
            'equity': 'equity',
            'cash_flow': 'cash_flow'
        }
        
        for source_field, target_field in field_mapping.items():
            if source_field in raw_data:
                value = raw_data[source_field]
                if target_field == 'period':
                    normalized[target_field] = self._normalize_period(value)
                elif target_field == 'company_id':
                    normalized[target_field] = str(value)
                else:
                    try:
                        normalized[target_field] = float(value)
                    except (ValueError, TypeError):
                        normalized[target_field] = 0.0
        
        return normalized

    def _normalize_period(self, period: str) -> str:
        """
        Normalize period to standard format (YYYY-MM or YYYY).
        
        Handles various input formats:
        - MM/YYYY, MM-YYYY -> YYYY-MM
        - YYYY-YY (financial year) -> YYYY
        - Month-YYYY -> YYYY-MM
        """
        if not period or not isinstance(period, str):
            return ''
        
        period = period.strip()
        
        # Handle MM/YYYY or MM-YYYY
        if re.match(r'\d{2}[-/]\d{4}', period):
            month, year = re.split(r'[-/]', period)
            return f"{year}-{month}"
        
        # Handle YYYY-YY (financial year like 2023-24) - extract first year
        if re.match(r'^\d{4}-\d{2}$', period) and not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', period):
            year = period.split('-')[0]
            return year
        
        # Handle YYYY-MM (already normalized)
        if re.match(r'^\d{4}-(0[1-9]|1[0-2])$', period):
            return period
        
        # Handle Month-YYYY or Month YYYY
        month_names = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09',
            'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        for month_name, month_num in month_names.items():
            if month_name in period.lower():
                year_match = re.search(r'\d{4}', period)
                if year_match:
                    return f"{year_match.group(0)}-{month_num}"
        
        # Handle just YYYY
        if re.match(r'^\d{4}$', period):
            return period
        
        return period
    
    def _apply_validation_rules(self, normalized: Dict[str, Any]) -> Dict[str, Any]:
        """Apply validation rules to normalized data."""
        messages = []
        status = 'valid'
        
        # Rule 1: Revenue should be non-negative
        if normalized['revenue'] < 0:
            messages.append("Revenue is negative - this is unusual")
            status = 'warning'
        
        # Rule 2: Total assets should be non-negative
        if normalized['total_assets'] < 0:
            messages.append("Total assets is negative - this is invalid")
            status = 'error'
        
        # Rule 3: Equity should equal assets minus liabilities (if all present)
        if normalized['total_assets'] > 0 and normalized['total_liabilities'] > 0 and normalized['equity'] > 0:
            calculated_equity = normalized['total_assets'] - normalized['total_liabilities']
            difference_pct = abs(calculated_equity - normalized['equity']) / normalized['total_assets']
            if difference_pct > 0.05:  # More than 5% difference
                messages.append("Balance sheet equation doesn't balance (Assets - Liabilities ≠ Equity)")
                status = 'warning' if status != 'error' else status
        
        # Rule 4: EBITDA should be less than or equal to revenue
        if normalized['revenue'] > 0 and normalized['ebitda'] > normalized['revenue']:
            messages.append("EBITDA exceeds revenue - this is unusual")
            status = 'warning' if status != 'error' else status
        
        # Rule 5: Net profit should be less than or equal to revenue
        if normalized['revenue'] > 0 and normalized['net_profit'] > normalized['revenue']:
            messages.append("Net profit exceeds revenue - this is unusual")
            status = 'warning' if status != 'error' else status
        
        # Rule 6: Period should be present
        if not normalized['period']:
            messages.append("Financial period is missing")
            status = 'warning' if status != 'error' else status
        
        # Rule 7: Company ID should be present
        if not normalized['company_id']:
            messages.append("Company ID is missing")
            status = 'warning' if status != 'error' else status
        
        normalized['validation_status'] = status
        normalized['validation_messages'] = messages
        
        return normalized
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules configuration."""
        return {
            'revenue': {
                'min': self.REVENUE_MIN,
                'max': self.REVENUE_MAX,
                'allow_negative': False
            },
            'expenses': {
                'min': 0,
                'max': self.REVENUE_MAX,
                'allow_negative': False
            },
            'total_assets': {
                'min': self.ASSET_MIN,
                'max': self.ASSET_MAX,
                'allow_negative': False
            },
            'total_liabilities': {
                'min': 0,
                'max': self.ASSET_MAX,
                'allow_negative': False
            },
            'equity': {
                'min': -self.ASSET_MAX,
                'max': self.ASSET_MAX,
                'allow_negative': True
            },
            'net_profit': {
                'min': -self.REVENUE_MAX,
                'max': self.REVENUE_MAX,
                'allow_negative': True
            },
            'cash_flow': {
                'min': -self.REVENUE_MAX,
                'max': self.REVENUE_MAX,
                'allow_negative': True
            }
        }
    
    def _validate_gstin(self, gstin: str) -> bool:
        """Validate GSTIN format (22AAAAA0000A1Z5)."""
        pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$'
        return bool(re.match(pattern, gstin))
    
    def _validate_pan(self, pan: str) -> bool:
        """Validate PAN format (AAAAA9999A)."""
        pattern = r'^[A-Z]{5}\d{4}[A-Z]{1}$'
        return bool(re.match(pattern, pan))
    
    def _validate_cin(self, cin: str) -> bool:
        """Validate CIN format (21 characters)."""
        pattern = r'^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$'
        return bool(re.match(pattern, cin))
    
    def _validate_period(self, period: str) -> bool:
        """Validate period format (YYYY-MM or YYYY)."""
        if re.match(r'^\d{4}-\d{2}$', period):
            year, month = period.split('-')
            return 1900 <= int(year) <= 2100 and 1 <= int(month) <= 12
        elif re.match(r'^\d{4}$', period):
            return 1900 <= int(period) <= 2100
        return False
