"""Property-based tests for circular trading detection.

Feature: intelli-credit
Properties tested:
- Property 7: Circular Trading Detection via Cross-Check
- Property 8: GSTR Mismatch Detection
- Property 9: Circular Trading Alert Generation
- Property 10: High-Risk Deposit Ratio Flagging
"""

from hypothesis import given, strategies as st, settings, assume, HealthCheck
import pytest
from datetime import datetime, timedelta

from app.services.data_ingestor.circular_trading_detector import CircularTradingDetector
from app.models.financial import GSTData, Transaction
from app.models.alerts import CircularTradingAlert


# Strategies for generating test data

# GST data strategies
gstin_strategy = st.just("27AABCU9603R1ZM")  # Valid GSTIN format
gst_period_strategy = st.sampled_from(["01/2024", "02/2024", "03/2024", "12/2023"])

# Amount strategies
positive_amount_strategy = st.floats(min_value=1000.0, max_value=10000000.0)
zero_or_positive_strategy = st.floats(min_value=0.0, max_value=10000000.0)

# Deposit ratio strategies (0.0 to 1.0)
deposit_ratio_strategy = st.floats(min_value=0.0, max_value=1.0)

# Transaction strategies
transaction_date_strategy = st.dates(
    min_value=datetime(2024, 1, 1).date(),
    max_value=datetime(2024, 12, 31).date()
)
transaction_amount_strategy = st.floats(min_value=100.0, max_value=1000000.0)


# Property 7: Circular Trading Detection via Cross-Check

