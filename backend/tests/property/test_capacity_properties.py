"""Property-based tests for Capacity analysis.

Feature: intelli-credit
Properties tested:
- Property 15: DSCR Calculation Formula
- Property 16: DSCR Threshold Flagging
- Property 17: Capacity Score Breakdown
"""

from hypothesis import given, strategies as st, assume, settings
import pytest
from app.services.credit_engine import FiveCsAnalyzer
from app.models.financial import FinancialData, Debt


# Strategies for generating realistic financial data
positive_float = st.floats(min_value=0.01, max_value=1e9)
non_negative_float = st.floats(min_value=0.0, max_value=1e9)


@settings(max_examples=15)
@given(
    cash_flow=positive_float,
    debt_service=positive_float,
)
def test_dscr_calculation_formula(cash_flow, debt_service):
    """
    Property 15: DSCR Calculation Formula
    
    For any financial data with cash flow and debt service values,
    the calculated DSCR should equal cash flow divided by debt service.
    
    Validates: Requirements 6.1
    """
    financial_data = FinancialData(
        company_id="TEST001",
        period="2023-2024",
        revenue=cash_flow * 2,
        expenses=cash_flow,
        ebitda=cash_flow,
        net_profit=cash_flow * 0.5,
        total_assets=cash_flow * 3,
        total_liabilities=debt_service * 2,
        equity=cash_flow * 2,
        cash_flow=cash_flow,
    )
    
    # Create debt obligations that sum to debt_service
    debt_obligations = [
        Debt(
            lender="Bank A",
            amount=debt_service,
            interest_rate=10.0,
            emi=debt_service,
            outstanding=debt_service * 0.8,
        )
    ]
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_capacity(financial_data, debt_obligations)
    
    expected_dscr = cash_flow / debt_service
    assert result.dscr == pytest.approx(expected_dscr, rel=0.001)


@settings(max_examples=15)
@given(
    cash_flow=positive_float,
    debt_service=positive_float,
)
def test_dscr_threshold_flagging(cash_flow, debt_service):
    """
    Property 16: DSCR Threshold Flagging
    
    For any loan application where DSCR is below 1.25, the system should
    flag the application as having insufficient repayment capacity (score < 60).
    
    Validates: Requirements 6.2
    """
    financial_data = FinancialData(
        company_id="TEST002",
        period="2023-2024",
        revenue=cash_flow * 2,
        expenses=cash_flow,
        ebitda=cash_flow,
        net_profit=cash_flow * 0.5,
        total_assets=cash_flow * 3,
        total_liabilities=debt_service * 2,
        equity=cash_flow * 2,
        cash_flow=cash_flow,
    )
    
    debt_obligations = [
        Debt(
            lender="Bank A",
            amount=debt_service,
            interest_rate=10.0,
            emi=debt_service,
            outstanding=debt_service * 0.8,
        )
    ]
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_capacity(financial_data, debt_obligations)
    
    dscr = cash_flow / debt_service
    
    # If DSCR < 1.25, score should be < 60
    if dscr < 1.25:
        assert result.score < 60, f"DSCR {dscr} < 1.25 but score {result.score} >= 60"
    # If DSCR >= 1.25, score should be >= 60
    else:
        assert result.score >= 60, f"DSCR {dscr} >= 1.25 but score {result.score} < 60"


@settings(max_examples=15)
@given(
    cash_flow=positive_float,
    debt_service=positive_float,
)
def test_capacity_score_breakdown(cash_flow, debt_service):
    """
    Property 17: Capacity Score Breakdown
    
    For any calculated DSCR, the system should provide a breakdown showing
    cash flow components and debt obligations.
    
    Validates: Requirements 6.5
    """
    financial_data = FinancialData(
        company_id="TEST003",
        period="2023-2024",
        revenue=cash_flow * 2,
        expenses=cash_flow,
        ebitda=cash_flow,
        net_profit=cash_flow * 0.5,
        total_assets=cash_flow * 3,
        total_liabilities=debt_service * 2,
        equity=cash_flow * 2,
        cash_flow=cash_flow,
    )
    
    debt_obligations = [
        Debt(
            lender="Bank A",
            amount=debt_service,
            interest_rate=10.0,
            emi=debt_service,
            outstanding=debt_service * 0.8,
        )
    ]
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_capacity(financial_data, debt_obligations)
    
    # Verify breakdown components are present and correct
    assert result.cash_flow == pytest.approx(cash_flow, rel=0.001)
    assert result.debt_service == pytest.approx(debt_service, rel=0.001)
    assert result.dscr == pytest.approx(cash_flow / debt_service, rel=0.001)


