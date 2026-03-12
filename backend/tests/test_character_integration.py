"""Integration tests for Character analysis."""

import pytest
from datetime import datetime, timedelta
from app.services.credit_engine import FiveCsAnalyzer
from app.models.research import LegalCase, MCAData


class TestCharacterIntegration:
    """Integration tests for Character assessment."""

    def test_character_analysis_realistic_scenario(self):
        """Test Character analysis with a realistic business scenario."""
        analyzer = FiveCsAnalyzer()

        # Scenario: Mid-sized company with minor compliance issues
        promoter_data = {
            "name": "Rajesh Kumar",
            "din": "87654321",
            "shareholding": 51.0,
            "role": "Managing Director",
        }

        # One minor civil dispute
        legal_cases = [
            LegalCase(
                case_number="CS/2023/12345",
                court="District Court, Mumbai",
                filing_date=datetime(2023, 6, 15),
                case_type="civil contract dispute",
                status="pending",
                summary="Dispute with vendor over payment terms",
                parties=["ABC Manufacturing Ltd", "XYZ Suppliers"],
            )
        ]

        # Partially compliant MCA status
        mca_data = MCAData(
            cin="U25209MH2015PTC123456",
            company_name="ABC Manufacturing Ltd",
            registration_date=datetime(2015, 3, 10),
            authorized_capital=10000000.0,
            paid_up_capital=7500000.0,
            last_filing_date=datetime.now() - timedelta(days=200),
            compliance_status="partially_compliant",
            directors=[
                {"name": "Rajesh Kumar", "din": "87654321", "designation": "MD"},
                {"name": "Priya Sharma", "din": "12348765", "designation": "Director"},
            ],
        )

        # Good credit bureau score
        credit_bureau_score = 720.0

        result = analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        # Assertions for realistic scenario
        assert isinstance(result.score, float)
        assert 60 <= result.score <= 85  # Should be in medium-good range
        assert result.litigation_count == 1
        assert result.governance_rating in ["Fair", "Good"]
        assert result.credit_bureau_score == 720.0
        assert len(result.negative_factors) >= 1  # At least partial compliance issue

    def test_character_analysis_excellent_profile(self):
        """Test Character analysis for an excellent borrower profile."""
        analyzer = FiveCsAnalyzer()

        promoter_data = {
            "name": "Sunita Patel",
            "din": "11223344",
            "shareholding": 75.0,
            "role": "CEO",
        }

        # No legal cases
        legal_cases = []

        # Fully compliant with recent filing
        mca_data = MCAData(
            cin="U72900KA2018PTC987654",
            company_name="TechCorp Solutions Pvt Ltd",
            registration_date=datetime(2018, 1, 15),
            authorized_capital=5000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=45),
            compliance_status="compliant",
            directors=[
                {"name": "Sunita Patel", "din": "11223344", "designation": "CEO"},
                {"name": "Amit Verma", "din": "55667788", "designation": "CFO"},
                {"name": "Neha Singh", "din": "99887766", "designation": "CTO"},
            ],
        )

        # Excellent credit score
        credit_bureau_score = 850.0

        result = analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        # Should have excellent score
        assert result.score >= 90
        assert result.litigation_count == 0
        assert result.governance_rating == "Good"
        assert len(result.negative_factors) == 0

    def test_character_analysis_high_risk_profile(self):
        """Test Character analysis for a high-risk borrower profile."""
        analyzer = FiveCsAnalyzer()

        promoter_data = {
            "name": "Troubled Promoter",
            "din": "99999999",
            "shareholding": 100.0,
            "role": "Director",
        }

        # Multiple serious legal cases
        legal_cases = [
            LegalCase(
                case_number="CBI/2022/001",
                court="Special CBI Court",
                filing_date=datetime(2022, 3, 1),
                case_type="fraud and misappropriation",
                status="ongoing",
                summary="Alleged fraud in loan application",
                parties=["Troubled Company", "Bank of India"],
            ),
            LegalCase(
                case_number="CR/2023/456",
                court="High Court",
                filing_date=datetime(2023, 1, 10),
                case_type="criminal breach of trust",
                status="pending",
                summary="Criminal case for breach of trust",
                parties=["Troubled Company", "Investors"],
            ),
            LegalCase(
                case_number="IB/2023/789",
                court="NCLT",
                filing_date=datetime(2023, 5, 20),
                case_type="insolvency proceedings",
                status="admitted",
                summary="Insolvency petition admitted",
                parties=["Troubled Company", "Creditors"],
            ),
        ]

        # Non-compliant with overdue filings
        mca_data = MCAData(
            cin="U99999XX2010PTC000000",
            company_name="Troubled Company Ltd",
            registration_date=datetime(2010, 6, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=600),
            compliance_status="non-compliant",
            directors=[],  # No director information
        )

        # Poor credit score
        credit_bureau_score = 450.0

        result = analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        # Should have very low score
        assert result.score < 40
        assert result.litigation_count == 3
        assert result.governance_rating == "Poor"
        assert len(result.negative_factors) >= 3
        assert any("fraud" in factor.lower() for factor in result.negative_factors)

    def test_character_score_consistency(self):
        """Test that Character score is consistent for same inputs."""
        analyzer = FiveCsAnalyzer()

        promoter_data = {"name": "Test", "din": "12345678"}
        legal_cases = []
        mca_data = MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=1000000.0,
            paid_up_capital=500000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="compliant",
            directors=[{"name": "Test", "din": "12345678"}],
        )
        credit_bureau_score = 750.0

        # Run analysis multiple times
        result1 = analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )
        result2 = analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )
        result3 = analyzer.analyze_character(
            promoter_data, legal_cases, mca_data, credit_bureau_score
        )

        # Results should be identical
        assert result1.score == result2.score == result3.score
        assert result1.litigation_count == result2.litigation_count == result3.litigation_count
        assert result1.governance_rating == result2.governance_rating == result3.governance_rating
