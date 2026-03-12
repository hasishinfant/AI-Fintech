"""Unit tests for RatioCalculator class."""

import pytest
from datetime import datetime
from app.services.credit_engine import RatioCalculator, RatioResult
from app.models.financial import Asset


class TestDSCRCalculation:
    """Tests for DSCR calculation."""

    def test_dscr_basic_calculation(self):
        """Test basic DSCR calculation: DSCR = Cash Flow / Debt Service."""
        calculator = RatioCalculator()
        
        cash_flow = 100000.0
        debt_service = 80000.0
        
        result = calculator.calculate_dscr(cash_flow, debt_service)
        
        assert result.ratio_name == "DSCR"
        assert abs(result.value - 1.25) < 0.001
        assert result.period == "annual"

    def test_dscr_high_coverage(self):
        """Test DSCR with high debt service coverage."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_dscr(200000.0, 100000.0)
        
        assert abs(result.value - 2.0) < 0.001
        assert not result.is_flagged

    def test_dscr_low_coverage_flagged(self):
        """Test DSCR below 1.25 is flagged as medium severity."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_dscr(100000.0, 120000.0)
        
        assert abs(result.value - 0.833) < 0.01
        assert result.is_flagged
        assert result.severity == "high"
        assert "below acceptable minimum" in result.flag_reason

    def test_dscr_zero_debt_service(self):
        """Test DSCR with zero debt service (no debt)."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_dscr(100000.0, 0.0)
        
        # Should handle gracefully
        assert result.value == 0.0  # Converted from inf

    def test_dscr_negative_cash_flow_raises_error(self):
        """Test that negative cash flow raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Cash flow must be non-negative"):
            calculator.calculate_dscr(-100000.0, 80000.0)

    def test_dscr_negative_debt_service_raises_error(self):
        """Test that negative debt service raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Debt service must be non-negative"):
            calculator.calculate_dscr(100000.0, -80000.0)

    def test_dscr_with_industry_benchmark(self):
        """Test DSCR calculation with industry benchmark."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_dscr(
            100000.0, 80000.0, industry="manufacturing"
        )
        
        assert result.benchmark is not None
        assert result.benchmark_source == "RBI Guidelines"


class TestDebtEquityCalculation:
    """Tests for Debt-to-Equity ratio calculation."""

    def test_debt_equity_basic_calculation(self):
        """Test basic Debt-to-Equity calculation."""
        calculator = RatioCalculator()
        
        total_debt = 100000.0
        total_equity = 100000.0
        
        result = calculator.calculate_debt_equity_ratio(total_debt, total_equity)
        
        assert result.ratio_name == "Debt-to-Equity"
        assert abs(result.value - 1.0) < 0.001

    def test_debt_equity_high_leverage(self):
        """Test Debt-to-Equity with high leverage."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_debt_equity_ratio(200000.0, 100000.0)
        
        assert abs(result.value - 2.0) < 0.001
        assert result.is_flagged
        assert result.severity == "medium"

    def test_debt_equity_very_high_leverage_flagged(self):
        """Test Debt-to-Equity exceeding 3.0 is flagged as high severity."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_debt_equity_ratio(300000.0, 100000.0)
        
        assert abs(result.value - 3.0) < 0.001
        assert result.is_flagged
        assert result.severity == "high"

    def test_debt_equity_zero_equity_raises_error(self):
        """Test that zero equity raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Total equity cannot be zero"):
            calculator.calculate_debt_equity_ratio(100000.0, 0.0)

    def test_debt_equity_negative_debt_raises_error(self):
        """Test that negative debt raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Total debt must be non-negative"):
            calculator.calculate_debt_equity_ratio(-100000.0, 100000.0)

    def test_debt_equity_negative_equity_raises_error(self):
        """Test that negative equity raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Total equity must be non-negative"):
            calculator.calculate_debt_equity_ratio(100000.0, -100000.0)

    def test_debt_equity_with_industry_benchmark(self):
        """Test Debt-to-Equity with industry benchmark."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_debt_equity_ratio(
            100000.0, 100000.0, industry="services"
        )
        
        assert result.benchmark is not None
        assert result.benchmark_source == "Industry Standards"