@settings(max_examples=15)
@given(
    cash_flow=positive_float,
    num_debts=st.integers(min_value=1, max_value=5),
)
def test_capacity_score_validity_range(cash_flow, num_debts):
    """
    Property 13: Five Cs Score Validity (Capacity component)
    
    For any completed Capacity assessment, the score should be within
    the range 0 to 100 inclusive.
    
    Validates: Requirements 6.4
    """
    # Generate multiple debt obligations
    debt_obligations = [
        Debt(
            lender=f"Bank {i}",
            amount=cash_flow / num_debts,
            interest_rate=8.0 + i,
            emi=cash_flow / (num_debts * 10),
            outstanding=cash_flow / (num_debts * 2),
        )
        for i in range(num_debts)
    ]
    
    financial_data = FinancialData(
        company_id="TEST004",
        period="2023-2024",
        revenue=cash_flow * 2,
        expenses=cash_flow,
        ebitda=cash_flow,
        net_profit=cash_flow * 0.5,
        total_assets=cash_flow * 3,
        total_liabilities=cash_flow,
        equity=cash_flow * 2,
        cash_flow=cash_flow,
    )
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_capacity(financial_data, debt_obligations)
    
    # Score must be within 0-100
    assert 0 <= result.score <= 100


@settings(max_examples=15)
@given(
    cash_flow=positive_float,
    debt_service=positive_float,
)
def test_capacity_score_monotonic_with_dscr(cash_flow, debt_service):
    """
    Property: Capacity score should increase monotonically with DSCR.
    
    For any two scenarios where DSCR1 > DSCR2, the capacity score
    for scenario 1 should be greater than or equal to scenario 2.
    
    Validates: Requirements 6.1, 6.4
    """
    # Scenario 1: Higher DSCR
    financial_data_1 = FinancialData(
        company_id="TEST005A",
        period="2023-2024",
        revenue=cash_flow * 3,
        expenses=cash_flow,
        ebitda=cash_flow * 1.5,
        net_profit=cash_flow * 0.75,
        total_assets=cash_flow * 4,
        total_liabilities=debt_service,
        equity=cash_flow * 3,
        cash_flow=cash_flow * 2,  # Higher cash flow
    )
    
    # Scenario 2: Lower DSCR
    financial_data_2 = FinancialData(
        company_id="TEST005B",
        period="2023-2024",
        revenue=cash_flow * 2,
        expenses=cash_flow * 1.5,
        ebitda=cash_flow * 0.5,
        net_profit=cash_flow * 0.25,
        total_assets=cash_flow * 2,
        total_liabilities=debt_service * 2,
        equity=cash_flow,
        cash_flow=cash_flow * 0.5,  # Lower cash flow
    )
    
    debt_obligations = [
        Debt(
            lender="Bank A",
            amount=debt_service,
            interest_rate=10.0,
            emi=debt_service,
            outstanding=debt_service * 0.8,
        )
    ]
    
    analyzer = FiveCsAnalyzer()
    result_1 = analyzer.analyze_capacity(financial_data_1, debt_obligations)
    result_2 = analyzer.analyze_capacity(financial_data_2, debt_obligations)
    
    # Higher DSCR should result in higher or equal score
    assert result_1.score >= result_2.score


@settings(max_examples=15)
@given(
    cash_flow=positive_float,
)
def test_capacity_no_debt_perfect_score(cash_flow):
    """
    Property: When there are no debt obligations, capacity score should be perfect (100).
    
    Validates: Requirements 6.4
    """
    financial_data = FinancialData(
        company_id="TEST006",
        period="2023-2024",
        revenue=cash_flow * 2,
        expenses=cash_flow,
        ebitda=cash_flow,
        net_profit=cash_flow * 0.5,
        total_assets=cash_flow * 3,
        total_liabilities=0.0,
        equity=cash_flow * 3,
        cash_flow=cash_flow,
    )
    
    debt_obligations = []  # No debt
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_capacity(financial_data, debt_obligations)
    
    assert result.score == 100.0
    assert result.debt_service == 0.0
