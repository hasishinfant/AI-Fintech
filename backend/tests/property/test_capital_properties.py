"""Property-based tests for Capital analysis in Five Cs framework.

Feature: intelli-credit
Properties tested:
- Property 18: Debt-to-Equity Calculation
- Property 19: Debt-to-Equity Threshold Flagging
- Property 20: Net Worth Trend Analysis
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from app.services.credit_engine import FiveCsAnalyzer
from app.models.financial import FinancialData


# Feature: intelli-credit, Property 18: Debt-to-Equity Calculation
@settings(max_examples=100)
@given(
    total_debt=st.floats(min_value=0.01, max_value=1e9),
    total_equity=st.floats(min_value=0.01, max_value=1e9),
)
def test_debt_to_equity_calculation(total_debt, total_equity):
    """For any balance sheet data with total debt and total equity values,
    the calculated Debt-to-Equity ratio should equal total debt divided by
    total equity.
    
    **Validates: Requirements 7.1**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create financial data with the given debt and equity
    financial_data = FinancialData(
        company_id="test_company",
        period="2023-2024",
        revenue=1000000.0,
        expenses=600000.0,
        ebitda=300000.0,
        net_profit=150000.0,
        total_assets=total_debt + total_equity,
        total_liabilities=total_debt,
        equity=total_equity,
        cash_flow=200000.0,
    )
    
    # Analyze capital
    result = analyzer.analyze_capital(financial_data)
    
    # Calculate expected D/E ratio
    expected_de = total_debt / total_equity
    
    # The calculated ratio should match the formula
    assert abs(result.debt_equity_ratio - expected_de) < 0.001, \
        f"Expected D/E={expected_de}, got {result.debt_equity_ratio}"


# Feature: intelli-credit, Property 19: Debt-to-Equity Threshold Flagging
@settings(max_examples=100)
@given(
    total_debt=st.floats(min_value=0.01, max_value=1e9),
    total_equity=st.floats(min_value=0.01, max_value=1e9),
)
def test_debt_to_equity_threshold_flagging(total_debt, total_equity):
    """For any loan application where Debt-to-Equity ratio exceeds 2.0,
    the system should flag the application as having weak capital structure.
    
    **Validates: Requirements 7.2**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create financial data
    financial_data = FinancialData(
        company_id="test_company",
        period="2023-2024",
        revenue=1000000.0,
        expenses=600000.0,
        ebitda=300000.0,
        net_profit=150000.0,
        total_assets=total_debt + total_equity,
        total_liabilities=total_debt,
        equity=total_equity,
        cash_flow=200000.0,
    )
    
    # Analyze capital
    result = analyzer.analyze_capital(financial_data)
    
    # Calculate D/E ratio
    de_ratio = total_debt / total_equity
    
    # Check threshold flagging
    if de_ratio > 2.0:
        # Should be flagged with lower score
        assert result.score < 60, \
            f"D/E={de_ratio} > 2.0 should result in score < 60, got {result.score}"
    elif de_ratio <= 2.0:
        # Should not be critically flagged
        assert result.score >= 40, \
            f"D/E={de_ratio} <= 2.0 should result in score >= 40, got {result.score}"


# Feature: intelli-credit, Property 20: Net Worth Trend Analysis
@settings(max_examples=100)
@given(
    year1_equity=st.floats(min_value=100000.0, max_value=1e9),
    year2_change_pct=st.floats(min_value=-0.5, max_value=0.5),
    year3_change_pct=st.floats(min_value=-0.5, max_value=0.5),
)
def test_net_worth_trend_analysis(year1_equity, year2_change_pct, year3_change_pct):
    """For any capital evaluation with financial data spanning three years,
    the system should analyze and report net worth trends over that period.
    
    **Validates: Requirements 7.3**
    """
    analyzer = FiveCsAnalyzer()
    
    # Calculate year 2 and 3 equity based on changes
    year2_equity = year1_equity * (1 + year2_change_pct)
    year3_equity = year2_equity * (1 + year3_change_pct)
    
    # Ensure all equity values are positive
    assume(year2_equity > 0)
    assume(year3_equity > 0)
    
    # Create financial data for current year (year 3)
    financial_data = FinancialData(
        company_id="test_company",
        period="2023-2024",
        revenue=1000000.0,
        expenses=600000.0,
        ebitda=300000.0,
        net_profit=150000.0,
        total_assets=year3_equity + 500000.0,
        total_liabilities=500000.0,
        equity=year3_equity,
        cash_flow=200000.0,
    )
    
    # Analyze capital
    result = analyzer.analyze_capital(financial_data)
    
    # Should return a trend value
    assert result.net_worth_trend in ["improving", "stable", "declining"], \
        f"Trend should be one of: improving, stable, declining. Got: {result.net_worth_trend}"
    
    # Net worth should match current equity
    assert abs(result.net_worth - year3_equity) < 0.001, \
        f"Net worth should be {year3_equity}, got {result.net_worth}"


# Feature: intelli-credit, Property 13: Five Cs Score Validity (Capital component)
@settings(max_examples=100)
@given(
    total_debt=st.floats(min_value=0.01, max_value=1e9),
    total_equity=st.floats(min_value=0.01, max_value=1e9),
)
def test_capital_score_validity_range(total_debt, total_equity):
    """For any completed Capital assessment, the score should be within
    the range 0 to 100 inclusive.
    
    **Validates: Requirements 7.4**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create financial data
    financial_data = FinancialData(
        company_id="test_company",
        period="2023-2024",
        revenue=1000000.0,
        expenses=600000.0,
        ebitda=300000.0,
        net_profit=150000.0,
        total_assets=total_debt + total_equity,
        total_liabilities=total_debt,
        equity=total_equity,
        cash_flow=200000.0,
    )
    
    # Analyze capital
    result = analyzer.analyze_capital(financial_data)
    
    # Score should be within 0-100
    assert 0 <= result.score <= 100, \
        f"Capital score should be 0-100, got {result.score}"


# Feature: intelli-credit, Property 7.5: Capital Adequacy Documentation
@settings(max_examples=100)
@given(
    total_debt=st.floats(min_value=0.01, max_value=1e9),
    total_equity=st.floats(min_value=0.01, max_value=1e9),
)
def test_capital_adequacy_documentation(total_debt, total_equity):
    """For any capital adequacy assessment, the system should document
    the composition of equity and debt.
    
    **Validates: Requirements 7.5**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create financial data
    financial_data = FinancialData(
        company_id="test_company",
        period="2023-2024",
        revenue=1000000.0,
        expenses=600000.0,
        ebitda=300000.0,
        net_profit=150000.0,
        total_assets=total_debt + total_equity,
        total_liabilities=total_debt,
        equity=total_equity,
        cash_flow=200000.0,
    )
    
    # Analyze capital
    result = analyzer.analyze_capital(financial_data)
    
    # Should have documented the debt and equity values
    assert result.debt_equity_ratio is not None, \
        "Debt-to-Equity ratio should be documented"
    assert result.net_worth is not None, \
        "Net worth should be documented"
    assert result.net_worth == total_equity, \
        f"Net worth should equal equity ({total_equity}), got {result.net_worth}"