class TestLTVCalculation:
    """Tests for Loan-to-Value ratio calculation."""

    def test_ltv_basic_calculation(self):
        """Test basic LTV calculation."""
        calculator = RatioCalculator()
        
        loan_amount = 75000.0
        collateral_value = 100000.0
        
        result = calculator.calculate_ltv(loan_amount, collateral_value)
        
        assert result.ratio_name == "LTV"
        assert abs(result.value - 0.75) < 0.001

    def test_ltv_high_ratio_flagged(self):
        """Test LTV exceeding 0.75 is flagged."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_ltv(85000.0, 100000.0)
        
        assert abs(result.value - 0.85) < 0.001
        assert result.is_flagged
        assert result.severity == "medium"

    def test_ltv_very_high_ratio_flagged(self):
        """Test LTV exceeding 0.90 is flagged as high severity."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_ltv(95000.0, 100000.0)
        
        assert abs(result.value - 0.95) < 0.001
        assert result.is_flagged
        assert result.severity == "high"

    def test_ltv_zero_collateral_raises_error(self):
        """Test that zero collateral value raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Collateral value cannot be zero"):
            calculator.calculate_ltv(75000.0, 0.0)

    def test_ltv_negative_loan_raises_error(self):
        """Test that negative loan amount raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Loan amount must be non-negative"):
            calculator.calculate_ltv(-75000.0, 100000.0)

    def test_ltv_negative_collateral_raises_error(self):
        """Test that negative collateral raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="Collateral value must be non-negative"):
            calculator.calculate_ltv(75000.0, -100000.0)

    def test_ltv_with_industry_benchmark(self):
        """Test LTV with industry benchmark."""
        calculator = RatioCalculator()
        
        result = calculator.calculate_ltv(
            75000.0, 100000.0, industry="retail"
        )
        
        assert result.benchmark is not None
        assert result.benchmark_source == "Lending Standards"


class TestAggregateLTV:
    """Tests for aggregate LTV calculation across multiple assets."""

    def test_aggregate_ltv_single_asset(self):
        """Test aggregate LTV with single collateral asset."""
        calculator = RatioCalculator()
        
        assets = [
            Asset(
                asset_type="property",
                description="Commercial property",
                value=100000.0,
                valuation_date=datetime.now()
            )
        ]
        
        result = calculator.calculate_aggregate_ltv(75000.0, assets)
        
        assert abs(result.value - 0.75) < 0.001

    def test_aggregate_ltv_multiple_assets(self):
        """Test aggregate LTV with multiple collateral assets."""
        calculator = RatioCalculator()
        
        assets = [
            Asset(
                asset_type="property",
                description="Commercial property",
                value=100000.0,
                valuation_date=datetime.now()
            ),
            Asset(
                asset_type="equipment",
                description="Machinery",
                value=50000.0,
                valuation_date=datetime.now()
            ),
        ]
        
        result = calculator.calculate_aggregate_ltv(100000.0, assets)
        
        # Total collateral = 150000, LTV = 100000/150000 = 0.667
        assert abs(result.value - 0.667) < 0.01

    def test_aggregate_ltv_empty_assets_raises_error(self):
        """Test that empty asset list raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="At least one collateral asset is required"):
            calculator.calculate_aggregate_ltv(75000.0, [])

    def test_aggregate_ltv_zero_total_value_raises_error(self):
        """Test that zero total collateral value raises ValueError."""
        calculator = RatioCalculator()
        
        assets = [
            Asset(
                asset_type="property",
                description="Property",
                value=0.0,
                valuation_date=datetime.now()
            )
        ]
        
        with pytest.raises(ValueError, match="Total collateral value must be positive"):
            calculator.calculate_aggregate_ltv(75000.0, assets)


