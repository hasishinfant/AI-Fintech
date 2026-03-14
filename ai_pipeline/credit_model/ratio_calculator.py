"""Financial ratio calculations for credit assessment."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from app.models.financial import FinancialData, Debt, Asset


@dataclass
class RatioResult:
    """Result of a financial ratio calculation."""
    ratio_name: str
    value: float
    period: str
    benchmark: Optional[float] = None
    benchmark_source: Optional[str] = None
    is_flagged: bool = False
    severity: Optional[str] = None  # "high", "medium", "low"
    flag_reason: Optional[str] = None
    trend: Optional[List[float]] = field(default_factory=list)  # Historical values for trend
    trend_direction: Optional[str] = None  # "improving", "stable", "declining"


@dataclass
class IndustryBenchmark:
    """Industry benchmark for a financial ratio."""
    ratio_name: str
    industry: str
    acceptable_range: Tuple[float, float]  # (min, max)
    optimal_value: float
    source: str


class RatioCalculator:
    """Calculates and analyzes financial ratios for credit assessment."""
    
    # Industry benchmarks (simplified for demonstration)
    # In production, these would be loaded from a database
    INDUSTRY_BENCHMARKS: Dict[str, Dict[str, IndustryBenchmark]] = {
        "manufacturing": {
            "dscr": IndustryBenchmark(
                ratio_name="DSCR",
                industry="manufacturing",
                acceptable_range=(1.25, 3.0),
                optimal_value=1.75,
                source="RBI Guidelines"
            ),
            "debt_equity": IndustryBenchmark(
                ratio_name="Debt-to-Equity",
                industry="manufacturing",
                acceptable_range=(0.5, 2.0),
                optimal_value=1.0,
                source="Industry Standards"
            ),
            "ltv": IndustryBenchmark(
                ratio_name="LTV",
                industry="manufacturing",
                acceptable_range=(0.0, 0.75),
                optimal_value=0.60,
                source="Lending Standards"
            ),
        },
        "services": {
            "dscr": IndustryBenchmark(
                ratio_name="DSCR",
                industry="services",
                acceptable_range=(1.25, 2.5),
                optimal_value=1.50,
                source="RBI Guidelines"
            ),
            "debt_equity": IndustryBenchmark(
                ratio_name="Debt-to-Equity",
                industry="services",
                acceptable_range=(0.3, 1.5),
                optimal_value=0.75,
                source="Industry Standards"
            ),
            "ltv": IndustryBenchmark(
                ratio_name="LTV",
                industry="services",
                acceptable_range=(0.0, 0.70),
                optimal_value=0.55,
                source="Lending Standards"
            ),
        },
        "retail": {
            "dscr": IndustryBenchmark(
                ratio_name="DSCR",
                industry="retail",
                acceptable_range=(1.25, 2.0),
                optimal_value=1.50,
                source="RBI Guidelines"
            ),
            "debt_equity": IndustryBenchmark(
                ratio_name="Debt-to-Equity",
                industry="retail",
                acceptable_range=(0.4, 1.8),
                optimal_value=0.90,
                source="Industry Standards"
            ),
            "ltv": IndustryBenchmark(
                ratio_name="LTV",
                industry="retail",
                acceptable_range=(0.0, 0.70),
                optimal_value=0.55,
                source="Lending Standards"
            ),
        },
    }

    def __init__(self):
        """Initialize the RatioCalculator."""
        pass

    def calculate_dscr(
        self,
        cash_flow: float,
        debt_service: float,
        period: str = "annual",
        industry: Optional[str] = None,
    ) -> RatioResult:
        """
        Calculate Debt Service Coverage Ratio (DSCR).
        
        DSCR = Cash Flow / Debt Service
        
        Requirement 16.1: Calculate DSCR
        Requirement 16.2: Use consistent accounting periods
        Requirement 16.3: Compare against industry benchmarks
        Requirement 16.5: Flag out-of-range ratios with severity
        
        Args:
            cash_flow: Operating cash flow (positive value)
            debt_service: Total annual debt service obligations (positive value)
            period: Accounting period ("annual", "quarterly", "monthly")
            industry: Industry type for benchmark comparison
            
        Returns:
            RatioResult with DSCR value and analysis
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if cash_flow < 0:
            raise ValueError("Cash flow must be non-negative")
        if debt_service < 0:
            raise ValueError("Debt service must be non-negative")
        if debt_service == 0:
            # No debt obligations - perfect DSCR
            dscr_value = float('inf')
        else:
            dscr_value = cash_flow / debt_service
        
        # Get benchmark if industry provided
        benchmark = None
        benchmark_source = None
        if industry and industry.lower() in self.INDUSTRY_BENCHMARKS:
            benchmark_data = self.INDUSTRY_BENCHMARKS[industry.lower()].get("dscr")
            if benchmark_data:
                benchmark = benchmark_data.optimal_value
                benchmark_source = benchmark_data.source
        
        # Check if ratio is flagged
        is_flagged, severity, flag_reason = self._check_dscr_flags(
            dscr_value, industry
        )
        
        return RatioResult(
            ratio_name="DSCR",
            value=dscr_value if dscr_value != float('inf') else 0.0,
            period=period,
            benchmark=benchmark,
            benchmark_source=benchmark_source,
            is_flagged=is_flagged,
            severity=severity,
            flag_reason=flag_reason,
        )

    def calculate_debt_equity_ratio(
        self,
        total_debt: float,
        total_equity: float,
        period: str = "annual",
        industry: Optional[str] = None,
    ) -> RatioResult:
        """
        Calculate Debt-to-Equity Ratio.
        
        Debt-to-Equity = Total Debt / Total Equity
        
        Requirement 16.1: Calculate Debt-to-Equity ratio
        Requirement 16.2: Use consistent accounting periods
        Requirement 16.3: Compare against industry benchmarks
        Requirement 16.5: Flag out-of-range ratios with severity
        
        Args:
            total_debt: Total debt obligations (positive value)
            total_equity: Total equity (positive value)
            period: Accounting period ("annual", "quarterly", "monthly")
            industry: Industry type for benchmark comparison
            
        Returns:
            RatioResult with Debt-to-Equity ratio and analysis
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if total_debt < 0:
            raise ValueError("Total debt must be non-negative")
        if total_equity < 0:
            raise ValueError("Total equity must be non-negative")
        if total_equity == 0:
            raise ValueError("Total equity cannot be zero")
        
        de_ratio = total_debt / total_equity
        
        # Get benchmark if industry provided
        benchmark = None
        benchmark_source = None
        if industry and industry.lower() in self.INDUSTRY_BENCHMARKS:
            benchmark_data = self.INDUSTRY_BENCHMARKS[industry.lower()].get("debt_equity")
            if benchmark_data:
                benchmark = benchmark_data.optimal_value
                benchmark_source = benchmark_data.source
        
        # Check if ratio is flagged
        is_flagged, severity, flag_reason = self._check_debt_equity_flags(
            de_ratio, industry
        )
        
        return RatioResult(
            ratio_name="Debt-to-Equity",
            value=de_ratio,
            period=period,
            benchmark=benchmark,
            benchmark_source=benchmark_source,
            is_flagged=is_flagged,
            severity=severity,
            flag_reason=flag_reason,
        )

    def calculate_ltv(
        self,
        loan_amount: float,
        collateral_value: float,
        period: str = "annual",
        industry: Optional[str] = None,
    ) -> RatioResult:
        """
        Calculate Loan-to-Value (LTV) Ratio.
        
        LTV = Loan Amount / Collateral Value
        
        Requirement 16.1: Calculate LTV
        Requirement 16.2: Use consistent accounting periods
        Requirement 16.3: Compare against industry benchmarks
        Requirement 16.5: Flag out-of-range ratios with severity
        
        Args:
            loan_amount: Requested loan amount (positive value)
            collateral_value: Total collateral value (positive value)
            period: Accounting period ("annual", "quarterly", "monthly")
            industry: Industry type for benchmark comparison
            
        Returns:
            RatioResult with LTV ratio and analysis
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if loan_amount < 0:
            raise ValueError("Loan amount must be non-negative")
        if collateral_value < 0:
            raise ValueError("Collateral value must be non-negative")
        if collateral_value == 0:
            raise ValueError("Collateral value cannot be zero")
        
        ltv_ratio = loan_amount / collateral_value
        
        # Get benchmark if industry provided
        benchmark = None
        benchmark_source = None
        if industry and industry.lower() in self.INDUSTRY_BENCHMARKS:
            benchmark_data = self.INDUSTRY_BENCHMARKS[industry.lower()].get("ltv")
            if benchmark_data:
                benchmark = benchmark_data.optimal_value
                benchmark_source = benchmark_data.source
        
        # Check if ratio is flagged
        is_flagged, severity, flag_reason = self._check_ltv_flags(
            ltv_ratio, industry
        )
        
        return RatioResult(
            ratio_name="LTV",
            value=ltv_ratio,
            period=period,
            benchmark=benchmark,
            benchmark_source=benchmark_source,
            is_flagged=is_flagged,
            severity=severity,
            flag_reason=flag_reason,
        )

    def calculate_aggregate_ltv(
        self,
        loan_amount: float,
        collateral_assets: List[Asset],
        industry: Optional[str] = None,
    ) -> RatioResult:
        """
        Calculate aggregate LTV across multiple collateral assets.
        
        Requirement 8.3: Calculate aggregate LTV for multiple assets
        
        Args:
            loan_amount: Requested loan amount
            collateral_assets: List of collateral assets with values
            industry: Industry type for benchmark comparison
            
        Returns:
            RatioResult with aggregate LTV
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not collateral_assets:
            raise ValueError("At least one collateral asset is required")
        
        total_collateral_value = sum(asset.value for asset in collateral_assets)
        
        if total_collateral_value <= 0:
            raise ValueError("Total collateral value must be positive")
        
        return self.calculate_ltv(
            loan_amount=loan_amount,
            collateral_value=total_collateral_value,
            period="annual",
            industry=industry,
        )

    def calculate_three_year_trend(
        self,
        historical_data: List[Tuple[str, float]],
        ratio_name: str,
    ) -> Tuple[List[float], str]:
        """
        Calculate year-over-year trend for past three years.
        
        Requirement 16.4: Calculate three-year trends
        
        Args:
            historical_data: List of (period, value) tuples, sorted chronologically
            ratio_name: Name of the ratio for context
            
        Returns:
            Tuple of (trend_values, trend_direction)
            trend_direction: "improving", "stable", or "declining"
            
        Raises:
            ValueError: If insufficient data provided
        """
        if len(historical_data) < 2:
            raise ValueError("At least 2 data points required for trend analysis")
        
        # Extract values
        values = [value for _, value in historical_data]
        
        # Calculate year-over-year changes
        yoy_changes = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                change = (values[i] - values[i-1]) / abs(values[i-1])
                yoy_changes.append(change)
        
        # Determine trend direction
        if not yoy_changes:
            trend_direction = "stable"
        else:
            avg_change = sum(yoy_changes) / len(yoy_changes)
            
            # Threshold for determining trend (5% change)
            if avg_change > 0.05:
                trend_direction = "improving"
            elif avg_change < -0.05:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        
        return values, trend_direction

    def compare_with_benchmarks(
        self,
        ratio_results: List[RatioResult],
        industry: str,
    ) -> List[RatioResult]:
        """
        Compare calculated ratios with industry benchmarks.
        
        Requirement 16.3: Compare against industry benchmarks
        
        Args:
            ratio_results: List of calculated ratio results
            industry: Industry type for benchmark lookup
            
        Returns:
            Updated ratio results with benchmark comparisons
        """
        updated_results = []
        
        if industry.lower() not in self.INDUSTRY_BENCHMARKS:
            # Industry not found, return results as-is
            return ratio_results
        
        industry_benchmarks = self.INDUSTRY_BENCHMARKS[industry.lower()]
        
        for result in ratio_results:
            # Map ratio names to benchmark keys
            ratio_key = None
            if result.ratio_name == "DSCR":
                ratio_key = "dscr"
            elif result.ratio_name == "Debt-to-Equity":
                ratio_key = "debt_equity"
            elif result.ratio_name == "LTV":
                ratio_key = "ltv"
            
            if ratio_key and ratio_key in industry_benchmarks:
                benchmark_data = industry_benchmarks[ratio_key]
                result.benchmark = benchmark_data.optimal_value
                result.benchmark_source = benchmark_data.source
                
                # Re-check flags with benchmark
                if result.ratio_name == "DSCR":
                    is_flagged, severity, reason = self._check_dscr_flags(
                        result.value, industry
                    )
                elif result.ratio_name == "Debt-to-Equity":
                    is_flagged, severity, reason = self._check_debt_equity_flags(
                        result.value, industry
                    )
                elif result.ratio_name == "LTV":
                    is_flagged, severity, reason = self._check_ltv_flags(
                        result.value, industry
                    )
                else:
                    is_flagged, severity, reason = False, None, None
                
                result.is_flagged = is_flagged
                result.severity = severity
                result.flag_reason = reason
            
            updated_results.append(result)
        
        return updated_results

    def _check_dscr_flags(
        self, dscr_value: float, industry: Optional[str]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if DSCR is flagged and determine severity.
        
        Requirement 16.5: Flag out-of-range ratios with severity
        """
        if dscr_value == float('inf') or dscr_value == 0.0:
            # No debt or no cash flow - handle separately
            return False, None, None
        
        # Get acceptable range from benchmark
        acceptable_min = 1.25
        acceptable_max = 3.0
        
        if industry and industry.lower() in self.INDUSTRY_BENCHMARKS:
            benchmark = self.INDUSTRY_BENCHMARKS[industry.lower()].get("dscr")
            if benchmark:
                acceptable_min, acceptable_max = benchmark.acceptable_range
        
        if dscr_value < acceptable_min:
            severity = "high" if dscr_value < 1.0 else "medium"
            reason = f"DSCR {dscr_value:.2f} below acceptable minimum {acceptable_min}"
            return True, severity, reason
        elif dscr_value > acceptable_max:
            severity = "low"
            reason = f"DSCR {dscr_value:.2f} above acceptable maximum {acceptable_max}"
            return True, severity, reason
        
        return False, None, None

    def _check_debt_equity_flags(
        self, de_ratio: float, industry: Optional[str]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if Debt-to-Equity ratio is flagged and determine severity.
        
        Requirement 16.5: Flag out-of-range ratios with severity
        """
        # Get acceptable range from benchmark
        acceptable_min = 0.5
        acceptable_max = 2.0
        
        if industry and industry.lower() in self.INDUSTRY_BENCHMARKS:
            benchmark = self.INDUSTRY_BENCHMARKS[industry.lower()].get("debt_equity")
            if benchmark:
                acceptable_min, acceptable_max = benchmark.acceptable_range
        
        if de_ratio >= acceptable_max:
            severity = "high" if de_ratio >= 3.0 else "medium"
            reason = f"Debt-to-Equity {de_ratio:.2f} exceeds acceptable maximum {acceptable_max}"
            return True, severity, reason
        elif de_ratio < acceptable_min:
            severity = "low"
            reason = f"Debt-to-Equity {de_ratio:.2f} below acceptable minimum {acceptable_min}"
            return True, severity, reason
        
        return False, None, None

    def _check_ltv_flags(
        self, ltv_ratio: float, industry: Optional[str]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if LTV ratio is flagged and determine severity.
        
        Requirement 16.5: Flag out-of-range ratios with severity
        """
        # Get acceptable range from benchmark
        acceptable_max = 0.75
        
        if industry and industry.lower() in self.INDUSTRY_BENCHMARKS:
            benchmark = self.INDUSTRY_BENCHMARKS[industry.lower()].get("ltv")
            if benchmark:
                acceptable_max = benchmark.acceptable_range[1]
        
        if ltv_ratio > acceptable_max:
            severity = "high" if ltv_ratio > 0.90 else "medium"
            reason = f"LTV {ltv_ratio:.2f} exceeds acceptable maximum {acceptable_max}"
            return True, severity, reason
        
        return False, None, None

    def verify_accounting_period_consistency(
        self,
        financial_data_list: List[FinancialData],
    ) -> bool:
        """
        Verify that all financial data uses consistent accounting periods.
        
        Requirement 16.2: Ensure accounting period consistency
        
        Args:
            financial_data_list: List of financial data objects
            
        Returns:
            True if all periods are consistent, False otherwise
        """
        if not financial_data_list:
            return True
        
        # Get the first period as reference
        reference_period = financial_data_list[0].period
        
        # Check all periods match
        for data in financial_data_list[1:]:
            if data.period != reference_period:
                return False
        
        return True
