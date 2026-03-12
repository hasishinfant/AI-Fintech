"""Unit tests for CircularTradingDetector."""

import pytest
from datetime import datetime
from app.services.data_ingestor import CircularTradingDetector, Discrepancy
from app.models.financial import GSTData, Transaction
from app.models.alerts import CircularTradingAlert


class TestCircularTradingDetector:
    """Test suite for CircularTradingDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a CircularTradingDetector instance."""
        return CircularTradingDetector()
    
    @pytest.fixture
    def sample_gst_data(self):
        """Create sample GST data."""
        return GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
    
    @pytest.fixture
    def sample_bank_transactions(self):
        """Create sample bank transactions with 80% deposit ratio."""
        return [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Customer payment",
                debit=0.0,
                credit=400000.0,
                balance=400000.0
            ),
            Transaction(
                date=datetime(2024, 1, 15),
                description="Customer payment",
                debit=0.0,
                credit=400000.0,
                balance=800000.0
            )
        ]
    
    # Test detect_circular_trading method
    
    def test_detect_circular_trading_no_alert_high_deposits(self, detector, sample_gst_data):
        """Test that no alert is generated when deposits are >= 70% of sales."""
        # Create transactions with 80% deposit ratio
        transactions = [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Payment",
                debit=0.0,
                credit=800000.0,
                balance=800000.0
            )
        ]
        
        alert = detector.detect_circular_trading(sample_gst_data, transactions)
        
        assert alert.detected is False
        assert alert.severity == "low"
        assert alert.gst_sales == 1000000.0
        assert alert.bank_deposits == 800000.0
        assert len(alert.discrepancies) == 0
    
    def test_detect_circular_trading_medium_severity(self, detector, sample_gst_data):
        """Test medium severity alert when deposits are 50-70% of sales."""
        # Create transactions with 60% deposit ratio
        transactions = [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Payment",
                debit=0.0,
                credit=600000.0,
                balance=600000.0
            )
        ]
        
        alert = detector.detect_circular_trading(sample_gst_data, transactions)
        
        assert alert.detected is True
        assert alert.severity == "medium"
        assert alert.gst_sales == 1000000.0
        assert alert.bank_deposits == 600000.0
        assert len(alert.discrepancies) > 0
        assert "60.0%" in alert.discrepancies[0]
    
    def test_detect_circular_trading_high_severity(self, detector, sample_gst_data):
        """Test high severity alert when deposits are < 50% of sales."""
        # Create transactions with 40% deposit ratio
        transactions = [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Payment",
                debit=0.0,
                credit=400000.0,
                balance=400000.0
            )
        ]
        
        alert = detector.detect_circular_trading(sample_gst_data, transactions)
        
        assert alert.detected is True
        assert alert.severity == "high"
        assert alert.gst_sales == 1000000.0
        assert alert.bank_deposits == 400000.0
        assert len(alert.discrepancies) >= 3
        assert "CRITICAL" in alert.discrepancies[2]
    
    def test_detect_circular_trading_exactly_70_percent(self, detector, sample_gst_data):
        """Test boundary case: exactly 70% deposits (should not trigger alert)."""
        transactions = [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Payment",
                debit=0.0,
                credit=700000.0,
                balance=700000.0
            )
        ]
        
        alert = detector.detect_circular_trading(sample_gst_data, transactions)
        
        assert alert.detected is False
        assert alert.severity == "low"
    
    def test_detect_circular_trading_zero_sales(self, detector):
        """Test edge case: zero GST sales."""
        gst_data = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=0.0,
            purchases=500000.0,
            tax_paid=0.0,
            transactions=[]
        )
        transactions = [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Payment",
                debit=0.0,
                credit=100000.0,
                balance=100000.0
            )
        ]
        
        alert = detector.detect_circular_trading(gst_data, transactions)
        
        assert alert.gst_sales == 0.0
        assert alert.bank_deposits == 100000.0
        assert alert.mismatch_percentage == 0.0
    
    def test_detect_circular_trading_no_deposits(self, detector, sample_gst_data):
        """Test edge case: no bank deposits."""
        transactions = []
        
        alert = detector.detect_circular_trading(sample_gst_data, transactions)
        
        assert alert.detected is True
        assert alert.severity == "high"
        assert alert.bank_deposits == 0.0
        assert "0.0%" in alert.discrepancies[0]
    
    def test_detect_circular_trading_multiple_transactions(self, detector, sample_gst_data):
        """Test with multiple bank transactions."""
        transactions = [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Payment 1",
                debit=0.0,
                credit=200000.0,
                balance=200000.0
            ),
            Transaction(
                date=datetime(2024, 1, 10),
                description="Payment 2",
                debit=0.0,
                credit=300000.0,
                balance=500000.0
            ),
            Transaction(
                date=datetime(2024, 1, 15),
                description="Payment 3",
                debit=0.0,
                credit=250000.0,
                balance=750000.0
            )
        ]
        
        alert = detector.detect_circular_trading(sample_gst_data, transactions)
        
        assert alert.bank_deposits == 750000.0
        assert alert.detected is False
    
    def test_detect_circular_trading_ignores_debits(self, detector, sample_gst_data):
        """Test that debit transactions are ignored in deposit calculation."""
        transactions = [
            Transaction(
                date=datetime(2024, 1, 5),
                description="Payment received",
                debit=0.0,
                credit=800000.0,
                balance=800000.0
            ),
            Transaction(
                date=datetime(2024, 1, 10),
                description="Payment made",
                debit=200000.0,
                credit=0.0,
                balance=600000.0
            )
        ]
        
        alert = detector.detect_circular_trading(sample_gst_data, transactions)
        
        # Should only count credits (800000), not subtract debits
        assert alert.bank_deposits == 800000.0
        assert alert.detected is False
    
    # Test compare_gstr_versions method
    
    def test_compare_gstr_versions_no_discrepancies(self, detector):
        """Test when GSTR-2A and GSTR-3B match perfectly."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        assert len(discrepancies) == 0
    
    def test_compare_gstr_versions_minor_differences(self, detector):
        """Test when differences are below threshold (10%)."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1050000.0,  # 5% difference
            purchases=510000.0,  # 2% difference
            tax_paid=185000.0,  # 2.8% difference
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        assert len(discrepancies) == 0
    
    def test_compare_gstr_versions_significant_purchase_mismatch(self, detector):
        """Test when purchases differ by more than 10%."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=600000.0,  # 20% difference
            tax_paid=180000.0,
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        assert len(discrepancies) == 1
        assert discrepancies[0].field == "purchases"
        assert discrepancies[0].gstr_2a_value == 500000.0
        assert discrepancies[0].gstr_3b_value == 600000.0
        assert discrepancies[0].difference == 100000.0
        assert discrepancies[0].percentage_diff == 20.0
    
    def test_compare_gstr_versions_significant_sales_mismatch(self, detector):
        """Test when sales differ by more than 10%."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1200000.0,  # 20% difference
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        assert len(discrepancies) == 1
        assert discrepancies[0].field == "sales"
        assert discrepancies[0].difference == 200000.0
    
    def test_compare_gstr_versions_significant_tax_mismatch(self, detector):
        """Test when tax paid differs by more than 10%."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=220000.0,  # 22% difference
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        assert len(discrepancies) == 1
        assert discrepancies[0].field == "tax_paid"
        assert discrepancies[0].difference == 40000.0
    
    def test_compare_gstr_versions_multiple_mismatches(self, detector):
        """Test when multiple fields have significant mismatches."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1200000.0,  # 20% difference
            purchases=600000.0,  # 20% difference
            tax_paid=220000.0,  # 22% difference
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        assert len(discrepancies) == 3
        fields = [d.field for d in discrepancies]
        assert "purchases" in fields
        assert "sales" in fields
        assert "tax_paid" in fields
    
    def test_compare_gstr_versions_exactly_10_percent_threshold(self, detector):
        """Test boundary case: exactly 10% difference (should trigger alert)."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1100000.0,  # Exactly 10% difference
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        # Should not trigger since we use > threshold, not >=
        assert len(discrepancies) == 0
    
    def test_compare_gstr_versions_zero_values(self, detector):
        """Test edge case: zero values in GSTR-2A."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=0.0,
            purchases=0.0,
            tax_paid=0.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=100000.0,
            purchases=50000.0,
            tax_paid=18000.0,
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        # Should not crash, but won't detect discrepancies due to zero denominator
        assert len(discrepancies) == 0
    
    def test_compare_gstr_versions_negative_difference(self, detector):
        """Test when GSTR-3B values are lower than GSTR-2A."""
        gstr_2a = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=1000000.0,
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        gstr_3b = GSTData(
            gstin="29ABCDE1234F1Z5",
            period="2024-01",
            sales=800000.0,  # 20% lower
            purchases=500000.0,
            tax_paid=180000.0,
            transactions=[]
        )
        
        discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
        
        assert len(discrepancies) == 1
        assert discrepancies[0].field == "sales"
        assert discrepancies[0].difference == -200000.0  # Negative difference
        assert discrepancies[0].percentage_diff == 20.0  # Absolute percentage
