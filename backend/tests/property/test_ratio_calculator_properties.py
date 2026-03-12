"""Property-based tests for RatioCalculator class."""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime
from app.services.credit_engine import RatioCalculator
from app.models.financial import Asset


# Feature: intelli-credit, Property 38: Financial Ratio Calculation Set
@settings(max_examples=10, suppress_health_check=[HealthCheck.data_too_large])
@given(
    cash_flow=st.floats(min_value=0.01, max_value=1e8),
    debt_service=st.floats(min_value=0.01, max_value=1e8),
    total_debt=st.floats(min_value=0.01, max_value=1e8),
    total_equity=st.floats(min_value=0.01, max_value=1e8),
    loan_amount=st.floats(min_value=0.01, max_value=1e8),
    collateral_value=st.floats(min_value=0.01, max_value=1e8),
)
def test_financial_ratio_calculation_set(
    cash_flow, debt_service, total_debt, total_equity, loan_amount, collateral_value
):
    """For any financial statements provided, the Credit_Engine SHALL calculate
    all three core ratios: DSCR, Debt-to-Equity, and LTV.
    
    **Validates: Requirements 16.1**
    """
    calculator = RatioCalculator()
    
    # Calculate all three ratios
    dscr_result = calculator.calculate_dscr(cash_flow, debt_service)
    de_result = calculator.calculate_debt_equity_ratio(total_debt, total_equity)
    ltv_result = calculator.calculate_ltv(loan_amount, collateral_value)
    
    # All ratios should be calculated
    assert dscr_result.ratio_name == "DSCR"
    assert de_result.ratio_name == "Debt-to-Equity"
    assert ltv_result.ratio_name == "LTV"
    
    # All ratios should have numeric values
    assert isinstance(dscr_result.value, (int, float))
    assert isinstance(de_result.value, (int, float))
    assert isinstance(ltv_result.value, (int, float))


# Feature: intelli-credit, Property 39: Accounting Period Consistency
@settings(max_examples=15)
@given(
    period=st.sampled_from(["annual", "quarterly", "monthly"]),
    num_periods=st.integers(min_value=2, max_value=5),
)
def test_accounting_period_consistency(period, num_periods):
    """For any set of ratio calculations, all ratios should use the same
    consistent accounting period.
    
    **Validates: Requirements 16.2**
    """
    from app.models.financial import FinancialData
    
    calculator = RatioCalculator()
    
    # Create financial data with consistent periods
    data_list = []
    for i in range(num_periods):
        data = FinancialData(
            company_id=f"comp{i}",
            period=period,
            revenue=1000000.0 + (i * 100000),
            expenses=800000.0 + (i * 80000),
            ebitda=200000.0 + (i * 20000),
            net_profit=100000.0 + (i * 10000),
            total_assets=5000000.0 + (i * 500000),
            total_liabilities=2000000.0 + (i * 200000),
            equity=3000000.0 + (i * 300000),
            cash_flow=150000.0 + (i * 15000),
        )
        data_list.append(data)
    
    # Verify consistency
    is_consistent = calculator.verify_accounting_period_consistency(data_list)
    
    assert is_consistent is True


# Feature: intelli-credit, Property 40: Industry Benchmark Comparison
@settings(max_examples=15)
@given(
    industry=st.sampled_from(["manufacturing", "services", "retail"]),
    dscr_value=st.floats(min_value=0.5, max_value=5.0),
)
def test_industry_benchmark_comparison(industry, dscr_value):
    """For any calculated financial ratios, the system should compare them
    against industry benchmarks.
    
    **Validates: Requirements 16.3**
    """
    calculator = RatioCalculator()
    
    # Calculate ratio with industry
    result = calculator.calculate_dscr(
        cash_flow=dscr_value * 100000,
        debt_service=100000.0,
        industry=industry,
    )
    
    # Benchmark should be set for known industries
    assert result.benchmark is not None
    assert result.benchmark_source is not None
    assert industry.lower() in ["manufacturing", "services", "retail"]


# Feature: intelli-credit, Property 41: Three-Year Trend Calculation
@settings(max_examples=10, suppress_health_check=[HealthCheck.data_too_large])
@given(
    year1_value=st.floats(min_value=0.5, max_value=5.0),
    year2_change_pct=st.floats(min_value=-0.5, max_value=0.5),
    year3_change_pct=st.floats(min_value=-0.5, max_value=0.5),
)
def test_three_year_trend_calculation(year1_value, year2_change_pct, year3_change_pct):
    """For any ratio trend analysis, the system should calculate year-over-year
    changes for the past three years.
    
    **Validates: Requirements 16.4**
    """
    calculator = RatioCalculator()
    
    # Create three-year trend data
    year2_value = year1_value * (1 + year2_change_pct)
    year3_value = year2_value * (1 + year3_change_pct)
    
    # Ensure all values are positive
    assume(year2_value > 0)
    assume(year3_value > 0)
    
    historical_data = [
        ("2022", year1_value),
        ("2023", year2_value),
        ("2024", year3_value),
    ]
    
    values, trend_direction = calculator.calculate_three_year_trend(
        historical_data, "DSCR"
    )
    
    # Should return all three values
    assert len(values) == 3
    assert abs(values[0] - year1_value) < 0.001
    assert abs(values[1] - year2_value) < 0.001
    assert abs(values[2] - year3_value) < 0.001
    
    # Trend direction should be one of the valid options
    assert trend_direction in ["improving", "stable", "declining"]


