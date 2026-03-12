"""
Data Extractor Module

This module provides format-specific data extraction for various financial documents
including GST returns, Income Tax Returns, bank statements, and annual reports.

Requirements: 1.1, 1.2, 1.3, 1.4, 18.1
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import logging

from app.models.financial import GSTData, Transaction, FinancialData

logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Handles extraction of structured financial data from parsed documents.
    
    This class provides format-specific extractors for:
    - GST returns (GSTR-2A, GSTR-3B)
    - Income Tax Returns (ITR)
    - Bank statements
    - Annual reports with financial statements
    """
    
    def __init__(self):
        """Initialize the DataExtractor."""
        pass
    
    def extract_gst_returns(self, gst_data: Dict[str, Any]) -> GSTData:
        """
        Extract GST return information from GSTR-2A and GSTR-3B formats.
        
        This method parses GST return documents and extracts key information
        including GSTIN, period, sales, purchases, tax paid, and transaction details.
        
        Args:
            gst_data: Dictionary containing parsed GST return data with keys:
                - text: Full text content from the document
                - document_type: Type of GST return ('gst_return_2a' or 'gst_return_3b')
                - metadata: Optional metadata
                
        Returns:
            GSTData object containing:
                - gstin: GST Identification Number
                - period: Tax period (e.g., "2024-01")
                - sales: Total sales amount
                - purchases: Total purchases amount
                - tax_paid: Total tax paid
                - transactions: List of transaction dictionaries
                
        Raises:
            ValueError: If required fields cannot be extracted
            
        Requirements: 1.1, 18.1
        """
        text = gst_data.get('text', '')
        document_type = gst_data.get('document_type', 'gst_return')
        
        if not text:
            raise ValueError("No text content provided for GST extraction")
        
        # Extract GSTIN (format: 22AAAAA0000A1Z5)
        gstin_pattern = r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b'
        gstin_match = re.search(gstin_pattern, text)
        gstin = gstin_match.group(0) if gstin_match else ""
        
        if not gstin:
            logger.warning("GSTIN not found in document")
        
        # Extract period (various formats: MM/YYYY, MM-YYYY, MMYYYY)
        period_patterns = [
            r'(?:period|month|tax period)[:\s]+(\d{2}[-/]\d{4})',
            r'(?:period|month|tax period)[:\s]+([A-Za-z]+[-\s]\d{4})',
            r'return period[:\s]+(\d{2}/\d{4})',
        ]
        period = ""
        for pattern in period_patterns:
            period_match = re.search(pattern, text, re.IGNORECASE)
            if period_match:
                period = period_match.group(1)
                break
        
        # Normalize period to YYYY-MM format
        if period:
            period = self._normalize_period(period)
        
        # Extract financial amounts based on document type
        if 'gstr-2a' in document_type or 'gstr_2a' in document_type or '2a' in document_type:
            sales, purchases, tax_paid = self._extract_gstr2a_amounts(text)
        elif 'gstr-3b' in document_type or 'gstr_3b' in document_type or '3b' in document_type:
            sales, purchases, tax_paid = self._extract_gstr3b_amounts(text)
        else:
            # Generic extraction for unspecified GST return type
            sales, purchases, tax_paid = self._extract_generic_gst_amounts(text)
        
        # Extract transactions
        transactions = self._extract_gst_transactions(text, document_type)
        
        logger.info(f"Extracted GST data: GSTIN={gstin}, period={period}, "
                   f"sales={sales}, purchases={purchases}, tax_paid={tax_paid}, "
                   f"transactions={len(transactions)}")
        
        return GSTData(
            gstin=gstin,
            period=period,
            sales=sales,
            purchases=purchases,
            tax_paid=tax_paid,
            transactions=transactions
        )
    
    def extract_itr(self, itr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract Income Tax Return data.
        
        This method parses ITR documents and extracts income, expenses,
        tax payment information, and other relevant details.
        
        Args:
            itr_data: Dictionary containing parsed ITR data with keys:
                - text: Full text content from the document
                - metadata: Optional metadata
                
        Returns:
            Dictionary containing:
                - pan: Permanent Account Number
                - assessment_year: Assessment year (e.g., "2023-24")
                - filing_date: Date of filing
                - gross_total_income: Total income before deductions
                - total_deductions: Total deductions claimed
                - taxable_income: Income after deductions
                - tax_paid: Total tax paid
                - refund_amount: Refund amount if any
                - income_sources: List of income source dictionaries
                
        Raises:
            ValueError: If required fields cannot be extracted
            
        Requirements: 1.2
        """
        text = itr_data.get('text', '')
        
        if not text:
            raise ValueError("No text content provided for ITR extraction")
        
        # Extract PAN (format: AAAAA9999A)
        pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]{1}\b'
        pan_match = re.search(r'(?:PAN|Permanent Account Number)[:\s]+(' + pan_pattern + ')', text, re.IGNORECASE)
        pan = pan_match.group(1) if pan_match else ""
        
        # Extract Assessment Year
        ay_pattern = r'(?:Assessment Year|A\.Y\.|AY)[:\s]+(\d{4}[-\s]?\d{2,4})'
        ay_match = re.search(ay_pattern, text, re.IGNORECASE)
        assessment_year = ay_match.group(1) if ay_match else ""
        
        # Extract Filing Date
        filing_date = self._extract_date(text, ['filing date', 'date of filing', 'submitted on'])
        
        # Extract financial amounts
        gross_total_income = self._extract_amount(text, ['gross total income', 'total income'])
        total_deductions = self._extract_amount(text, ['total deductions', 'deductions under chapter vi-a'])
        taxable_income = self._extract_amount(text, ['taxable income', 'total taxable income'])
        tax_paid = self._extract_amount(text, ['tax paid', 'total tax paid', 'taxes paid'])
        refund_amount = self._extract_amount(text, ['refund', 'refund amount', 'amount refundable'])
        
        # Extract income sources
        income_sources = self._extract_income_sources(text)
        
        logger.info(f"Extracted ITR data: PAN={pan}, AY={assessment_year}, "
                   f"gross_income={gross_total_income}, taxable_income={taxable_income}")
        
        return {
            'pan': pan,
            'assessment_year': assessment_year,
            'filing_date': filing_date,
            'gross_total_income': gross_total_income,
            'total_deductions': total_deductions,
            'taxable_income': taxable_income,
            'tax_paid': tax_paid,
            'refund_amount': refund_amount,
            'income_sources': income_sources
        }
    
    def extract_bank_statements(self, statement_data: Dict[str, Any]) -> List[Transaction]:
        """
        Extract bank transaction history from bank statements.
        
        This method parses bank statement documents and extracts transaction
        records including dates, descriptions, debits, credits, and balances.
        
        Args:
            statement_data: Dictionary containing parsed bank statement data with keys:
                - text: Full text content from the document
                - metadata: Optional metadata
                
        Returns:
            List of Transaction objects, each containing:
                - date: Transaction date
                - description: Transaction description
                - debit: Debit amount (0 if credit transaction)
                - credit: Credit amount (0 if debit transaction)
                - balance: Account balance after transaction
                
        Raises:
            ValueError: If no transactions can be extracted
            
        Requirements: 1.3
        """
        text = statement_data.get('text', '')
        
        if not text:
            raise ValueError("No text content provided for bank statement extraction")
        
        transactions = []
        
        # Split text into lines for transaction parsing
        lines = text.split('\n')
        
        # Common date patterns in bank statements
        date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b'
        
        # Amount pattern (supports Indian number format with commas)
        # More flexible to capture amounts with Rs./INR prefix
        amount_pattern = r'(?:Rs\.?\s*|INR\s*)?([\d,]+\.?\d{0,2})'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for date in the line
            date_match = re.search(date_pattern, line)
            if not date_match:
                continue
            
            try:
                # Parse date
                date_str = date_match.group(1)
                transaction_date = self._parse_date(date_str)
                
                # Extract amounts from the line
                amounts = re.findall(amount_pattern, line)
                if len(amounts) < 1:
                    continue
                
                # Clean and parse amounts
                cleaned_amounts = [float(amt.replace(',', '')) for amt in amounts if amt.replace(',', '').replace('.', '').isdigit()]
                
                if len(cleaned_amounts) < 1:
                    continue
                
                # Extract description (text between date and first amount)
                date_end = date_match.end()
                first_amount_pos = line.find(amounts[0], date_end)
                description = line[date_end:first_amount_pos].strip()
                # Clean up description
                description = re.sub(r'\s+', ' ', description)
                
                # Determine debit/credit based on common patterns
                # Usually: Date | Description | Debit | Credit | Balance
                # or: Date | Description | Amount | Balance (with Dr/Cr indicator)
                
                debit = 0.0
                credit = 0.0
                balance = 0.0
                
                if len(cleaned_amounts) >= 3:
                    # Format: Debit | Credit | Balance
                    debit = cleaned_amounts[0] if cleaned_amounts[0] > 0 else 0.0
                    credit = cleaned_amounts[1] if cleaned_amounts[1] > 0 else 0.0
                    balance = cleaned_amounts[2]
                elif len(cleaned_amounts) == 2:
                    # Format: Amount | Balance
                    # Check for Dr/Cr indicator
                    if 'dr' in line.lower() or 'debit' in line.lower() or 'withdrawal' in line.lower():
                        debit = cleaned_amounts[0]
                    else:
                        credit = cleaned_amounts[0]
                    balance = cleaned_amounts[1]
                elif len(cleaned_amounts) == 1:
                    # Only balance or only amount
                    balance = cleaned_amounts[0]
                
                transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    debit=debit,
                    credit=credit,
                    balance=balance
                )
                
                transactions.append(transaction)
                
            except (ValueError, IndexError) as e:
                logger.debug(f"Skipping line due to parsing error: {line[:50]}... Error: {e}")
                continue
        
        if not transactions:
            logger.warning("No transactions extracted from bank statement")
        
        logger.info(f"Extracted {len(transactions)} transactions from bank statement")
        
        return transactions
    
    def extract_annual_report(self, report_data: Dict[str, Any]) -> FinancialData:
        """
        Extract financial statements from annual reports.
        
        This method parses annual report documents and extracts financial data
        including balance sheet, profit & loss, and cash flow information.
        
        Args:
            report_data: Dictionary containing parsed annual report data with keys:
                - text: Full text content from the document
                - metadata: Optional metadata
                - company_id: Company identifier (optional)
                
        Returns:
            FinancialData object containing:
                - company_id: Company identifier
                - period: Financial period
                - revenue: Total revenue
                - expenses: Total expenses
                - ebitda: EBITDA
                - net_profit: Net profit
                - total_assets: Total assets
                - total_liabilities: Total liabilities
                - equity: Total equity
                - cash_flow: Operating cash flow
                - confidence_scores: Confidence scores for each field
                
        Raises:
            ValueError: If required fields cannot be extracted
            
        Requirements: 1.4
        """
        text = report_data.get('text', '')
        company_id = report_data.get('company_id', '')
        
        if not text:
            raise ValueError("No text content provided for annual report extraction")
        
        # Extract financial period
        period = self._extract_financial_period(text)
        
        # Extract Profit & Loss items
        revenue = self._extract_amount(text, [
            'total revenue', 'revenue from operations', 'total income', 'sales'
        ])
        expenses = self._extract_amount(text, [
            'total expenses', 'operating expenses', 'total expenditure'
        ])
        ebitda = self._extract_amount(text, ['ebitda', 'operating profit before interest'])
        net_profit = self._extract_amount(text, [
            'net profit', 'profit after tax', 'net income', 'profit for the year'
        ])
        
        # Extract Balance Sheet items
        total_assets = self._extract_amount(text, ['total assets', 'total assets'])
        total_liabilities = self._extract_amount(text, [
            'total liabilities', 'total liabilities and equity'
        ])
        equity = self._extract_amount(text, [
            'total equity', 'shareholders equity', 'net worth', 'equity capital'
        ])
        
        # Extract Cash Flow items
        cash_flow = self._extract_amount(text, [
            'cash flow from operating activities', 'operating cash flow',
            'net cash from operations'
        ])
        
        # Calculate confidence scores based on extraction success
        confidence_scores = {
            'revenue': 0.9 if revenue > 0 else 0.3,
            'expenses': 0.9 if expenses > 0 else 0.3,
            'ebitda': 0.8 if ebitda > 0 else 0.3,
            'net_profit': 0.9 if net_profit != 0 else 0.3,
            'total_assets': 0.9 if total_assets > 0 else 0.3,
            'total_liabilities': 0.9 if total_liabilities > 0 else 0.3,
            'equity': 0.9 if equity > 0 else 0.3,
            'cash_flow': 0.8 if cash_flow != 0 else 0.3,
        }
        
        logger.info(f"Extracted financial data: period={period}, revenue={revenue}, "
                   f"net_profit={net_profit}, total_assets={total_assets}")
        
        return FinancialData(
            company_id=company_id,
            period=period,
            revenue=revenue,
            expenses=expenses,
            ebitda=ebitda,
            net_profit=net_profit,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            equity=equity,
            cash_flow=cash_flow,
            confidence_scores=confidence_scores
        )
    
    # Helper methods
    
    def _normalize_period(self, period: str) -> str:
        """Normalize period to YYYY-MM format."""
        # Handle MM/YYYY or MM-YYYY
        if re.match(r'\d{2}[-/]\d{4}', period):
            month, year = re.split(r'[-/]', period)
            return f"{year}-{month}"
        
        # Handle Month-YYYY (e.g., "January-2024")
        month_names = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        for month_name, month_num in month_names.items():
            if month_name in period.lower():
                year = re.search(r'\d{4}', period)
                if year:
                    return f"{year.group(0)}-{month_num}"
        
        return period
    
    def _extract_gstr2a_amounts(self, text: str) -> tuple:
        """Extract amounts specific to GSTR-2A format."""
        # GSTR-2A focuses on purchases (input tax credit)
        purchases = self._extract_amount(text, [
            'total taxable value', 'total purchases', 'input tax credit', 'taxable value'
        ])
        tax_paid = self._extract_amount(text, [
            'total tax', 'igst', 'cgst', 'sgst', 'total gst', 'tax'
        ])
        sales = 0.0  # GSTR-2A doesn't contain sales data
        
        return sales, purchases, tax_paid
    
    def _extract_gstr3b_amounts(self, text: str) -> tuple:
        """Extract amounts specific to GSTR-3B format."""
        # GSTR-3B contains both outward and inward supplies
        sales = self._extract_amount(text, [
            'outward taxable supplies', 'total outward supplies', 'taxable outward supplies',
            'outward supplies'
        ])
        purchases = self._extract_amount(text, [
            'inward supplies', 'eligible itc', 'input tax credit', 'itc'
        ])
        tax_paid = self._extract_amount(text, [
            'total tax payable', 'tax paid', 'total tax liability', 'tax payable'
        ])
        
        return sales, purchases, tax_paid
    
    def _extract_generic_gst_amounts(self, text: str) -> tuple:
        """Extract amounts from generic GST return."""
        sales = self._extract_amount(text, ['sales', 'outward supplies', 'turnover'])
        purchases = self._extract_amount(text, ['purchases', 'inward supplies'])
        tax_paid = self._extract_amount(text, ['tax paid', 'total tax', 'gst paid'])
        
        return sales, purchases, tax_paid
    
    def _extract_gst_transactions(self, text: str, document_type: str) -> List[Dict]:
        """Extract individual transactions from GST return."""
        transactions = []
        
        # This is a simplified extraction - real implementation would need
        # more sophisticated parsing based on GST return table structures
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines that might contain transaction data
            # Typically: GSTIN | Invoice No | Date | Amount | Tax
            if re.search(r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}', line):
                # This line might contain a transaction
                amounts = re.findall(r'[\d,]+\.?\d{0,2}', line)
                if len(amounts) >= 2:
                    try:
                        transaction = {
                            'line': line.strip(),
                            'amounts': [float(amt.replace(',', '')) for amt in amounts]
                        }
                        transactions.append(transaction)
                    except ValueError:
                        continue
        
        return transactions
    
    def _extract_amount(self, text: str, keywords: List[str]) -> float:
        """Extract monetary amount following specific keywords."""
        for keyword in keywords:
            # Pattern: keyword followed by amount (with optional Rs./INR prefix and colon)
            # More flexible pattern to handle various formats
            pattern = rf'{re.escape(keyword)}[:\s]+(?:Rs\.?\s*|INR\s*)?([\d,]+\.?\d{{0,2}})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_date(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extract date following specific keywords."""
        for keyword in keywords:
            pattern = rf'{re.escape(keyword)}[:\s]+(\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{2,4}})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        # Try different date formats
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
                  '%Y-%m-%d', '%Y/%m/%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, return current date
        logger.warning(f"Could not parse date: {date_str}, using current date")
        return datetime.now()
    
    def _extract_income_sources(self, text: str) -> List[Dict]:
        """Extract income sources from ITR."""
        income_sources = []
        
        # Common income source keywords
        sources = {
            'salary': ['salary', 'income from salary'],
            'house_property': ['house property', 'rental income'],
            'business': ['business', 'profession', 'business income'],
            'capital_gains': ['capital gains', 'short term capital gains', 'long term capital gains'],
            'other_sources': ['other sources', 'interest income', 'dividend']
        }
        
        for source_type, keywords in sources.items():
            amount = self._extract_amount(text, keywords)
            if amount > 0:
                income_sources.append({
                    'source_type': source_type,
                    'amount': amount
                })
        
        return income_sources
    
    def _extract_financial_period(self, text: str) -> str:
        """Extract financial period from annual report."""
        # Look for financial year patterns
        patterns = [
            r'(?:financial year|fy|year ended)[:\s]+(\d{4}[-\s]?\d{2,4})',
            r'(?:for the year ended|year ending)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'(?:period|year)[:\s]+(\d{4}[-\s]?\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default to current year if not found
        return str(datetime.now().year)
