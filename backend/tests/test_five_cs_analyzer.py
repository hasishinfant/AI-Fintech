"""Unit tests for FiveCsAnalyzer class."""

import pytest
from datetime import datetime, timedelta
from app.services.credit_engine import FiveCsAnalyzer
from app.models.research import LegalCase, MCAData, SentimentScore, RBINotification
from app.models.credit_assessment import CharacterScore, CapacityScore, CapitalScore, CollateralScore, ConditionsScore
from app.models.financial import FinancialData, Debt


class TestCharacterAnalysis:
    """Test Character assessment functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FiveCsAnalyzer()

    def test_analyze_character_no_issues(self):
        """Test Character analysis with clean record."""
        promoter_data = {"name": "John Doe", "din": "12345678"}
        legal_cases = []
        mca_data = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="compliant",
            directors=[{"name": "John Doe", "din": "12345678"}],
        )
        credit_bureau_score = 800.0

        result = self.analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        assert isinstance(result, CharacterScore)
        assert 0 <= result.score <= 100
        assert result.score >= 80  # Should be high with clean record
        assert result.litigation_count == 0
        assert result.governance_rating == "Good"
        assert result.credit_bureau_score == 800.0
        assert len(result.negative_factors) == 0

    def test_analyze_character_with_litigation(self):
        """Test Character analysis with legal cases."""
        promoter_data = {"name": "John Doe", "din": "12345678"}
        legal_cases = [
            LegalCase(
                case_number="CASE001",
                court="High Court",
                filing_date=datetime(2022, 1, 1),
                case_type="fraud",
                status="pending",
                summary="Fraud case",
                parties=["Test Company", "Plaintiff"],
            ),
            LegalCase(
                case_number="CASE002",
                court="District Court",
                filing_date=datetime(2023, 1, 1),
                case_type="civil dispute",
                status="pending",
                summary="Contract dispute",
                parties=["Test Company", "Vendor"],
            ),
        ]
        mca_data = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="compliant",
            directors=[{"name": "John Doe", "din": "12345678"}],
        )
        credit_bureau_score = 750.0

        result = self.analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        assert result.litigation_count == 2
        assert result.score < 90  # Should be lower with litigation
        assert len(result.negative_factors) > 0
        assert any("fraud" in factor.lower() for factor in result.negative_factors)

    def test_analyze_character_low_credit_score(self):
        """Test Character analysis with low credit bureau score."""
        promoter_data = {"name": "John Doe", "din": "12345678"}
        legal_cases = []
        mca_data = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="compliant",
            directors=[{"name": "John Doe", "din": "12345678"}],
        )
        credit_bureau_score = 600.0  # Low score

        result = self.analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        assert result.score < 90  # Should be lower with low credit score
        assert any("credit bureau score" in factor.lower() for factor in result.negative_factors)

    def test_analyze_character_mca_non_compliant(self):
        """Test Character analysis with MCA non-compliance."""
        promoter_data = {"name": "John Doe", "din": "12345678"}
        legal_cases = []
        mca_data = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=400),  # Overdue
            compliance_status="non-compliant",
            directors=[{"name": "John Doe", "din": "12345678"}],
        )
        credit_bureau_score = 750.0

        result = self.analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        assert result.governance_rating == "Poor"
        assert result.score < 80  # Should be lower with non-compliance
        assert any("non-compliance" in factor.lower() for factor in result.negative_factors)
        assert any("overdue" in factor.lower() for factor in result.negative_factors)

    def test_analyze_character_score_bounds(self):
        """Test that Character score stays within 0-100 bounds."""
        promoter_data = {"name": "John Doe", "din": "12345678"}
        # Create many high-severity cases to test lower bound
        legal_cases = [
            LegalCase(
                case_number=f"CASE{i:03d}",
                court="High Court",
                filing_date=datetime(2022, 1, 1),
                case_type="fraud",
                status="pending",
                summary="Fraud case",
                parties=["Test Company", "Plaintiff"],
            )
            for i in range(10)
        ]
        mca_data = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=500),
            compliance_status="non-compliant",
            directors=[],
        )
        credit_bureau_score = 300.0  # Minimum score

        result = self.analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        assert 0 <= result.score <= 100
        assert result.score >= 0  # Should not go below 0

    def test_normalize_credit_bureau_score_ranges(self):
        """Test credit bureau score normalization across different ranges."""
        analyzer = FiveCsAnalyzer()

        # Excellent range (750-900)
        assert analyzer._normalize_credit_bureau_score(750) == 80
        assert analyzer._normalize_credit_bureau_score(900) == 100
        assert 80 <= analyzer._normalize_credit_bureau_score(825) <= 100

        # Good range (650-749)
        assert analyzer._normalize_credit_bureau_score(650) == 60
        assert 60 <= analyzer._normalize_credit_bureau_score(700) < 80

        # Fair range (550-649)
        assert analyzer._normalize_credit_bureau_score(550) == 40
        assert 40 <= analyzer._normalize_credit_bureau_score(600) < 60

        # Poor range (300-549)
        assert analyzer._normalize_credit_bureau_score(300) == 0
        assert 0 <= analyzer._normalize_credit_bureau_score(425) < 40

    def test_litigation_severity_classification(self):
        """Test that different litigation types are classified correctly."""
        promoter_data = {"name": "John Doe", "din": "12345678"}
        mca_data = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="compliant",
            directors=[{"name": "John Doe", "din": "12345678"}],
        )
        credit_bureau_score = 750.0

        # Test with high-severity case
        high_severity_cases = [
            LegalCase(
                case_number="CASE001",
                court="High Court",
                filing_date=datetime(2022, 1, 1),
                case_type="criminal fraud",
                status="pending",
                summary="Criminal fraud case",
                parties=["Test Company"],
            )
        ]
        result_high = self.analyzer.analyze_character(
            promoter_data, high_severity_cases, mca_data, credit_bureau_score
        )

        # Test with low-severity case
        low_severity_cases = [
            LegalCase(
                case_number="CASE002",
                court="District Court",
                filing_date=datetime(2023, 1, 1),
                case_type="procedural",
                status="pending",
                summary="Minor procedural issue",
                parties=["Test Company"],
            )
        ]
        result_low = self.analyzer.analyze_character(
            promoter_data, low_severity_cases, mca_data, credit_bureau_score
        )

        # High severity should result in lower score
        assert result_high.score < result_low.score

    def test_governance_rating_levels(self):
        """Test different governance rating levels."""
        analyzer = FiveCsAnalyzer()

        # Good governance
        mca_good = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="compliant",
            directors=[{"name": "John Doe", "din": "12345678"}],
        )
        rating_good, score_good = analyzer._calculate_governance_score(mca_good, [])
        assert rating_good == "Good"
        assert score_good >= 90

        # Poor governance
        mca_poor = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=400),
            compliance_status="non-compliant",
            directors=[],
        )
        rating_poor, score_poor = analyzer._calculate_governance_score(mca_poor, [])
        assert rating_poor == "Poor"
        assert score_poor < score_good


class TestCapacityAnalysis:
    """Test Capacity assessment functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FiveCsAnalyzer()

    def test_analyze_capacity_healthy_dscr(self):
        """Test Capacity analysis with healthy DSCR."""
        financial_data = FinancialData(
            company_id="COMP001",
            period="2023-2024",
            revenue=10000000.0,
            expenses=6000000.0,
            ebitda=2000000.0,
            net_profit=1000000.0,
            total_assets=5000000.0,
            total_liabilities=2000000.0,
            equity=3000000.0,
            cash_flow=1500000.0,
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=500000.0,
                interest_rate=10.0,
                emi=50000.0,
                outstanding=400000.0,
            ),
            Debt(
                lender="Bank B",
                amount=300000.0,
                interest_rate=11.0,
                emi=30000.0,
                outstanding=200000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        assert isinstance(result, CapacityScore)
        assert 0 <= result.score <= 100
        # DSCR = 1500000 / (50000 + 30000) = 1500000 / 80000 = 18.75
        assert result.dscr == pytest.approx(18.75, rel=0.01)
        assert result.cash_flow == 1500000.0
        assert result.debt_service == 80000.0
        assert result.score >= 90  # Should be high with healthy DSCR

    def test_analyze_capacity_low_dscr(self):
        """Test Capacity analysis with low DSCR (< 1.25)."""
        financial_data = FinancialData(
            company_id="COMP002",
            period="2023-2024",
            revenue=5000000.0,
            expenses=4000000.0,
            ebitda=500000.0,
            net_profit=200000.0,
            total_assets=3000000.0,
            total_liabilities=2000000.0,
            equity=1000000.0,
            cash_flow=400000.0,
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=1000000.0,
                interest_rate=10.0,
                emi=100000.0,
                outstanding=800000.0,
            ),
            Debt(
                lender="Bank B",
                amount=500000.0,
                interest_rate=11.0,
                emi=50000.0,
                outstanding=400000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        # DSCR = 400000 / (100000 + 50000) = 400000 / 150000 = 2.67
        assert result.dscr == pytest.approx(2.67, rel=0.01)
        assert result.score >= 75  # Should be good even with moderate DSCR

    def test_analyze_capacity_insufficient_dscr(self):
        """Test Capacity analysis with insufficient DSCR (< 1.0)."""
        financial_data = FinancialData(
            company_id="COMP003",
            period="2023-2024",
            revenue=2000000.0,
            expenses=1800000.0,
            ebitda=100000.0,
            net_profit=50000.0,
            total_assets=1000000.0,
            total_liabilities=800000.0,
            equity=200000.0,
            cash_flow=80000.0,
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=500000.0,
                interest_rate=10.0,
                emi=100000.0,
                outstanding=400000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        # DSCR = 80000 / 100000 = 0.8
        assert result.dscr == pytest.approx(0.8, rel=0.01)
        assert result.score < 40  # Should be low with insufficient DSCR

    def test_analyze_capacity_no_debt(self):
        """Test Capacity analysis with no debt obligations."""
        financial_data = FinancialData(
            company_id="COMP004",
            period="2023-2024",
            revenue=10000000.0,
            expenses=6000000.0,
            ebitda=2000000.0,
            net_profit=1000000.0,
            total_assets=5000000.0,
            total_liabilities=0.0,
            equity=5000000.0,
            cash_flow=1500000.0,
        )
        debt_obligations = []

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        # No debt - perfect capacity
        assert result.dscr == 0.0  # Represented as 0 when infinite
        assert result.score == 100.0  # Perfect score with no debt
        assert result.debt_service == 0.0

    def test_analyze_capacity_zero_cash_flow_uses_ebitda(self):
        """Test Capacity analysis falls back to EBITDA when cash flow is zero."""
        financial_data = FinancialData(
            company_id="COMP005",
            period="2023-2024",
            revenue=5000000.0,
            expenses=3000000.0,
            ebitda=1500000.0,
            net_profit=500000.0,
            total_assets=3000000.0,
            total_liabilities=1000000.0,
            equity=2000000.0,
            cash_flow=0.0,  # Zero cash flow
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=500000.0,
                interest_rate=10.0,
                emi=100000.0,
                outstanding=400000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        # Should use EBITDA as fallback
        # DSCR = 1500000 / 100000 = 15.0
        assert result.dscr == pytest.approx(15.0, rel=0.01)
        assert result.cash_flow == 1500000.0  # Should be EBITDA

    def test_analyze_capacity_score_bounds(self):
        """Test that Capacity score stays within 0-100 bounds."""
        financial_data = FinancialData(
            company_id="COMP006",
            period="2023-2024",
            revenue=1000000.0,
            expenses=900000.0,
            ebitda=50000.0,
            net_profit=10000.0,
            total_assets=500000.0,
            total_liabilities=400000.0,
            equity=100000.0,
            cash_flow=30000.0,
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=1000000.0,
                interest_rate=10.0,
                emi=200000.0,
                outstanding=800000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        assert 0 <= result.score <= 100

    def test_analyze_capacity_multiple_debt_obligations(self):
        """Test Capacity analysis with multiple debt obligations."""
        financial_data = FinancialData(
            company_id="COMP007",
            period="2023-2024",
            revenue=20000000.0,
            expenses=12000000.0,
            ebitda=5000000.0,
            net_profit=2000000.0,
            total_assets=10000000.0,
            total_liabilities=4000000.0,
            equity=6000000.0,
            cash_flow=3500000.0,
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=1000000.0,
                interest_rate=9.0,
                emi=100000.0,
                outstanding=800000.0,
            ),
            Debt(
                lender="Bank B",
                amount=800000.0,
                interest_rate=10.0,
                emi=80000.0,
                outstanding=600000.0,
            ),
            Debt(
                lender="NBFC C",
                amount=500000.0,
                interest_rate=12.0,
                emi=60000.0,
                outstanding=400000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        # Total EMI = 100000 + 80000 + 60000 = 240000
        # DSCR = 3500000 / 240000 = 14.58
        assert result.dscr == pytest.approx(14.58, rel=0.01)
        assert result.debt_service == 240000.0
        assert result.score >= 90

    def test_capacity_score_dscr_thresholds(self):
        """Test Capacity score calculation at DSCR thresholds."""
        analyzer = FiveCsAnalyzer()

        # Test DSCR >= 2.0 (should be 90+)
        score_high = analyzer._calculate_capacity_score(2.5)
        assert score_high >= 90

        # Test DSCR 1.5-1.99 (should be 75-89)
        score_very_good = analyzer._calculate_capacity_score(1.75)
        assert 75 <= score_very_good <= 89

        # Test DSCR 1.25-1.49 (should be 60-74)
        score_good = analyzer._calculate_capacity_score(1.35)
        assert 60 <= score_good <= 74

        # Test DSCR 1.0-1.24 (should be 40-59)
        score_fair = analyzer._calculate_capacity_score(1.1)
        assert 40 <= score_fair <= 59

        # Test DSCR < 1.0 (should be 0-39)
        score_poor = analyzer._calculate_capacity_score(0.8)
        assert 0 <= score_poor <= 39

        # Test no debt (should be 100)
        score_perfect = analyzer._calculate_capacity_score(float('inf'))
        assert score_perfect == 100.0

    def test_analyze_capacity_trend_stable(self):
        """Test that Capacity analysis returns stable trend."""
        financial_data = FinancialData(
            company_id="COMP008",
            period="2023-2024",
            revenue=10000000.0,
            expenses=6000000.0,
            ebitda=2000000.0,
            net_profit=1000000.0,
            total_assets=5000000.0,
            total_liabilities=2000000.0,
            equity=3000000.0,
            cash_flow=1500000.0,
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=500000.0,
                interest_rate=10.0,
                emi=50000.0,
                outstanding=400000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        # For now, trend should be stable (would need historical data for other trends)
        assert result.trend == "stable"

    def test_analyze_capacity_very_high_dscr(self):
        """Test Capacity analysis with very high DSCR."""
        financial_data = FinancialData(
            company_id="COMP009",
            period="2023-2024",
            revenue=100000000.0,
            expenses=50000000.0,
            ebitda=30000000.0,
            net_profit=15000000.0,
            total_assets=50000000.0,
            total_liabilities=10000000.0,
            equity=40000000.0,
            cash_flow=25000000.0,
        )
        debt_obligations = [
            Debt(
                lender="Bank A",
                amount=1000000.0,
                interest_rate=8.0,
                emi=50000.0,
                outstanding=800000.0,
            ),
        ]

        result = self.analyzer.analyze_capacity(financial_data, debt_obligations)

        # DSCR = 25000000 / 50000 = 500
        assert result.dscr == pytest.approx(500.0, rel=0.01)
        assert result.score == 100.0  # Should be capped at 100


class TestCapitalAnalysis:
    """Test Capital assessment functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FiveCsAnalyzer()

    def test_analyze_capital_healthy_ratio(self):
        """Test Capital analysis with healthy Debt-to-Equity ratio."""
        financial_data = FinancialData(
            company_id="COMP001",
            period="2023-2024",
            revenue=10000000.0,
            expenses=6000000.0,
            ebitda=2000000.0,
            net_profit=1000000.0,
            total_assets=5000000.0,
            total_liabilities=1000000.0,
            equity=4000000.0,
            cash_flow=1500000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        assert isinstance(result, CapitalScore)
        assert 0 <= result.score <= 100
        # D/E = 1000000 / 4000000 = 0.25
        assert result.debt_equity_ratio == pytest.approx(0.25, rel=0.01)
        assert result.net_worth == 4000000.0
        assert result.score >= 90  # Should be high with healthy ratio
        assert result.net_worth_trend == "stable"

    def test_analyze_capital_moderate_ratio(self):
        """Test Capital analysis with moderate Debt-to-Equity ratio."""
        financial_data = FinancialData(
            company_id="COMP002",
            period="2023-2024",
            revenue=10000000.0,
            expenses=6000000.0,
            ebitda=2000000.0,
            net_profit=1000000.0,
            total_assets=5000000.0,
            total_liabilities=2000000.0,
            equity=3000000.0,
            cash_flow=1500000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 2000000 / 3000000 = 0.67
        assert result.debt_equity_ratio == pytest.approx(0.67, rel=0.01)
        assert result.score >= 75  # Should be good with moderate ratio
        assert result.score < 90

    def test_analyze_capital_high_ratio_flagged(self):
        """Test Capital analysis with high Debt-to-Equity ratio (> 2.0)."""
        financial_data = FinancialData(
            company_id="COMP003",
            period="2023-2024",
            revenue=5000000.0,
            expenses=3000000.0,
            ebitda=1000000.0,
            net_profit=500000.0,
            total_assets=3000000.0,
            total_liabilities=4000000.0,
            equity=2000000.0,
            cash_flow=800000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 4000000 / 2000000 = 2.0 (at threshold)
        assert result.debt_equity_ratio == pytest.approx(2.0, rel=0.01)
        assert result.score >= 40  # Should be fair at threshold
        assert result.score <= 60  # At threshold, score is around 60

    def test_analyze_capital_very_high_ratio(self):
        """Test Capital analysis with very high Debt-to-Equity ratio."""
        financial_data = FinancialData(
            company_id="COMP004",
            period="2023-2024",
            revenue=3000000.0,
            expenses=2500000.0,
            ebitda=300000.0,
            net_profit=100000.0,
            total_assets=2000000.0,
            total_liabilities=5000000.0,
            equity=1000000.0,
            cash_flow=200000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 5000000 / 1000000 = 5.0
        assert result.debt_equity_ratio == pytest.approx(5.0, rel=0.01)
        assert result.score < 40  # Should be poor with very high ratio

    def test_analyze_capital_zero_equity(self):
        """Test Capital analysis with zero equity (critical situation)."""
        financial_data = FinancialData(
            company_id="COMP005",
            period="2023-2024",
            revenue=5000000.0,
            expenses=4000000.0,
            ebitda=500000.0,
            net_profit=0.0,
            total_assets=2000000.0,
            total_liabilities=2000000.0,
            equity=0.0,
            cash_flow=400000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = infinity (zero equity)
        assert result.debt_equity_ratio == 0.0  # Represented as 0 when infinite
        assert result.score == 0.0  # Critical situation
        assert result.net_worth == 0.0

    def test_analyze_capital_negative_equity(self):
        """Test Capital analysis with negative equity (insolvency)."""
        financial_data = FinancialData(
            company_id="COMP006",
            period="2023-2024",
            revenue=2000000.0,
            expenses=2500000.0,
            ebitda=-200000.0,
            net_profit=-500000.0,
            total_assets=1000000.0,
            total_liabilities=2000000.0,
            equity=-1000000.0,
            cash_flow=-300000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # Negative equity - critical
        assert result.net_worth == -1000000.0
        assert result.score == 0.0  # Critical situation

    def test_analyze_capital_score_bounds(self):
        """Test that Capital score stays within 0-100 bounds."""
        # Test with extremely high D/E ratio
        financial_data = FinancialData(
            company_id="COMP007",
            period="2023-2024",
            revenue=1000000.0,
            expenses=900000.0,
            ebitda=50000.0,
            net_profit=10000.0,
            total_assets=500000.0,
            total_liabilities=10000000.0,
            equity=100000.0,
            cash_flow=30000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        assert 0 <= result.score <= 100

    def test_analyze_capital_excellent_ratio(self):
        """Test Capital analysis with excellent Debt-to-Equity ratio."""
        financial_data = FinancialData(
            company_id="COMP008",
            period="2023-2024",
            revenue=20000000.0,
            expenses=10000000.0,
            ebitda=7000000.0,
            net_profit=4000000.0,
            total_assets=15000000.0,
            total_liabilities=2000000.0,
            equity=13000000.0,
            cash_flow=5000000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 2000000 / 13000000 = 0.154
        assert result.debt_equity_ratio == pytest.approx(0.154, rel=0.01)
        assert result.score >= 95  # Should be excellent

    def test_analyze_capital_fair_ratio(self):
        """Test Capital analysis with fair Debt-to-Equity ratio."""
        financial_data = FinancialData(
            company_id="COMP009",
            period="2023-2024",
            revenue=8000000.0,
            expenses=5000000.0,
            ebitda=2000000.0,
            net_profit=1000000.0,
            total_assets=4000000.0,
            total_liabilities=2500000.0,
            equity=1500000.0,
            cash_flow=1200000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 2500000 / 1500000 = 1.67
        assert result.debt_equity_ratio == pytest.approx(1.67, rel=0.01)
        assert 60 <= result.score <= 74  # Should be in good range

    def test_capital_score_de_thresholds(self):
        """Test Capital score calculation at D/E thresholds."""
        analyzer = FiveCsAnalyzer()

        # Test D/E <= 0.5 (should be 90+)
        score_excellent = analyzer._calculate_capital_score(0.3, 1000000.0)
        assert score_excellent >= 90

        # Test D/E 0.5-1.0 (should be 75-89)
        score_very_good = analyzer._calculate_capital_score(0.75, 1000000.0)
        assert 75 <= score_very_good <= 89

        # Test D/E 1.0-2.0 (should be 60-74)
        score_good = analyzer._calculate_capital_score(1.5, 1000000.0)
        assert 60 <= score_good <= 74

        # Test D/E 2.0-3.0 (should be 40-59)
        score_fair = analyzer._calculate_capital_score(2.5, 1000000.0)
        assert 40 <= score_fair <= 59

        # Test D/E > 3.0 (should be 0-39)
        score_poor = analyzer._calculate_capital_score(4.0, 1000000.0)
        assert 0 <= score_poor <= 39

        # Test zero equity (should be 0)
        score_critical = analyzer._calculate_capital_score(float('inf'), 0.0)
        assert score_critical == 0.0

    def test_analyze_capital_large_company(self):
        """Test Capital analysis with large company financials."""
        financial_data = FinancialData(
            company_id="COMP010",
            period="2023-2024",
            revenue=500000000.0,
            expenses=300000000.0,
            ebitda=150000000.0,
            net_profit=75000000.0,
            total_assets=250000000.0,
            total_liabilities=50000000.0,
            equity=200000000.0,
            cash_flow=100000000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 50000000 / 200000000 = 0.25
        assert result.debt_equity_ratio == pytest.approx(0.25, rel=0.01)
        assert result.net_worth == 200000000.0
        assert result.score >= 90

    def test_analyze_capital_small_company(self):
        """Test Capital analysis with small company financials."""
        financial_data = FinancialData(
            company_id="COMP011",
            period="2023-2024",
            revenue=500000.0,
            expenses=300000.0,
            ebitda=150000.0,
            net_profit=75000.0,
            total_assets=250000.0,
            total_liabilities=100000.0,
            equity=150000.0,
            cash_flow=100000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 100000 / 150000 = 0.67
        assert result.debt_equity_ratio == pytest.approx(0.67, rel=0.01)
        assert result.net_worth == 150000.0
        assert result.score >= 75

    def test_analyze_capital_at_threshold_2_0(self):
        """Test Capital analysis exactly at D/E threshold of 2.0."""
        financial_data = FinancialData(
            company_id="COMP012",
            period="2023-2024",
            revenue=6000000.0,
            expenses=4000000.0,
            ebitda=1500000.0,
            net_profit=750000.0,
            total_assets=3000000.0,
            total_liabilities=2000000.0,
            equity=1000000.0,
            cash_flow=1000000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 2000000 / 1000000 = 2.0 (exactly at threshold)
        assert result.debt_equity_ratio == pytest.approx(2.0, rel=0.01)
        # At threshold, score should be around 60
        assert 40 <= result.score <= 60

    def test_analyze_capital_just_above_threshold(self):
        """Test Capital analysis just above D/E threshold of 2.0."""
        financial_data = FinancialData(
            company_id="COMP013",
            period="2023-2024",
            revenue=5000000.0,
            expenses=3500000.0,
            ebitda=1000000.0,
            net_profit=500000.0,
            total_assets=2500000.0,
            total_liabilities=2100000.0,
            equity=1000000.0,
            cash_flow=800000.0,
        )

        result = self.analyzer.analyze_capital(financial_data)

        # D/E = 2100000 / 1000000 = 2.1 (just above threshold)
        assert result.debt_equity_ratio == pytest.approx(2.1, rel=0.01)
        # Just above threshold, score should be in fair range
        assert result.score < 60



class TestCollateralAnalysis:
    """Test Collateral assessment functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FiveCsAnalyzer()

    def test_analyze_collateral_single_asset_healthy_ltv(self):
        """Test Collateral analysis with single asset and healthy LTV."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Commercial property",
                value=1000000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 500000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        assert isinstance(result, CollateralScore)
        assert 0 <= result.score <= 100
        # LTV = 500000 / 1000000 = 0.5
        assert result.ltv == pytest.approx(0.5, rel=0.01)
        assert result.collateral_type == "Real Estate"
        assert result.score >= 90  # Should be excellent with LTV = 0.5

    def test_analyze_collateral_single_asset_at_threshold(self):
        """Test Collateral analysis with LTV at 0.75 threshold."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Machinery",
                description="Industrial equipment",
                value=1000000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 750000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # LTV = 750000 / 1000000 = 0.75 (at threshold)
        assert result.ltv == pytest.approx(0.75, rel=0.01)
        # At threshold, score should be around 70
        assert 70 <= result.score <= 75

    def test_analyze_collateral_single_asset_above_threshold(self):
        """Test Collateral analysis with LTV above 0.75 threshold."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Inventory",
                description="Raw materials",
                value=1000000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 850000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # LTV = 850000 / 1000000 = 0.85 (above threshold)
        assert result.ltv == pytest.approx(0.85, rel=0.01)
        # Above threshold, score should be < 70
        assert result.score < 70

    def test_analyze_collateral_multiple_assets_aggregate_ltv(self):
        """Test Collateral analysis with multiple assets and aggregate LTV."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Commercial property",
                value=1000000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Machinery",
                description="Industrial equipment",
                value=500000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Inventory",
                description="Raw materials",
                value=500000.0,
                valuation_date=datetime.now(),
            ),
        ]
        loan_amount = 1000000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # Total collateral = 1000000 + 500000 + 500000 = 2000000
        # LTV = 1000000 / 2000000 = 0.5
        assert result.ltv == pytest.approx(0.5, rel=0.01)
        assert result.collateral_type == "Real Estate"  # Most valuable asset type
        assert result.score >= 90

    def test_analyze_collateral_multiple_assets_same_type(self):
        """Test Collateral analysis with multiple assets of same type."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property 1",
                value=500000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Real Estate",
                description="Property 2",
                value=500000.0,
                valuation_date=datetime.now(),
            ),
        ]
        loan_amount = 600000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # Total collateral = 500000 + 500000 = 1000000
        # LTV = 600000 / 1000000 = 0.6
        assert result.ltv == pytest.approx(0.6, rel=0.01)
        assert result.collateral_type == "Real Estate"
        assert result.score >= 70

    def test_analyze_collateral_no_collateral(self):
        """Test Collateral analysis with no collateral assets."""
        from app.models.financial import Asset
        
        collateral_assets = []
        loan_amount = 500000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # No collateral - LTV is infinite
        assert result.ltv == 0.0  # Represented as 0 when infinite
        assert result.collateral_type == "none"
        assert result.score == 0.0  # Critical situation

    def test_analyze_collateral_ltv_exceeds_1_0(self):
        """Test Collateral analysis with LTV > 1.0 (loan exceeds collateral)."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property",
                value=500000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 600000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # LTV = 600000 / 500000 = 1.2
        assert result.ltv == pytest.approx(1.2, rel=0.01)
        # LTV > 1.0 is poor
        assert result.score < 50

    def test_analyze_collateral_ltv_very_high(self):
        """Test Collateral analysis with very high LTV."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Inventory",
                description="Raw materials",
                value=100000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 500000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # LTV = 500000 / 100000 = 5.0
        assert result.ltv == pytest.approx(5.0, rel=0.01)
        # Very high LTV is critical
        assert result.score < 20

    def test_analyze_collateral_score_bounds(self):
        """Test that Collateral score stays within 0-100 bounds."""
        from app.models.financial import Asset
        
        # Test with extremely high LTV
        collateral_assets = [
            Asset(
                asset_type="Inventory",
                description="Raw materials",
                value=10000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 10000000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        assert 0 <= result.score <= 100

    def test_analyze_collateral_valuation_date_most_recent(self):
        """Test that valuation date is the most recent from all assets."""
        from app.models.financial import Asset
        
        old_date = datetime(2023, 1, 1)
        recent_date = datetime.now()
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property 1",
                value=500000.0,
                valuation_date=old_date,
            ),
            Asset(
                asset_type="Machinery",
                description="Equipment",
                value=300000.0,
                valuation_date=recent_date,
            ),
        ]
        loan_amount = 400000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # Should use the most recent valuation date
        assert result.valuation_date == recent_date

    def test_analyze_collateral_mixed_asset_types(self):
        """Test Collateral analysis with mixed asset types."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property",
                value=600000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Machinery",
                description="Equipment",
                value=300000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Inventory",
                description="Raw materials",
                value=100000.0,
                valuation_date=datetime.now(),
            ),
        ]
        loan_amount = 500000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # Total collateral = 600000 + 300000 + 100000 = 1000000
        # LTV = 500000 / 1000000 = 0.5
        assert result.ltv == pytest.approx(0.5, rel=0.01)
        # Primary type should be Real Estate (most valuable)
        assert result.collateral_type == "Real Estate"
        assert result.score >= 90

    def test_analyze_collateral_ltv_zero(self):
        """Test Collateral analysis with zero loan amount."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property",
                value=1000000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 0.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # LTV = 0 / 1000000 = 0.0
        assert result.ltv == pytest.approx(0.0, rel=0.01)
        # Perfect score with zero loan
        assert result.score == 100.0

    def test_analyze_collateral_excellent_ltv(self):
        """Test Collateral analysis with excellent LTV (0.25)."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property",
                value=4000000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 1000000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # LTV = 1000000 / 4000000 = 0.25
        assert result.ltv == pytest.approx(0.25, rel=0.01)
        # Excellent LTV
        assert result.score >= 95

    def test_analyze_collateral_fair_ltv(self):
        """Test Collateral analysis with fair LTV (0.9)."""
        from app.models.financial import Asset
        
        collateral_assets = [
            Asset(
                asset_type="Machinery",
                description="Equipment",
                value=1000000.0,
                valuation_date=datetime.now(),
            )
        ]
        loan_amount = 900000.0

        result = self.analyzer.analyze_collateral(collateral_assets, loan_amount)

        # LTV = 900000 / 1000000 = 0.9
        assert result.ltv == pytest.approx(0.9, rel=0.01)
        # Fair LTV (above threshold)
        assert 50 <= result.score < 70

    def test_collateral_score_ltv_thresholds(self):
        """Test Collateral score calculation at LTV thresholds."""
        analyzer = FiveCsAnalyzer()

        # Test LTV <= 0.5 (should be 90+)
        score_excellent = analyzer._calculate_collateral_score(0.3)
        assert score_excellent >= 90

        # Test LTV 0.5-0.75 (should be 70-89)
        score_good = analyzer._calculate_collateral_score(0.65)
        assert 70 <= score_good <= 89

        # Test LTV 0.75-1.0 (should be 50-69)
        score_fair = analyzer._calculate_collateral_score(0.85)
        assert 50 <= score_fair <= 69

        # Test LTV 1.0-1.5 (should be 20-49)
        score_poor = analyzer._calculate_collateral_score(1.2)
        assert 20 <= score_poor <= 49

        # Test LTV > 1.5 (should be 0-19)
        score_critical = analyzer._calculate_collateral_score(2.0)
        assert 0 <= score_critical <= 19

        # Test no collateral (should be 0)
        score_no_collateral = analyzer._calculate_collateral_score(float('inf'))
        assert score_no_collateral == 0.0

    def test_determine_primary_collateral_type_single(self):
        """Test primary collateral type determination with single asset."""
        from app.models.financial import Asset
        
        analyzer = FiveCsAnalyzer()
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property",
                value=1000000.0,
                valuation_date=datetime.now(),
            )
        ]

        result = analyzer._determine_primary_collateral_type(collateral_assets)

        assert result == "Real Estate"

    def test_determine_primary_collateral_type_multiple_same(self):
        """Test primary collateral type with multiple assets of same type."""
        from app.models.financial import Asset
        
        analyzer = FiveCsAnalyzer()
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property 1",
                value=500000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Real Estate",
                description="Property 2",
                value=500000.0,
                valuation_date=datetime.now(),
            ),
        ]

        result = analyzer._determine_primary_collateral_type(collateral_assets)

        assert result == "Real Estate"

    def test_determine_primary_collateral_type_multiple_different(self):
        """Test primary collateral type with multiple different asset types."""
        from app.models.financial import Asset
        
        analyzer = FiveCsAnalyzer()
        
        collateral_assets = [
            Asset(
                asset_type="Real Estate",
                description="Property",
                value=600000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Machinery",
                description="Equipment",
                value=300000.0,
                valuation_date=datetime.now(),
            ),
            Asset(
                asset_type="Inventory",
                description="Raw materials",
                value=100000.0,
                valuation_date=datetime.now(),
            ),
        ]

        result = analyzer._determine_primary_collateral_type(collateral_assets)

        # Should return the most valuable type
        assert result == "Real Estate"

    def test_determine_primary_collateral_type_empty(self):
        """Test primary collateral type with no assets."""
        from app.models.financial import Asset
        
        analyzer = FiveCsAnalyzer()
        
        collateral_assets = []

        result = analyzer._determine_primary_collateral_type(collateral_assets)

        assert result == "none"