# Feature: intelli-credit, Property 42: Out-of-Range Ratio Flagging
@settings(max_examples=15)
@given(
    dscr_value=st.floats(min_value=0.1, max_value=10.0),
)
def test_out_of_range_ratio_flagging_dscr(dscr_value):
    """For any calculated ratio that falls outside acceptable ranges, the system
    should flag it with a severity indicator.
    
    **Validates: Requirements 16.5**
    """
    calculator = RatioCalculator()
    
    # Calculate DSCR
    result = calculator.calculate_dscr(
        cash_flow=dscr_value * 100000,
        debt_service=100000.0,
    )
    
    # Check flagging logic
    if dscr_value < 1.25:
        # Should be flagged
        assert result.is_flagged is True
        assert result.severity in ["high", "medium"]
    elif dscr_value > 3.0:
        # Should be flagged
        assert result.is_flagged is True
        assert result.severity == "low"
    else:
        # Should not be flagged
        assert result.is_flagged is False


# Feature: intelli-credit, Property 42: Out-of-Range Ratio Flagging (Debt-to-Equity)
@settings(max_examples=15)
@given(
    de_ratio=st.floats(min_value=0.1, max_value=5.0),
)
def test_out_of_range_ratio_flagging_debt_equity(de_ratio):
    """For any calculated Debt-to-Equity ratio that falls outside acceptable
    ranges, the system should flag it with a severity indicator.
    
    **Validates: Requirements 16.5**
    """
    calculator = RatioCalculator()
    
    # Calculate Debt-to-Equity
    result = calculator.calculate_debt_equity_ratio(
        total_debt=de_ratio * 100000,
        total_equity=100000.0,
    )
    
    # Check flagging logic
    if de_ratio > 2.0:
        # Should be flagged
        assert result.is_flagged is True
        if de_ratio > 3.0:
            assert result.severity == "high"
        else:
            assert result.severity == "medium"
    elif de_ratio < 0.5:
        # Should be flagged
        assert result.is_flagged is True
        assert result.severity == "low"
    else:
        # Should not be flagged
        assert result.is_flagged is False


# Feature: intelli-credit, Property 42: Out-of-Range Ratio Flagging (LTV)
@settings(max_examples=15)
@given(
    ltv_ratio=st.floats(min_value=0.0, max_value=1.5),
)
def test_out_of_range_ratio_flagging_ltv(ltv_ratio):
    """For any calculated LTV ratio that falls outside acceptable ranges,
    the system should flag it with a severity indicator.
    
    **Validates: Requirements 16.5**
    """
    calculator = RatioCalculator()
    
    # Calculate LTV
    result = calculator.calculate_ltv(
        loan_amount=ltv_ratio * 100000,
        collateral_value=100000.0,
    )
    
    # Check flagging logic
    if ltv_ratio > 0.75:
        # Should be flagged
        assert result.is_flagged is True
        if ltv_ratio > 0.90:
            assert result.severity == "high"
        else:
            assert result.severity == "medium"
    else:
        # Should not be flagged
        assert result.is_flagged is False


# Feature: intelli-credit, Property 15: DSCR Calculation Formula
@settings(max_examples=15)
@given(
    cash_flow=st.floats(min_value=0.01, max_value=1e9),
    debt_service=st.floats(min_value=0.01, max_value=1e9),
)
def test_dscr_calculation_formula(cash_flow, debt_service):
    """For any financial data with cash flow and debt service values,
    the calculated DSCR should equal cash flow divided by debt service.
    
    **Validates: Requirements 6.1**
    """
    calculator = RatioCalculator()
    
    result = calculator.calculate_dscr(cash_flow, debt_service)
    expected_dscr = cash_flow / debt_service
    
    assert abs(result.value - expected_dscr) < 0.001


# Feature: intelli-credit, Property 18: Debt-to-Equity Calculation
@settings(max_examples=15)
@given(
    total_debt=st.floats(min_value=0.01, max_value=1e9),
    total_equity=st.floats(min_value=0.01, max_value=1e9),
)
def test_debt_equity_calculation_formula(total_debt, total_equity):
    """For any balance sheet data with total debt and total equity values,
    the calculated Debt-to-Equity ratio should equal total debt divided by
    total equity.
    
    **Validates: Requirements 7.1**
    """
    calculator = RatioCalculator()
    
    result = calculator.calculate_debt_equity_ratio(total_debt, total_equity)
    expected_de = total_debt / total_equity
    
    assert abs(result.value - expected_de) < 0.001


# Feature: intelli-credit, Property 21: LTV Calculation Formula
@settings(max_examples=15)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    collateral_value=st.floats(min_value=0.01, max_value=1e9),
)
def test_ltv_calculation_formula(loan_amount, collateral_value):
    """For any collateral information with loan amount and collateral value,
    the calculated LTV should equal loan amount divided by collateral value.
    
    **Validates: Requirements 8.1**
    """
    calculator = RatioCalculator()
    
    result = calculator.calculate_ltv(loan_amount, collateral_value)
    expected_ltv = loan_amount / collateral_value
    
    assert abs(result.value - expected_ltv) < 0.001


# Feature: intelli-credit, Property 23: Aggregate LTV Calculation
@settings(max_examples=15)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    num_assets=st.integers(min_value=1, max_value=5),
)
def test_aggregate_ltv_calculation(loan_amount, num_assets):
    """For any loan application with multiple collateral assets, the system
    should calculate an aggregate LTV across all assets.
    
    **Validates: Requirements 8.3**
    """
    calculator = RatioCalculator()
    
    # Create multiple assets
    assets = []
    total_value = 0.0
    for i in range(num_assets):
        asset_value = 100000.0 + (i * 50000)
        assets.append(
            Asset(
                asset_type="property",
                description=f"Asset {i}",
                value=asset_value,
                valuation_date=datetime.now(),
            )
        )
        total_value += asset_value
    
    result = calculator.calculate_aggregate_ltv(loan_amount, assets)
    expected_ltv = loan_amount / total_value
    
    assert abs(result.value - expected_ltv) < 0.001
