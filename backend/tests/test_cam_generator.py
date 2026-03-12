"""Tests for CAM Generator service."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.cam_generator.cam_generator import CAMGenerator
from app.models.cam import CAMDocument, AuditTrail, AuditEvent
from app.models.credit_assessment import (
    FiveCsScores,
    CharacterScore,
    CapacityScore,
    CapitalScore,
    CollateralScore,
    ConditionsScore,
    RiskScore,
    LoanRecommendation,
    Explanation,
)
from app.models.financial import FinancialData
from app.models.company import Company, Promoter
from app.models.research import MCAData


@pytest.fixture
def sample_company():
    """Create sample company data."""
    return Company(
        company_id="comp_001",
        cin="U12345AB2020PTC123456",
        gstin="27AABCT1234H1Z0",
        name="Sample Manufacturing Ltd",
        industry="Manufacturing",
        incorporation_date=datetime(2020, 1, 15),
        promoters=[
            Promoter(
                name="John Doe",
                din="00123456",
                shareholding=60.0,
                role="Managing Director",
            ),
            Promoter(
                name="Jane Smith",
                din="00234567",
                shareholding=40.0,
                role="Director",
            ),
        ],
    )


@pytest.fixture
def sample_financial_data():
    """Create sample financial data."""
    return FinancialData(
        company_id="comp_001",
        period="FY 2023-24",
        revenue=50000000.0,
        expenses=35000000.0,
        ebitda=15000000.0,
        net_profit=10000000.0,
        total_assets=100000000.0,
        total_liabilities=40000000.0,
        equity=60000000.0,
        cash_flow=12000000.0,
        confidence_scores={"revenue": 0.95, "expenses": 0.92},
    )


@pytest.fixture
def sample_mca_data():
    """Create sample MCA data."""
    return MCAData(
        cin="U12345AB2020PTC123456",
        company_name="Sample Manufacturing Ltd",
        registration_date=datetime(2020, 1, 15),
        authorized_capital=10000000.0,
        paid_up_capital=5000000.0,
        last_filing_date=datetime(2024, 1, 31),
        compliance_status="Compliant",
        directors=[
            {"name": "John Doe", "din": "00123456"},
            {"name": "Jane Smith", "din": "00234567"},
        ],
    )


@pytest.fixture
def sample_five_cs_scores():
    """Create sample Five Cs scores."""
    return FiveCsScores(
        character=CharacterScore(
            score=85.0,
            litigation_count=0,
            governance_rating="Good",
            credit_bureau_score=750.0,
            negative_factors=[],
        ),
        capacity=CapacityScore(
            score=80.0,
            dscr=1.8,
            cash_flow=12000000.0,
            debt_service=6666666.67,
            trend="improving",
        ),
        capital=CapitalScore(
            score=75.0,
            debt_equity_ratio=0.67,
            net_worth=60000000.0,
            net_worth_trend="stable",
        ),
        collateral=CollateralScore(
            score=70.0,
            ltv=0.5,
            collateral_type="Property",
            valuation_date=datetime.now(),
        ),
        conditions=ConditionsScore(
            score=72.0,
            sector_risk="Medium",
            regulatory_risk="Low",
            commodity_risk="Low",
            risk_factors=["Market volatility"],
        ),
    )


@pytest.fixture
def sample_risk_score():
    """Create sample risk score."""
    return RiskScore(
        overall_score=76.4,
        risk_level="low",
        top_risk_factors=["Market volatility", "Commodity price risk"],
        top_positive_factors=["Strong cash flow", "Good governance"],
    )


@pytest.fixture
def sample_loan_recommendation(sample_risk_score):
    """Create sample loan recommendation."""
    return LoanRecommendation(
        max_loan_amount=20000000.0,
        recommended_interest_rate=9.5,
        risk_score=sample_risk_score,
        limiting_constraint="EBITDA-based calculation",
        explanations={
            "character": Explanation(
                summary="Strong promoter credibility with no litigation history",
                key_factors=[("No litigation", 0.3), ("Good governance", 0.25)],
                data_sources=["e-Courts database", "MCA filings"],
                reasoning="Promoters have clean track record",
            ),
            "capacity": Explanation(
                summary="Strong repayment capacity with DSCR of 1.8",
                key_factors=[("DSCR", 0.35), ("Cash flow trend", 0.25)],
                data_sources=["Financial statements"],
                reasoning="DSCR well above 1.25 threshold",
            ),
            "capital": Explanation(
                summary="Adequate capital structure with D/E ratio of 0.67",
                key_factors=[("Debt/Equity ratio", 0.3), ("Net worth", 0.25)],
                data_sources=["Balance sheet"],
                reasoning="D/E ratio below 2.0 threshold",
            ),
            "collateral": Explanation(
                summary="Sufficient collateral with LTV of 0.5",
                key_factors=[("LTV ratio", 0.35), ("Asset quality", 0.2)],
                data_sources=["Collateral valuation report"],
                reasoning="LTV well below 0.75 threshold",
            ),
            "conditions": Explanation(
                summary="Moderate external risk factors",
                key_factors=[("Sector risk", 0.25), ("Regulatory risk", 0.15)],
                data_sources=["Industry reports", "RBI notifications"],
                reasoning="Manufacturing sector has moderate growth",
            ),
        },
    )


@pytest.fixture
def sample_audit_trail():
    """Create sample audit trail."""
    trail = AuditTrail()
    now = datetime.now()

    trail.events = [
        AuditEvent(
            timestamp=now - timedelta(hours=2),
            event_type="data_ingestion",
            description="Financial statements extracted from annual report",
            user="credit_officer_001",
            data={"document_type": "annual_report", "pages": 45},
        ),
        AuditEvent(
            timestamp=now - timedelta(hours=1, minutes=30),
            event_type="research_activity",
            description="MCA filings retrieved",
            user=None,
            data={"source": "MCA API", "records": 5},
        ),
        AuditEvent(
            timestamp=now - timedelta(hours=1),
            event_type="calculation",
            description="DSCR calculated",
            user=None,
            data={"formula": "cash_flow / debt_service", "result": 1.8},
        ),
        AuditEvent(
            timestamp=now - timedelta(minutes=30),
            event_type="calculation",
            description="Risk score aggregated",
            user=None,
            data={"formula": "weighted_five_cs", "result": 76.4},
        ),
    ]

    return trail


@pytest.fixture
def sample_research_data(sample_mca_data):
    """Create sample research data."""
    return {
        "mca_data": sample_mca_data,
        "industry_data": {
            "name": "Manufacturing",
            "market_size": "₹500 Crore",
            "growth_rate": "8.5%",
        },
        "sentiment": {
            "overall": "Positive",
            "positive_count": 5,
            "negative_count": 1,
        },
        "conditions_score": {
            "sector_risk": "Medium",
            "regulatory_risk": "Low",
            "commodity_risk": "Low",
        },
        "ratios": {
            "DSCR": 1.8,
            "Debt/Equity": 0.67,
            "LTV": 0.5,
            "ROE": 0.167,
            "ROA": 0.1,
        },
    }


class TestCAMGeneratorBasics:
    """Test basic CAM Generator functionality."""

    def test_cam_generator_initialization(self):
        """Test CAM Generator can be initialized."""
        generator = CAMGenerator()
        assert generator is not None
        assert generator.audit_trail is not None

    def test_generate_executive_summary(self, sample_loan_recommendation):
        """Test executive summary generation."""
        generator = CAMGenerator()
        summary = generator.generate_executive_summary(sample_loan_recommendation)

        assert "EXECUTIVE SUMMARY" in summary
        assert "LOW" in summary  # Risk level
        assert "76.20" in summary or "76.4" in summary  # Risk score
        assert "₹20,000,000.00" in summary  # Loan amount
        assert "9.50" in summary  # Interest rate
        assert "Market volatility" in summary  # Risk factor

    def test_generate_company_overview(self, sample_company, sample_mca_data):
        """Test company overview generation."""
        generator = CAMGenerator()
        overview = generator.generate_company_overview(sample_company, sample_mca_data)

        assert "COMPANY OVERVIEW" in overview
        assert "Sample Manufacturing Ltd" in overview
        assert "U12345AB2020PTC123456" in overview
        assert "27AABCT1234H1Z0" in overview
        assert "Manufacturing" in overview
        assert "John Doe" in overview
        assert "Jane Smith" in overview
        assert "Compliant" in overview

    def test_generate_company_overview_without_mca(self, sample_company):
        """Test company overview generation without MCA data."""
        generator = CAMGenerator()
        overview = generator.generate_company_overview(sample_company, None)

        assert "COMPANY OVERVIEW" in overview
        assert "Sample Manufacturing Ltd" in overview
        assert "John Doe" in overview

    def test_generate_industry_analysis(self, sample_research_data, sample_risk_score):
        """Test industry analysis generation."""
        generator = CAMGenerator()
        analysis = generator.generate_industry_analysis(
            sample_research_data, sample_risk_score
        )

        assert "INDUSTRY ANALYSIS" in analysis
        assert "Manufacturing" in analysis
        assert "8.5%" in analysis
        assert "Medium" in analysis  # Sector risk

    def test_generate_financial_analysis(self, sample_financial_data, sample_research_data):
        """Test financial analysis generation."""
        generator = CAMGenerator()
        analysis = generator.generate_financial_analysis(
            sample_financial_data, sample_research_data["ratios"]
        )

        assert "FINANCIAL ANALYSIS" in analysis
        assert "FY 2023-24" in analysis
        assert "₹50,000,000.00" in analysis  # Revenue
        assert "₹15,000,000.00" in analysis  # EBITDA
        assert "1.8" in analysis  # DSCR ratio

    def test_generate_risk_assessment(self, sample_risk_score, sample_loan_recommendation):
        """Test risk assessment generation."""
        generator = CAMGenerator()
        assessment = generator.generate_risk_assessment(
            sample_risk_score, sample_loan_recommendation
        )

        assert "RISK ASSESSMENT" in assessment
        assert "76.20" in assessment or "76.4" in assessment
        assert "LOW" in assessment
        assert "Market volatility" in assessment

    def test_generate_five_cs_summary(self, sample_loan_recommendation):
        """Test Five Cs summary generation."""
        generator = CAMGenerator()
        summary = generator.generate_five_cs_summary(sample_loan_recommendation)

        assert "FIVE CS SUMMARY" in summary
        assert "CHARACTER:" in summary
        assert "CAPACITY:" in summary
        assert "CAPITAL:" in summary
        assert "COLLATERAL:" in summary
        assert "CONDITIONS:" in summary

    def test_generate_final_recommendation(self, sample_loan_recommendation):
        """Test final recommendation generation."""
        generator = CAMGenerator()
        recommendation = generator.generate_final_recommendation(
            sample_loan_recommendation
        )

        assert "FINAL RECOMMENDATION" in recommendation
        assert "LOW" in recommendation
        assert "₹20,000,000.00" in recommendation
        assert "9.50" in recommendation
        assert "Five Cs of Credit" in recommendation

    def test_add_explainability_notes(self, sample_loan_recommendation):
        """Test explainability notes generation."""
        generator = CAMGenerator()
        notes = generator.add_explainability_notes(
            sample_loan_recommendation.explanations
        )

        assert "EXPLAINABILITY NOTES" in notes
        assert "CHARACTER EXPLANATION:" in notes
        assert "CAPACITY EXPLANATION:" in notes
        assert "Strong promoter credibility" in notes
        assert "e-Courts database" in notes

    def test_add_audit_trail(self, sample_audit_trail):
        """Test audit trail generation."""
        generator = CAMGenerator()
        trail_text = generator.add_audit_trail(sample_audit_trail)

        assert "AUDIT TRAIL" in trail_text
        assert "Total Events: 4" in trail_text
        assert "DATA_INGESTION" in trail_text
        assert "RESEARCH_ACTIVITY" in trail_text
        assert "CALCULATION" in trail_text


class TestCAMDocumentGeneration:
    """Test complete CAM document generation."""

    def test_generate_cam_complete(
        self,
        sample_company,
        sample_financial_data,
        sample_research_data,
        sample_loan_recommendation,
        sample_audit_trail,
    ):
        """Test complete CAM document generation."""
        generator = CAMGenerator()
        cam_doc = generator.generate_cam(
            application_id="app_001",
            company_data=sample_company,
            financial_data=sample_financial_data,
            research_data=sample_research_data,
            loan_recommendation=sample_loan_recommendation,
            audit_trail=sample_audit_trail,
        )

        assert isinstance(cam_doc, CAMDocument)
        assert cam_doc.application_id == "app_001"
        assert cam_doc.company_name == "Sample Manufacturing Ltd"
        assert cam_doc.version == 1

    def test_cam_document_has_all_sections(
        self,
        sample_company,
        sample_financial_data,
        sample_research_data,
        sample_loan_recommendation,
        sample_audit_trail,
    ):
        """Test that CAM document contains all required sections."""
        generator = CAMGenerator()
        cam_doc = generator.generate_cam(
            application_id="app_001",
            company_data=sample_company,
            financial_data=sample_financial_data,
            research_data=sample_research_data,
            loan_recommendation=sample_loan_recommendation,
            audit_trail=sample_audit_trail,
        )

        required_sections = [
            "executive_summary",
            "company_overview",
            "industry_analysis",
            "financial_analysis",
            "risk_assessment",
            "five_cs_summary",
            "final_recommendation",
            "explainability_notes",
            "audit_trail",
        ]

        for section in required_sections:
            assert section in cam_doc.sections
            assert len(cam_doc.sections[section]) > 0

    def test_cam_document_audit_trail_preserved(
        self,
        sample_company,
        sample_financial_data,
        sample_research_data,
        sample_loan_recommendation,
        sample_audit_trail,
    ):
        """Test that audit trail is preserved in CAM document."""
        generator = CAMGenerator()
        cam_doc = generator.generate_cam(
            application_id="app_001",
            company_data=sample_company,
            financial_data=sample_financial_data,
            research_data=sample_research_data,
            loan_recommendation=sample_loan_recommendation,
            audit_trail=sample_audit_trail,
        )

        assert cam_doc.audit_trail == sample_audit_trail
        assert len(cam_doc.audit_trail.events) == 4

    def test_cam_document_generated_date(
        self,
        sample_company,
        sample_financial_data,
        sample_research_data,
        sample_loan_recommendation,
        sample_audit_trail,
    ):
        """Test that CAM document has generated date."""
        generator = CAMGenerator()
        before = datetime.now()
        cam_doc = generator.generate_cam(
            application_id="app_001",
            company_data=sample_company,
            financial_data=sample_financial_data,
            research_data=sample_research_data,
            loan_recommendation=sample_loan_recommendation,
            audit_trail=sample_audit_trail,
        )
        after = datetime.now()

        assert before <= cam_doc.generated_date <= after


class TestCAMSectionContent:
    """Test content quality of CAM sections."""

    def test_executive_summary_contains_key_metrics(self, sample_loan_recommendation):
        """Test executive summary contains all key metrics."""
        generator = CAMGenerator()
        summary = generator.generate_executive_summary(sample_loan_recommendation)

        # Check for key metrics
        assert "Risk Assessment:" in summary
        assert "Overall Risk Score:" in summary
        assert "Maximum Loan Amount:" in summary
        assert "Recommended Interest Rate:" in summary
        assert "Limiting Constraint:" in summary
        assert "Key Risk Factors:" in summary
        assert "Key Positive Factors:" in summary

    def test_financial_analysis_includes_all_line_items(self, sample_financial_data):
        """Test financial analysis includes all financial line items."""
        generator = CAMGenerator()
        analysis = generator.generate_financial_analysis(sample_financial_data, {})

        assert "Revenue:" in analysis
        assert "Expenses:" in analysis
        assert "EBITDA:" in analysis
        assert "Net Profit:" in analysis
        assert "Total Assets:" in analysis
        assert "Total Liabilities:" in analysis
        assert "Equity:" in analysis
        assert "Operating Cash Flow:" in analysis

    def test_risk_assessment_includes_five_cs(self, sample_risk_score, sample_loan_recommendation):
        """Test risk assessment includes Five Cs information."""
        generator = CAMGenerator()
        assessment = generator.generate_risk_assessment(
            sample_risk_score, sample_loan_recommendation
        )

        assert "Character Score:" in assessment
        assert "Capacity Score:" in assessment
        assert "Capital Score:" in assessment
        assert "Collateral Score:" in assessment
        assert "Conditions Score:" in assessment

    def test_audit_trail_groups_events_by_type(self, sample_audit_trail):
        """Test audit trail groups events by type."""
        generator = CAMGenerator()
        trail_text = generator.add_audit_trail(sample_audit_trail)

        assert "DATA_INGESTION" in trail_text
        assert "RESEARCH_ACTIVITY" in trail_text
        assert "CALCULATION" in trail_text


class TestCAMEdgeCases:
    """Test edge cases in CAM generation."""

    def test_cam_with_empty_explanations(
        self,
        sample_company,
        sample_financial_data,
        sample_research_data,
        sample_audit_trail,
    ):
        """Test CAM generation with minimal explanations."""
        generator = CAMGenerator()
        risk_score = RiskScore(
            overall_score=50.0,
            risk_level="medium",
            top_risk_factors=[],
            top_positive_factors=[],
        )
        loan_rec = LoanRecommendation(
            max_loan_amount=10000000.0,
            recommended_interest_rate=10.0,
            risk_score=risk_score,
            limiting_constraint="Conservative approach",
            explanations={},
        )

        cam_doc = generator.generate_cam(
            application_id="app_002",
            company_data=sample_company,
            financial_data=sample_financial_data,
            research_data=sample_research_data,
            loan_recommendation=loan_rec,
            audit_trail=sample_audit_trail,
        )

        assert cam_doc is not None
        assert len(cam_doc.sections) == 9

    def test_cam_with_no_promoters(self, sample_financial_data, sample_research_data, sample_loan_recommendation, sample_audit_trail):
        """Test CAM generation with company having no promoters."""
        generator = CAMGenerator()
        company = Company(
            company_id="comp_002",
            cin="U12345AB2020PTC123457",
            gstin="27AABCT1234H1Z1",
            name="Test Company",
            industry="Services",
            incorporation_date=datetime(2020, 1, 15),
            promoters=[],
        )

        cam_doc = generator.generate_cam(
            application_id="app_003",
            company_data=company,
            financial_data=sample_financial_data,
            research_data=sample_research_data,
            loan_recommendation=sample_loan_recommendation,
            audit_trail=sample_audit_trail,
        )

        assert cam_doc is not None
        assert "Test Company" in cam_doc.sections["company_overview"]

    def test_cam_with_high_risk_score(
        self,
        sample_company,
        sample_financial_data,
        sample_research_data,
        sample_audit_trail,
    ):
        """Test CAM generation with high risk score."""
        generator = CAMGenerator()
        risk_score = RiskScore(
            overall_score=35.0,
            risk_level="high",
            top_risk_factors=["Negative cash flow", "High debt", "Litigation"],
            top_positive_factors=[],
        )
        loan_rec = LoanRecommendation(
            max_loan_amount=5000000.0,
            recommended_interest_rate=15.0,
            risk_score=risk_score,
            limiting_constraint="High risk profile",
            explanations={},
        )

        cam_doc = generator.generate_cam(
            application_id="app_004",
            company_data=sample_company,
            financial_data=sample_financial_data,
            research_data=sample_research_data,
            loan_recommendation=loan_rec,
            audit_trail=sample_audit_trail,
        )

        assert "HIGH" in cam_doc.sections["executive_summary"]
        assert "35.00" in cam_doc.sections["executive_summary"]