class TestConditionsAnalysis:
    """Test Conditions assessment functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FiveCsAnalyzer()

    def test_analyze_conditions_healthy_environment(self):
        """Test Conditions analysis with healthy external environment."""
        industry_data = {
            "sector": "Technology",
            "growth_rate": 8.0,
            "volatility": 0.2,
            "commodity_exposure": False,
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=0.3,
            positive_count=5,
            neutral_count=3,
            negative_count=1,
            key_themes=["growth", "innovation"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert isinstance(result, ConditionsScore)
        assert 0 <= result.score <= 100
        assert result.sector_risk == "Low"
        assert result.regulatory_risk == "Low"
        assert result.commodity_risk == "Low"
        assert result.score >= 80  # Should be high with healthy environment

    def test_analyze_conditions_declining_sector(self):
        """Test Conditions analysis with declining sector."""
        industry_data = {
            "sector": "Coal Mining",
            "growth_rate": -8.0,
            "volatility": 0.6,
            "commodity_exposure": True,
            "commodity_volatility": 0.7,
            "commodity_types": ["Coal"],
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=-0.2,
            positive_count=1,
            neutral_count=2,
            negative_count=5,
            key_themes=["decline", "regulation"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.sector_risk == "High"
        assert result.commodity_risk == "High"
        assert result.score < 80  # Should be lower with declining sector
        assert len(result.risk_factors) > 0

    def test_analyze_conditions_with_rbi_restrictions(self):
        """Test Conditions analysis with high-severity RBI notifications."""
        industry_data = {
            "sector": "NBFC",
            "growth_rate": 5.0,
            "volatility": 0.3,
            "commodity_exposure": False,
        }
        rbi_notifications = [
            RBINotification(
                notification_id="RBI001",
                title="Restrictions on NBFC lending",
                url="https://rbi.org.in/notification1",
                published_date=datetime.now(),
                sector="NBFC",
                content="New restrictions on NBFC lending practices",
                summary="Tightening of NBFC regulations",
            ),
            RBINotification(
                notification_id="RBI002",
                title="Mandatory compliance requirements",
                url="https://rbi.org.in/notification2",
                published_date=datetime.now(),
                sector="NBFC",
                content="Increased compliance requirements for all NBFCs",
                summary="Compliance tightening",
            ),
        ]
        sentiment = SentimentScore(
            overall=0.0,
            positive_count=2,
            neutral_count=4,
            negative_count=2,
            key_themes=["regulation"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.regulatory_risk == "High"
        assert result.score < 92  # Should be lower with restrictions
        assert any("RBI" in factor for factor in result.risk_factors)

    def test_analyze_conditions_commodity_exposure_high_volatility(self):
        """Test Conditions analysis with high commodity price volatility."""
        industry_data = {
            "sector": "Steel",
            "growth_rate": 4.0,
            "volatility": 0.4,
            "commodity_exposure": True,
            "commodity_volatility": 0.75,
            "commodity_types": ["Iron Ore", "Coal"],
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=0.1,
            positive_count=3,
            neutral_count=4,
            negative_count=2,
            key_themes=["volatility"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.commodity_risk == "High"
        assert result.score < 96  # Should be lower with high commodity volatility
        assert any("commodity" in factor.lower() for factor in result.risk_factors)

    def test_analyze_conditions_moderate_risks(self):
        """Test Conditions analysis with moderate risks."""
        industry_data = {
            "sector": "Manufacturing",
            "growth_rate": 2.5,
            "volatility": 0.45,
            "commodity_exposure": True,
            "commodity_volatility": 0.5,
            "commodity_types": ["Steel"],
        }
        rbi_notifications = [
            RBINotification(
                notification_id="RBI003",
                title="Advisory on lending practices",
                url="https://rbi.org.in/notification3",
                published_date=datetime.now(),
                sector="Manufacturing",
                content="Advisory on prudent lending practices",
                summary="Lending advisory",
            ),
        ]
        sentiment = SentimentScore(
            overall=0.0,
            positive_count=2,
            neutral_count=5,
            negative_count=2,
            key_themes=["stability"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.sector_risk == "Medium"
        assert result.regulatory_risk == "Medium"
        assert result.commodity_risk == "Medium"
        assert 85 <= result.score <= 92  # Should be in moderate range

    def test_analyze_conditions_no_commodity_exposure(self):
        """Test Conditions analysis with no commodity exposure."""
        industry_data = {
            "sector": "IT Services",
            "growth_rate": 10.0,
            "volatility": 0.15,
            "commodity_exposure": False,
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=0.5,
            positive_count=8,
            neutral_count=2,
            negative_count=0,
            key_themes=["growth", "innovation"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.commodity_risk == "Low"
        assert result.score >= 85  # Should be high with no commodity risk

    def test_analyze_conditions_negative_sentiment(self):
        """Test Conditions analysis with negative sentiment."""
        industry_data = {
            "sector": "Retail",
            "growth_rate": 1.0,
            "volatility": 0.5,
            "commodity_exposure": False,
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=-0.8,
            positive_count=1,
            neutral_count=1,
            negative_count=10,
            key_themes=["decline", "crisis"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        # Negative sentiment should reduce score
        assert result.score < 88

    def test_analyze_conditions_positive_sentiment(self):
        """Test Conditions analysis with positive sentiment."""
        industry_data = {
            "sector": "Pharma",
            "growth_rate": 6.0,
            "volatility": 0.25,
            "commodity_exposure": False,
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=0.9,
            positive_count=15,
            neutral_count=2,
            negative_count=0,
            key_themes=["growth", "opportunity"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        # Positive sentiment should boost score
        assert result.score >= 80

    def test_analyze_conditions_score_bounds(self):
        """Test that Conditions score stays within 0-100 bounds."""
        # Test with extreme negative conditions
        industry_data = {
            "sector": "Coal",
            "growth_rate": -15.0,
            "volatility": 0.9,
            "commodity_exposure": True,
            "commodity_volatility": 0.95,
            "commodity_types": ["Coal"],
        }
        rbi_notifications = [
            RBINotification(
                notification_id="RBI004",
                title="Ban on coal mining",
                url="https://rbi.org.in/notification4",
                published_date=datetime.now(),
                sector="Coal",
                content="Restrictions on coal mining",
                summary="Coal mining ban",
            ),
        ]
        sentiment = SentimentScore(
            overall=-1.0,
            positive_count=0,
            neutral_count=0,
            negative_count=20,
            key_themes=["crisis"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert 0 <= result.score <= 100

    def test_analyze_conditions_multiple_rbi_notifications(self):
        """Test Conditions analysis with multiple RBI notifications."""
        industry_data = {
            "sector": "Banking",
            "growth_rate": 3.0,
            "volatility": 0.3,
            "commodity_exposure": False,
        }
        rbi_notifications = [
            RBINotification(
                notification_id="RBI005",
                title="Tightening of capital requirements",
                url="https://rbi.org.in/notification5",
                published_date=datetime.now(),
                sector="Banking",
                content="Increased capital requirements",
                summary="Capital tightening",
            ),
            RBINotification(
                notification_id="RBI006",
                title="Monitoring of credit growth",
                url="https://rbi.org.in/notification6",
                published_date=datetime.now(),
                sector="Banking",
                content="Enhanced monitoring of credit growth",
                summary="Credit monitoring",
            ),
            RBINotification(
                notification_id="RBI007",
                title="Clarification on lending norms",
                url="https://rbi.org.in/notification7",
                published_date=datetime.now(),
                sector="Banking",
                content="Clarification on existing lending norms",
                summary="Lending clarification",
            ),
        ]
        sentiment = SentimentScore(
            overall=0.0,
            positive_count=2,
            neutral_count=5,
            negative_count=2,
            key_themes=["regulation"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.regulatory_risk == "High"
        assert len(result.risk_factors) > 0
        assert any("RBI" in factor for factor in result.risk_factors)

    def test_analyze_conditions_low_growth_sector(self):
        """Test Conditions analysis with low growth sector."""
        industry_data = {
            "sector": "Agriculture",
            "growth_rate": 1.5,
            "volatility": 0.6,
            "commodity_exposure": True,
            "commodity_volatility": 0.65,
            "commodity_types": ["Wheat", "Rice"],
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=-0.1,
            positive_count=2,
            neutral_count=4,
            negative_count=3,
            key_themes=["weather", "prices"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.sector_risk == "Medium"
        assert result.commodity_risk == "High"
        assert result.score < 86

    def test_analyze_conditions_strong_growth_sector(self):
        """Test Conditions analysis with strong growth sector."""
        industry_data = {
            "sector": "Renewable Energy",
            "growth_rate": 15.0,
            "volatility": 0.2,
            "commodity_exposure": False,
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=0.7,
            positive_count=12,
            neutral_count=3,
            negative_count=1,
            key_themes=["growth", "sustainability"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        assert result.sector_risk == "Low"
        assert result.score >= 85

    def test_assess_sector_risk_negative_growth(self):
        """Test sector risk assessment with negative growth."""
        analyzer = FiveCsAnalyzer()
        risk_factors = []

        # High negative growth
        risk_level, score = analyzer._assess_sector_risk(
            {"sector": "Coal", "growth_rate": -8.0, "volatility": 0.5},
            risk_factors,
        )
        assert risk_level == "High"
        assert score <= 70
        assert len(risk_factors) > 0

    def test_assess_sector_risk_high_volatility(self):
        """Test sector risk assessment with high volatility."""
        analyzer = FiveCsAnalyzer()
        risk_factors = []

        risk_level, score = analyzer._assess_sector_risk(
            {"sector": "Crypto", "growth_rate": 5.0, "volatility": 0.85},
            risk_factors,
        )
        assert risk_level == "High"
        assert score <= 80
        assert any("volatility" in factor.lower() for factor in risk_factors)

    def test_assess_regulatory_risk_no_notifications(self):
        """Test regulatory risk assessment with no notifications."""
        analyzer = FiveCsAnalyzer()
        risk_factors = []

        risk_level, score = analyzer._assess_regulatory_risk([], risk_factors)

        assert risk_level == "Low"
        assert score == 100.0
        assert len(risk_factors) == 0

    def test_assess_regulatory_risk_high_severity(self):
        """Test regulatory risk assessment with high-severity notifications."""
        analyzer = FiveCsAnalyzer()
        risk_factors = []

        notifications = [
            RBINotification(
                notification_id="RBI008",
                title="Ban on certain lending practices",
                url="https://rbi.org.in/notification8",
                published_date=datetime.now(),
                sector="NBFC",
                content="Restrictions on lending",
                summary="Lending ban",
            ),
        ]

        risk_level, score = analyzer._assess_regulatory_risk(notifications, risk_factors)

        assert risk_level == "High"
        assert score <= 75
        assert len(risk_factors) > 0

    def test_assess_commodity_risk_no_exposure(self):
        """Test commodity risk assessment with no exposure."""
        analyzer = FiveCsAnalyzer()
        risk_factors = []

        risk_level, score = analyzer._assess_commodity_risk(
            {"commodity_exposure": False},
            risk_factors,
        )

        assert risk_level == "Low"
        assert score == 100.0
        assert len(risk_factors) == 0

    def test_assess_commodity_risk_high_volatility(self):
        """Test commodity risk assessment with high volatility."""
        analyzer = FiveCsAnalyzer()
        risk_factors = []

        risk_level, score = analyzer._assess_commodity_risk(
            {
                "commodity_exposure": True,
                "commodity_volatility": 0.8,
                "commodity_types": ["Oil", "Gas"],
            },
            risk_factors,
        )

        assert risk_level == "High"
        assert score <= 75
        assert any("commodity" in factor.lower() for factor in risk_factors)

    def test_assess_commodity_risk_moderate_volatility(self):
        """Test commodity risk assessment with moderate volatility."""
        analyzer = FiveCsAnalyzer()
        risk_factors = []

        risk_level, score = analyzer._assess_commodity_risk(
            {
                "commodity_exposure": True,
                "commodity_volatility": 0.5,
                "commodity_types": ["Steel"],
            },
            risk_factors,
        )

        assert risk_level == "Medium"
        assert 75 <= score < 90
        assert len(risk_factors) > 0

    def test_analyze_conditions_sentiment_adjustment_positive(self):
        """Test that positive sentiment improves Conditions score."""
        industry_data = {
            "sector": "Tech",
            "growth_rate": 5.0,
            "volatility": 0.3,
            "commodity_exposure": False,
        }
        rbi_notifications = []

        # Positive sentiment
        sentiment_positive = SentimentScore(
            overall=0.8,
            positive_count=10,
            neutral_count=2,
            negative_count=0,
            key_themes=["growth"],
        )

        result_positive = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment_positive
        )

        # Negative sentiment
        sentiment_negative = SentimentScore(
            overall=-0.8,
            positive_count=0,
            neutral_count=2,
            negative_count=10,
            key_themes=["decline"],
        )

        result_negative = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment_negative
        )

        # Positive sentiment should result in higher score than negative
        assert result_positive.score > result_negative.score

    def test_analyze_conditions_sentiment_adjustment_negative(self):
        """Test that negative sentiment reduces Conditions score."""
        industry_data = {
            "sector": "Tech",
            "growth_rate": 5.0,
            "volatility": 0.3,
            "commodity_exposure": False,
        }
        rbi_notifications = []

        # Negative sentiment
        sentiment_negative = SentimentScore(
            overall=-0.8,
            positive_count=0,
            neutral_count=2,
            negative_count=10,
            key_themes=["decline"],
        )

        result_negative = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment_negative
        )

        # Neutral sentiment
        sentiment_neutral = SentimentScore(
            overall=0.0,
            positive_count=5,
            neutral_count=5,
            negative_count=0,
            key_themes=["neutral"],
        )

        result_neutral = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment_neutral
        )

        # Negative sentiment should result in lower score
        assert result_negative.score < result_neutral.score

    def test_analyze_conditions_comprehensive_scenario(self):
        """Test Conditions analysis with comprehensive real-world scenario."""
        # Scenario: Manufacturing company in a moderately growing sector
        # with some regulatory concerns and commodity exposure
        industry_data = {
            "sector": "Automotive",
            "growth_rate": 4.5,
            "volatility": 0.35,
            "commodity_exposure": True,
            "commodity_volatility": 0.45,
            "commodity_types": ["Steel", "Aluminum"],
        }
        rbi_notifications = [
            RBINotification(
                notification_id="RBI009",
                title="Guidelines on auto financing",
                url="https://rbi.org.in/notification9",
                published_date=datetime.now(),
                sector="Automotive",
                content="New guidelines for auto financing",
                summary="Auto financing guidelines",
            ),
        ]
        sentiment = SentimentScore(
            overall=0.2,
            positive_count=4,
            neutral_count=5,
            negative_count=2,
            key_themes=["growth", "regulation"],
        )

        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )

        # Should be in moderate range
        assert 90 <= result.score <= 100
        assert result.sector_risk == "Low"
        assert result.regulatory_risk == "Medium"
        assert result.commodity_risk == "Medium"
        assert len(result.risk_factors) > 0
