"""
Data Ingestor Validation Script

This script validates the Data Ingestor components by testing them with
sample documents and data. It verifies:
1. Document parsing functionality
2. Data extraction from various document types
3. Data normalization
4. Circular trading detection
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_ingestor.document_parser import DocumentParser
from app.services.data_ingestor.data_extractor import DataExtractor
from app.services.data_ingestor.data_normalizer import DataNormalizer
from app.services.data_ingestor.circular_trading_detector import CircularTradingDetector
from app.models.financial import GSTData, Transaction


def test_document_type_detection():
    """Test document type detection with sample text"""
    print("\n" + "="*80)
    print("TEST 1: Document Type Detection")
    print("="*80)
    
    parser = DocumentParser()
    
    test_cases = [
        ("GSTR-3B Return for the month of January 2024", "gst_return_3b"),
        ("Income Tax Return for Assessment Year 2023-24", "itr"),
        ("Bank Statement - Account Statement with Opening Balance and Closing Balance showing Debit Credit transactions", "bank_statement"),
        ("Annual Report 2023 - Balance Sheet and Profit & Loss Statement", "annual_report"),
    ]
    
    passed = 0
    for text, expected_type in test_cases:
        detected_type = parser.detect_document_type(text)
        status = "✓ PASS" if detected_type == expected_type else "✗ FAIL"
        print(f"{status}: Expected '{expected_type}', got '{detected_type}'")
        print(f"  Text: {text[:60]}...")
        if detected_type == expected_type:
            passed += 1
    
    print(f"\nResult: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_gst_data_extraction():
    """Test GST data extraction"""
    print("\n" + "="*80)
    print("TEST 2: GST Data Extraction")
    print("="*80)
    
    extractor = DataExtractor()
    
    # Sample GSTR-3B text
    sample_text = """
    GSTR-3B Summary Return
    GSTIN: 29ABCDE1234F1Z5
    Tax Period: January 2024
    
    Outward Supplies:
    Taxable Value: Rs. 5,000,000
    Integrated Tax: Rs. 900,000
    Central Tax: Rs. 450,000
    State Tax: Rs. 450,000
    
    Input Tax Credit:
    Integrated Tax: Rs. 300,000
    Central Tax: Rs. 150,000
    State Tax: Rs. 150,000
    """
    
    parsed_doc = {
        'text': sample_text,
        'document_type': 'gst_return_3b'
    }
    
    try:
        gst_data = extractor.extract_gst_returns(parsed_doc)
        print(f"✓ PASS: GST data extracted successfully")
        print(f"  GSTIN: {gst_data.gstin}")
        print(f"  Period: {gst_data.period}")
        print(f"  Sales: Rs. {gst_data.sales:,.2f}")
        print(f"  Tax Paid: Rs. {gst_data.tax_paid:,.2f}")
        return True
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        return False


def test_bank_statement_extraction():
    """Test bank statement extraction"""
    print("\n" + "="*80)
    print("TEST 3: Bank Statement Extraction")
    print("="*80)
    
    extractor = DataExtractor()
    
    # Sample bank statement text
    sample_text = """
    Bank Statement
    Account Number: 1234567890
    Period: January 2024
    
    Date        Description                 Debit       Credit      Balance
    01/01/2024  Opening Balance                                     1,000,000
    05/01/2024  Customer Payment                        500,000     1,500,000
    10/01/2024  Supplier Payment            300,000                 1,200,000
    15/01/2024  Salary Payment              200,000                 1,000,000
    20/01/2024  Customer Payment                        750,000     1,750,000
    """
    
    parsed_doc = {
        'text': sample_text,
        'document_type': 'bank_statement'
    }
    
    try:
        transactions = extractor.extract_bank_statements(parsed_doc)
        print(f"✓ PASS: Bank statement extracted successfully")
        print(f"  Transactions found: {len(transactions)}")
        if transactions:
            print(f"  Sample transaction: {transactions[0].description}")
            print(f"    Date: {transactions[0].date}")
            print(f"    Credit: Rs. {transactions[0].credit:,.2f}")
        return True
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        return False


def test_data_normalization():
    """Test data normalization"""
    print("\n" + "="*80)
    print("TEST 4: Data Normalization")
    print("="*80)
    
    normalizer = DataNormalizer()
    
    # Sample raw GST data
    raw_data = {
        'gstin': '29ABCDE1234F1Z5',
        'period': 'January 2024',
        'sales': 5000000.0,
        'purchases': 3000000.0,
        'tax_paid': 900000.0,
    }
    
    try:
        normalized = normalizer.normalize_financial_data(raw_data, 'gst_return')
        print(f"✓ PASS: Data normalized successfully")
        print(f"  Company ID: {normalized['company_id']}")
        print(f"  Period: {normalized['period']}")
        print(f"  Revenue: Rs. {normalized['revenue']:,.2f}")
        print(f"  Source Type: {normalized['source_type']}")
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        return False


def test_circular_trading_detection():
    """Test circular trading detection"""
    print("\n" + "="*80)
    print("TEST 5: Circular Trading Detection")
    print("="*80)
    
    detector = CircularTradingDetector()
    
    # Test case 1: Normal case (no circular trading)
    gst_data_normal = GSTData(
        gstin='29ABCDE1234F1Z5',
        period='2024-01',
        sales=5000000.0,
        purchases=3000000.0,
        tax_paid=900000.0,
        transactions=[]
    )
    
    bank_data_normal = [
        Transaction(
            date=datetime(2024, 1, 5),
            description='Customer Payment',
            debit=0.0,
            credit=4500000.0,  # 90% of sales
            balance=4500000.0
        )
    ]
    
    alert_normal = detector.detect_circular_trading(gst_data_normal, bank_data_normal)
    status1 = "✓ PASS" if not alert_normal.detected else "✗ FAIL"
    print(f"{status1}: Normal case - No circular trading detected")
    print(f"  GST Sales: Rs. {gst_data_normal.sales:,.2f}")
    print(f"  Bank Deposits: Rs. {sum(t.credit for t in bank_data_normal):,.2f}")
    print(f"  Ratio: {(sum(t.credit for t in bank_data_normal) / gst_data_normal.sales * 100):.1f}%")
    
    # Test case 2: Suspicious case (circular trading)
    gst_data_suspicious = GSTData(
        gstin='29ABCDE1234F1Z5',
        period='2024-01',
        sales=5000000.0,
        purchases=3000000.0,
        tax_paid=900000.0,
        transactions=[]
    )
    
    bank_data_suspicious = [
        Transaction(
            date=datetime(2024, 1, 5),
            description='Customer Payment',
            debit=0.0,
            credit=3000000.0,  # Only 60% of sales
            balance=3000000.0
        )
    ]
    
    alert_suspicious = detector.detect_circular_trading(gst_data_suspicious, bank_data_suspicious)
    status2 = "✓ PASS" if alert_suspicious.detected else "✗ FAIL"
    print(f"\n{status2}: Suspicious case - Circular trading detected")
    print(f"  GST Sales: Rs. {gst_data_suspicious.sales:,.2f}")
    print(f"  Bank Deposits: Rs. {sum(t.credit for t in bank_data_suspicious):,.2f}")
    print(f"  Ratio: {(sum(t.credit for t in bank_data_suspicious) / gst_data_suspicious.sales * 100):.1f}%")
    print(f"  Severity: {alert_suspicious.severity}")
    
    return not alert_normal.detected and alert_suspicious.detected


def main():
    """Run all validation tests"""
    print("\n" + "="*80)
    print("DATA INGESTOR VALIDATION")
    print("="*80)
    print("This script validates the Data Ingestor components with sample data.")
    
    results = []
    
    # Run all tests
    results.append(("Document Type Detection", test_document_type_detection()))
    results.append(("GST Data Extraction", test_gst_data_extraction()))
    results.append(("Bank Statement Extraction", test_bank_statement_extraction()))
    results.append(("Data Normalization", test_data_normalization()))
    results.append(("Circular Trading Detection", test_circular_trading_detection()))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All Data Ingestor validation tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