class TestThreeYearTrend:
    """Tests for three-year trend calculation."""

    def test_trend_improving(self):
        """Test trend calculation for improving ratios."""
        calculator = RatioCalculator()
        
        historical_data = [
            ("2022", 1.0),
            ("2023", 1.2),
            ("2024", 1.4),
        ]
        
        values, trend_direction = calculator.calculate_three_year_trend(
            historical_data, "DSCR"
        )
        
        assert values == [1.0, 1.2, 1.4]
        assert trend_direction == "improving"

    def test_trend_declining(self):
        """Test trend calculation for declining ratios."""
        calculator = RatioCalculator()
        
        historical_data = [
            ("2022", 2.0),
            ("2023", 1.5),
            ("2024", 1.0),
        ]
        
        values, trend_direction = calculator.calculate_three_year_trend(
            historical_data, "DSCR"
        )
        
        assert values == [2.0, 1.5, 1.0]
        assert trend_direction == "declining"

    def test_trend_stable(self):
        """Test trend calculation for stable ratios."""
        calculator = RatioCalculator()
        
        historical_data = [
            ("2022", 1.5),
            ("2023", 1.5),
            ("2024", 1.5),
        ]
        
        values, trend_direction = calculator.calculate_three_year_trend(
            historical_data, "DSCR"
        )
        
        assert values == [1.5, 1.5, 1.5]
        assert trend_direction == "stable"

    def test_trend_insufficient_data_raises_error(self):
        """Test that insufficient data raises ValueError."""
        calculator = RatioCalculator()
        
        with pytest.raises(ValueError, match="At least 2 data points required"):
            calculator.calculate_three_year_trend([("2024", 1.5)], "DSCR")


class TestBenchmarkComparison:
    """Tests for benchmark comparison."""

    def test_compare_with_benchmarks_manufacturing(self):
        """Test benchmark comparison for manufacturing industry."""
        calculator = RatioCalculator()
        
        results = [
            RatioResult(
                ratio_name="DSCR",
                value=1.5,
                period="annual",
            ),
            RatioResult(
                ratio_name="Debt-to-Equity",
                value=1.0,
                period="annual",
            ),
        ]
        
        updated = calculator.compare_with_benchmarks(results, "manufacturing")
        
        assert len(updated) == 2
        assert updated[0].benchmark is not None
        assert updated[0].benchmark_source == "RBI Guidelines"
        assert updated[1].benchmark is not None
        assert updated[1].benchmark_source == "Industry Standards"

    def test_compare_with_benchmarks_unknown_industry(self):
        """Test benchmark comparison with unknown industry."""
        calculator = RatioCalculator()
        
        results = [
            RatioResult(
                ratio_name="DSCR",
                value=1.5,
                period="annual",
            ),
        ]
        
        updated = calculator.compare_with_benchmarks(results, "unknown_industry")
        
        # Should return results unchanged
        assert len(updated) == 1
        assert updated[0].benchmark is None


class TestAccountingPeriodConsistency:
    """Tests for accounting period consistency verification."""

    def test_consistent_periods(self):
        """Test verification of consistent accounting periods."""
        from app.models.financial import FinancialData
        
        calculator = RatioCalculator()
        
        data = [
            FinancialData(
                company_id="comp1",
                period="annual",
                revenue=1000000.0,
                expenses=800000.0,
                ebitda=200000.0,
                net_profit=100000.0,
                total_assets=5000000.0,
                total_liabilities=2000000.0,
                equity=3000000.0,
                cash_flow=150000.0,
            ),
            FinancialData(
                company_id="comp1",
                period="annual",
                revenue=1100000.0,
                expenses=850000.0,
                ebitda=250000.0,
                net_profit=120000.0,
                total_assets=5500000.0,
                total_liabilities=2100000.0,
                equity=3400000.0,
                cash_flow=180000.0,
            ),
        ]
        
        is_consistent = calculator.verify_accounting_period_consistency(data)
        
        assert is_consistent is True

    def test_inconsistent_periods(self):
        """Test detection of inconsistent accounting periods."""
        from app.models.financial import FinancialData
        
        calculator = RatioCalculator()
        
        data = [
            FinancialData(
                company_id="comp1",
                period="annual",
                revenue=1000000.0,
                expenses=800000.0,
                ebitda=200000.0,
                net_profit=100000.0,
                total_assets=5000000.0,
                total_liabilities=2000000.0,
                equity=3000000.0,
                cash_flow=150000.0,
            ),
            FinancialData(
                company_id="comp1",
                period="quarterly",
                revenue=250000.0,
                expenses=200000.0,
                ebitda=50000.0,
                net_profit=25000.0,
                total_assets=5000000.0,
                total_liabilities=2000000.0,
                equity=3000000.0,
                cash_flow=37500.0,
            ),
        ]
        
        is_consistent = calculator.verify_accounting_period_consistency(data)
        
        assert is_consistent is False

    def test_empty_data_list(self):
        """Test consistency check with empty data list."""
        calculator = RatioCalculator()
        
        is_consistent = calculator.verify_accounting_period_consistency([])
        
        assert is_consistent is True