@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
    deposit_ratio=deposit_ratio_strategy,
)
def test_circular_trading_cross_check_detection(gstin, period, gst_sales, deposit_ratio):
    """
    Property 7: Circular Trading Detection via Cross-Check
    
    For any loan application with both GST sales data and bank deposit data,
    the Data_Ingestor should perform a cross-check comparison between the
    two data sources.
    
    Validates: Requirements 3.1
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,  # Typical 50% purchase ratio
        tax_paid=gst_sales * 0.18,  # 18% GST
        transactions=[]
    )
    
    # Create bank transactions with specified deposit ratio
    bank_deposits = gst_sales * deposit_ratio
    transactions = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Customer payment",
            debit=0.0,
            credit=bank_deposits,
            balance=bank_deposits
        )
    ]
    
    # Perform cross-check
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify cross-check was performed
    assert isinstance(alert, CircularTradingAlert), "Should return CircularTradingAlert"
    assert alert.gst_sales == gst_sales, "GST sales should be recorded"
    assert alert.bank_deposits == bank_deposits, "Bank deposits should be recorded"
    
    # Verify detection logic
    if deposit_ratio < 0.70:
        assert alert.detected is True, "Should detect circular trading when deposits < 70% of sales"
    else:
        assert alert.detected is False, "Should not detect circular trading when deposits >= 70% of sales"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
    num_transactions=st.integers(min_value=1, max_value=10),
)
def test_circular_trading_multiple_transactions_aggregation(gstin, period, gst_sales, num_transactions):
    """
    Property 7: Circular Trading Detection via Cross-Check (Multiple Transactions)
    
    For any loan application with multiple bank transactions, the Data_Ingestor
    should aggregate all deposits for cross-check comparison.
    
    Validates: Requirements 3.1
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Create multiple bank transactions
    per_transaction_amount = gst_sales / num_transactions
    transactions = []
    balance = 0.0
    
    for i in range(num_transactions):
        balance += per_transaction_amount
        transactions.append(
            Transaction(
                date=datetime(2024, 1, 1) + timedelta(days=i),
                description=f"Payment {i+1}",
                debit=0.0,
                credit=per_transaction_amount,
                balance=balance
            )
        )
    
    # Perform cross-check
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify aggregation
    total_deposits = sum(t.credit for t in transactions)
    assert alert.bank_deposits == total_deposits, "Should aggregate all deposits"
    assert alert.detected is False, "Should not detect when total deposits equal sales"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
)
def test_circular_trading_ignores_debits(gstin, period, gst_sales):
    """
    Property 7: Circular Trading Detection via Cross-Check (Debit Handling)
    
    For any bank transaction data, the Data_Ingestor should only count
    credits (deposits) and ignore debits when calculating total deposits.
    
    Validates: Requirements 3.1
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Create transactions with both credits and debits
    transactions = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Customer payment",
            debit=0.0,
            credit=gst_sales * 0.8,  # 80% of sales as deposit
            balance=gst_sales * 0.8
        ),
        Transaction(
            date=datetime(2024, 1, 10),
            description="Expense payment",
            debit=gst_sales * 0.2,  # Debit should be ignored
            credit=0.0,
            balance=gst_sales * 0.6
        )
    ]
    
    # Perform cross-check
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify only credits are counted
    expected_deposits = gst_sales * 0.8
    assert alert.bank_deposits == expected_deposits, "Should only count credits, not debits"
    assert alert.detected is False, "Should not detect when deposits are 80% of sales"


# Property 8: GSTR Mismatch Detection

@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    base_sales=positive_amount_strategy,
    base_purchases=positive_amount_strategy,
    base_tax=positive_amount_strategy,
    mismatch_percentage=st.floats(min_value=0.0, max_value=0.5),  # 0-50% mismatch
)
def test_gstr_mismatch_detection_threshold(gstin, period, base_sales, base_purchases, base_tax, mismatch_percentage):
    """
    Property 8: GSTR Mismatch Detection
    
    For any loan application with both GSTR-2A and GSTR-3B data, when a
    significant mismatch exists between the two forms (>10%), the
    Data_Ingestor should flag the application for circular trading risk.
    
    Validates: Requirements 3.2
    """
    detector = CircularTradingDetector()
    
    # Create GSTR-2A data
    gstr_2a = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales,
        purchases=base_purchases,
        tax_paid=base_tax,
        transactions=[]
    )
    
    # Create GSTR-3B data with specified mismatch
    gstr_3b = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales * (1 + mismatch_percentage),
        purchases=base_purchases * (1 + mismatch_percentage),
        tax_paid=base_tax * (1 + mismatch_percentage),
        transactions=[]
    )
    
    # Compare versions
    discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
    
    # Verify detection logic
    if mismatch_percentage > 0.10:  # 10% threshold
        assert len(discrepancies) > 0, "Should detect mismatch when difference > 10%"
    else:
        assert len(discrepancies) == 0, "Should not detect mismatch when difference <= 10%"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    base_sales=positive_amount_strategy,
    base_purchases=positive_amount_strategy,
    base_tax=positive_amount_strategy,
)
def test_gstr_mismatch_detection_individual_fields(gstin, period, base_sales, base_purchases, base_tax):
    """
    Property 8: GSTR Mismatch Detection (Individual Fields)
    
    For any GSTR comparison, the Data_Ingestor should detect mismatches
    in individual fields (sales, purchases, tax) independently.
    
    Validates: Requirements 3.2
    """
    detector = CircularTradingDetector()
    
    # Create GSTR-2A data
    gstr_2a = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales,
        purchases=base_purchases,
        tax_paid=base_tax,
        transactions=[]
    )
    
    # Create GSTR-3B with only sales mismatch (20% difference)
    gstr_3b = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales * 1.20,  # 20% mismatch
        purchases=base_purchases,  # No mismatch
        tax_paid=base_tax,  # No mismatch
        transactions=[]
    )
    
    # Compare versions
    discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
    
    # Verify only sales mismatch is detected
    assert len(discrepancies) == 1, "Should detect only the sales mismatch"
    assert discrepancies[0].field == "sales", "Should identify sales as the mismatched field"
    assert abs(discrepancies[0].percentage_diff - 20.0) < 0.01, "Should calculate correct percentage difference"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    base_sales=positive_amount_strategy,
    base_purchases=positive_amount_strategy,
    base_tax=positive_amount_strategy,
)
def test_gstr_mismatch_detection_multiple_fields(gstin, period, base_sales, base_purchases, base_tax):
    """
    Property 8: GSTR Mismatch Detection (Multiple Fields)
    
    For any GSTR comparison with multiple field mismatches, the
    Data_Ingestor should detect all significant mismatches.
    
    Validates: Requirements 3.2
    """
    detector = CircularTradingDetector()
    
    # Create GSTR-2A data
    gstr_2a = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales,
        purchases=base_purchases,
        tax_paid=base_tax,
        transactions=[]
    )
    
    # Create GSTR-3B with multiple mismatches (all 20% different)
    gstr_3b = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales * 1.20,
        purchases=base_purchases * 1.20,
        tax_paid=base_tax * 1.20,
        transactions=[]
    )
    
    # Compare versions
    discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
    
    # Verify all mismatches are detected
    assert len(discrepancies) == 3, "Should detect all three field mismatches"
    fields = {d.field for d in discrepancies}
    assert fields == {"sales", "purchases", "tax_paid"}, "Should detect all three fields"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    base_sales=positive_amount_strategy,
    base_purchases=positive_amount_strategy,
    base_tax=positive_amount_strategy,
)
def test_gstr_mismatch_detection_negative_differences(gstin, period, base_sales, base_purchases, base_tax):
    """
    Property 8: GSTR Mismatch Detection (Negative Differences)
    
    For any GSTR comparison where GSTR-3B values are lower than GSTR-2A,
    the Data_Ingestor should still detect the mismatch using absolute
    percentage difference.
    
    Validates: Requirements 3.2
    """
    detector = CircularTradingDetector()
    
    # Create GSTR-2A data
    gstr_2a = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales,
        purchases=base_purchases,
        tax_paid=base_tax,
        transactions=[]
    )
    
    # Create GSTR-3B with lower values (20% lower)
    gstr_3b = GSTData(
        gstin=gstin,
        period=period,
        sales=base_sales * 0.80,  # 20% lower
        purchases=base_purchases,
        tax_paid=base_tax,
        transactions=[]
    )
    
    # Compare versions
    discrepancies = detector.compare_gstr_versions(gstr_2a, gstr_3b)
    
    # Verify mismatch is detected despite negative difference
    assert len(discrepancies) == 1, "Should detect mismatch even with negative difference"
    assert discrepancies[0].field == "sales", "Should identify sales as mismatched"
    assert abs(discrepancies[0].percentage_diff - 20.0) < 0.01, "Should use absolute percentage difference"
    assert abs(discrepancies[0].difference - (-base_sales * 0.20)) < 1.0, "Should record negative difference"


# Property 9: Circular Trading Alert Generation

@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
    deposit_ratio=deposit_ratio_strategy,
)
def test_circular_trading_alert_generation(gstin, period, gst_sales, deposit_ratio):
    """
    Property 9: Circular Trading Alert Generation
    
    For any detected circular trading indicator, the system should generate
    an alert containing specific discrepancies and amounts.
    
    Validates: Requirements 3.3
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Create bank transactions
    bank_deposits = gst_sales * deposit_ratio
    transactions = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Payment",
            debit=0.0,
            credit=bank_deposits,
            balance=bank_deposits
        )
    ]
    
    # Generate alert
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify alert structure
    assert isinstance(alert, CircularTradingAlert), "Should return CircularTradingAlert"
    assert isinstance(alert.detected, bool), "detected should be boolean"
    assert alert.severity in ["high", "medium", "low"], "severity should be valid"
    assert isinstance(alert.discrepancies, list), "discrepancies should be a list"
    assert isinstance(alert.gst_sales, float), "gst_sales should be float"
    assert isinstance(alert.bank_deposits, float), "bank_deposits should be float"
    assert isinstance(alert.mismatch_percentage, float), "mismatch_percentage should be float"
    
    # Verify alert contains specific amounts
    if alert.detected:
        assert len(alert.discrepancies) > 0, "Alert should contain discrepancies when detected"
        # Check that amounts are mentioned in discrepancies (with formatting)
        discrepancy_text = " ".join(alert.discrepancies)
        # The amounts may be formatted with commas and decimals, so check for the numeric part
        assert "₹" in discrepancy_text or str(int(gst_sales)) in discrepancy_text or str(int(bank_deposits)) in discrepancy_text, \
            "Alert should mention specific amounts"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
)
def test_circular_trading_alert_severity_levels(gstin, period, gst_sales):
    """
    Property 9: Circular Trading Alert Generation (Severity Levels)
    
    For any detected circular trading, the system should assign appropriate
    severity levels based on the deposit ratio.
    
    Validates: Requirements 3.3
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Test high severity (< 50% deposits)
    transactions_high = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Payment",
            debit=0.0,
            credit=gst_sales * 0.40,
            balance=gst_sales * 0.40
        )
    ]
    alert_high = detector.detect_circular_trading(gst_data, transactions_high)
    assert alert_high.severity == "high", "Should be high severity when deposits < 50%"
    assert alert_high.detected is True, "Should be detected as high risk"
    
    # Test medium severity (50-70% deposits)
    transactions_medium = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Payment",
            debit=0.0,
            credit=gst_sales * 0.60,
            balance=gst_sales * 0.60
        )
    ]
    alert_medium = detector.detect_circular_trading(gst_data, transactions_medium)
    assert alert_medium.severity == "medium", "Should be medium severity when deposits 50-70%"
    assert alert_medium.detected is True, "Should be detected as medium risk"
    
    # Test low severity (>= 70% deposits)
    transactions_low = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Payment",
            debit=0.0,
            credit=gst_sales * 0.80,
            balance=gst_sales * 0.80
        )
    ]
    alert_low = detector.detect_circular_trading(gst_data, transactions_low)
    assert alert_low.severity == "low", "Should be low severity when deposits >= 70%"
    assert alert_low.detected is False, "Should not be detected as risk"


# Property 10: High-Risk Deposit Ratio Flagging

@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
    deposit_ratio=deposit_ratio_strategy,
)
def test_high_risk_deposit_ratio_flagging(gstin, period, gst_sales, deposit_ratio):
    """
    Property 10: High-Risk Deposit Ratio Flagging
    
    For any loan application where bank deposits are less than 70% of
    reported GST sales, the system should mark this as a high-risk indicator.
    
    Validates: Requirements 3.4
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Create bank transactions with specified ratio
    bank_deposits = gst_sales * deposit_ratio
    transactions = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Payment",
            debit=0.0,
            credit=bank_deposits,
            balance=bank_deposits
        )
    ]
    
    # Detect circular trading
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify high-risk flagging
    if deposit_ratio < 0.70:
        assert alert.detected is True, "Should flag as high-risk when deposits < 70% of sales"
    else:
        assert alert.detected is False, "Should not flag as high-risk when deposits >= 70% of sales"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
)
def test_high_risk_deposit_ratio_boundary_70_percent(gstin, period, gst_sales):
    """
    Property 10: High-Risk Deposit Ratio Flagging (Boundary at 70%)
    
    For any loan application where bank deposits are approximately 70% of GST sales,
    the system should NOT flag as high-risk (boundary condition).
    
    Validates: Requirements 3.4
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Create bank transactions with exactly 70% deposits
    # Use a slightly higher ratio to account for floating-point precision
    transactions = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Payment",
            debit=0.0,
            credit=gst_sales * 0.701,  # Slightly above 70% to avoid floating-point issues
            balance=gst_sales * 0.701
        )
    ]
    
    # Detect circular trading
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify boundary condition
    assert alert.detected is False, "Should not flag as high-risk when deposits >= 70%"
    assert alert.severity == "low", "Should be low severity when deposits >= 70%"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
)
def test_high_risk_deposit_ratio_just_below_threshold(gstin, period, gst_sales):
    """
    Property 10: High-Risk Deposit Ratio Flagging (Just Below 70%)
    
    For any loan application where bank deposits are just below 70% of GST sales,
    the system should flag as high-risk.
    
    Validates: Requirements 3.4
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Create bank transactions with 69.9% deposits (just below threshold)
    transactions = [
        Transaction(
            date=datetime(2024, 1, 5),
            description="Payment",
            debit=0.0,
            credit=gst_sales * 0.699,
            balance=gst_sales * 0.699
        )
    ]
    
    # Detect circular trading
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify flagging just below threshold
    assert alert.detected is True, "Should flag as high-risk when deposits < 70%"
    assert alert.severity in ["medium", "high"], "Should be medium or high severity"


@settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
@given(
    gstin=gstin_strategy,
    period=gst_period_strategy,
    gst_sales=positive_amount_strategy,
)
def test_high_risk_deposit_ratio_zero_deposits(gstin, period, gst_sales):
    """
    Property 10: High-Risk Deposit Ratio Flagging (Zero Deposits)
    
    For any loan application with zero bank deposits, the system should
    flag as high-risk (most severe case).
    
    Validates: Requirements 3.4
    """
    detector = CircularTradingDetector()
    
    # Create GST data
    gst_data = GSTData(
        gstin=gstin,
        period=period,
        sales=gst_sales,
        purchases=gst_sales * 0.5,
        tax_paid=gst_sales * 0.18,
        transactions=[]
    )
    
    # Create empty transaction list (zero deposits)
    transactions = []
    
    # Detect circular trading
    alert = detector.detect_circular_trading(gst_data, transactions)
    
    # Verify high-risk flagging for zero deposits
    assert alert.detected is True, "Should flag as high-risk when deposits are zero"
    assert alert.severity == "high", "Should be high severity when deposits are zero"
    assert alert.bank_deposits == 0.0, "Bank deposits should be zero"
