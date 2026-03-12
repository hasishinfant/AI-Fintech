"""Property-based tests for CAM Generator service.

Feature: intelli-credit
"""

from datetime import datetime, timedelta
from typing import Dict, Any

import pytest
from hypothesis import given, strategies as st, settings

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


# Strategies for generating test data
@st.composite
def companies(draw):
    """Generate valid company data."""
    name = draw(st.text(min_size=5, max_size=100))
    cin = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=21, max_size=21))
    gstin = draw(st.text(alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=15, max_size=15))
    industry = draw(st.sampled_from([
        "Manufacturing", "Services", "IT", "Finance", "Healthcare",
        "Retail", "Logistics", "Energy", "Telecom", "Real Estate"
    ]))
    
    num_promoters = draw(st.integers(min_value=0, max_value=3))
    promoters = []
    for i in range(num_promoters):
        promoters.append(Promoter(
            name=f"Promoter {i+1}",
            din=f"{i:08d}",
            shareholding=100.0 / max(1, num_promoters),
            role="Director" if i > 0 else "Managing Director"
        ))
    
    return Company(
        company_id=f"comp_{draw(st.integers(min_value=1, max_value=10000))}",
        cin=cin,
        gstin=gstin,
        name=name,
        industry=industry,
        incorporation_date=datetime.now() - timedelta(days=draw(st.integers(min_value=365, max_value=7300))),
        promoters=promoters,
    )


@st.composite
def financial_data_objects(draw):
    """Generate valid financial data."""
    revenue = draw(st.floats(min_value=1000000, max_value=1000000000))
    expenses = draw(st.floats(min_value=revenue * 0.5, max_value=revenue * 0.95))
    ebitda = revenue - expenses
    net_profit = draw(st.floats(min_value=ebitda * 0.3, max_value=ebitda * 0.8))
    total_assets = draw(st.floats(min_value=revenue, max_value=revenue * 5))
    total_liabilities = draw(st.floats(min_value=total_assets * 0.2, max_value=total_assets * 0.7))
    equity = total_assets - total_liabilities
    cash_flow = draw(st.floats(min_value=net_profit * 0.5, max_value=net_profit * 1.5))
    
    return FinancialData(
        company_id="comp_001",
        period=f"FY {draw(st.integers(min_value=2020, max_value=2024))}-{draw(st.integers(min_value=2021, max_value=2025))}",
        revenue=revenue,
        expenses=expenses,
        ebitda=ebitda,
        net_profit=net_profit,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        equity=equity,
        cash_flow=cash_flow,
        confidence_scores={"revenue": 0.95, "expenses": 0.92},
    )


@st.composite
def risk_scores(draw):
    """Generate valid risk scores."""
    overall_score = draw(st.floats(min_value=0, max_value=100))
    risk_level = draw(st.sampled_from(["low", "medium", "high"]))
    
    return RiskScore(
        overall_score=overall_score,
        risk_level=risk_level,
        top_risk_factors=draw(st.lists(
            st.text(min_size=5, max_size=50),
            min_size=0,
            max_size=5
        )),
        top_positive_factors=draw(st.lists(
            st.text(min_size=5, max_size=50),
            min_size=0,
            max_size=5
        )),
    )


@st.composite
def loan_recommendations(draw):
    """Generate valid loan recommendations."""
    risk_score = draw(risk_scores())
    max_loan = draw(st.floats(min_value=100000, max_value=100000000))
    interest_rate = draw(st.floats(min_value=5, max_value=20))
    
    return LoanRecommendation(
        max_loan_amount=max_loan,
        recommended_interest_rate=interest_rate,
        risk_score=risk_score,
        limiting_constraint=draw(st.sampled_from([
            "EBITDA-based calculation",
            "Collateral cap",
            "DSCR reduction",
            "Conservative approach"
        ])),
        explanations={
            "character": Explanation(
                summary=draw(st.text(min_size=10, max_size=100)),
                key_factors=[(f"Factor {i}", draw(st.floats(min_value=0, max_value=1))) for i in range(3)],
                data_sources=["Source 1", "Source 2"],
                reasoning=draw(st.text(min_size=10, max_size=100)),
            ),
            "capacity": Explanation(
                summary=draw(st.text(min_size=10, max_size=100)),
                key_factors=[(f"Factor {i}", draw(st.floats(min_value=0, max_value=1))) for i in range(3)],
                data_sources=["Source 1"],
                reasoning=draw(st.text(min_size=10, max_size=100)),
            ),
            "capital": Explanation(
                summary=draw(st.text(min_size=10, max_size=100)),
                key_factors=[(f"Factor {i}", draw(st.floats(min_value=0, max_value=1))) for i in range(2)],
                data_sources=["Source 1"],
                reasoning=draw(st.text(min_size=10, max_size=100)),
            ),
            "collateral": Explanation(
                summary=draw(st.text(min_size=10, max_size=100)),
                key_factors=[(f"Factor {i}", draw(st.floats(min_value=0, max_value=1))) for i in range(2)],
                data_sources=["Source 1"],
                reasoning=draw(st.text(min_size=10, max_size=100)),
            ),
            "conditions": Explanation(
                summary=draw(st.text(min_size=10, max_size=100)),
                key_factors=[(f"Factor {i}", draw(st.floats(min_value=0, max_value=1))) for i in range(2)],
                data_sources=["Source 1"],
                reasoning=draw(st.text(min_size=10, max_size=100)),
            ),
        },
    )


@st.composite
def audit_trails(draw):
    """Generate valid audit trails."""
    num_events = draw(st.integers(min_value=1, max_value=10))
    events = []
    now = datetime.now()
    
    for i in range(num_events):
        events.append(AuditEvent(
            timestamp=now - timedelta(hours=i),
            event_type=draw(st.sampled_from(["data_ingestion", "research_activity", "calculation"])),
            description=draw(st.text(min_size=10, max_size=100)),
            user=draw(st.one_of(st.none(), st.text(min_size=5, max_size=20))),
            data={},
        ))
    
    return AuditTrail(events=events)


@st.composite
def research_data_objects(draw):
    """Generate valid research data."""
    return {
        "mca_data": MCAData(
            cin="U12345AB2020PTC123456",
            company_name="Test Company",
            registration_date=datetime.now() - timedelta(days=1000),
            authorized_capital=draw(st.floats(min_value=1000000, max_value=100000000)),
            paid_up_capital=draw(st.floats(min_value=500000, max_value=50000000)),
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status=draw(st.sampled_from(["Compliant", "Non-compliant", "Pending"])),
            directors=[],
        ),
        "industry_data": {
            "name": draw(st.text(min_size=5, max_size=50)),
            "market_size": draw(st.text(min_size=5, max_size=50)),
            "growth_rate": draw(st.text(min_size=3, max_size=10)),
        },
        "sentiment": {
            "overall": draw(st.sampled_from(["Positive", "Neutral", "Negative"])),
            "positive_count": draw(st.integers(min_value=0, max_value=10)),
            "negative_count": draw(st.integers(min_value=0, max_value=10)),
        },
        "conditions_score": {
            "sector_risk": draw(st.sampled_from(["Low", "Medium", "High"])),
            "regulatory_risk": draw(st.sampled_from(["Low", "Medium", "High"])),
            "commodity_risk": draw(st.sampled_from(["Low", "Medium", "High"])),
        },
        "ratios": {
            "DSCR": draw(st.floats(min_value=0.5, max_value=3.0)),
            "Debt/Equity": draw(st.floats(min_value=0.1, max_value=5.0)),
            "LTV": draw(st.floats(min_value=0.1, max_value=1.0)),
        },
    }


class TestCAMGeneratorProperties:
    """Property-based tests for CAM Generator."""

    # Feature: intelli-credit, Property 35: CAM Section Completeness
    @settings(max_examples=50)
    @given(
        company=companies(),
        financial_data=financial_data_objects(),
        research_data=research_data_objects(),
        loan_recommendation=loan_recommendations(),
        audit_trail=audit_trails(),
    )
    def test_cam_section_completeness(
        self,
        company,
        financial_data,
        research_data,
        loan_recommendation,
        audit_trail,
    ):
        """For any generated CAM document, it should contain all eight required sections:
        Executive Summary, Company Overview, Industry Analysis, Financial Analysis,
        Risk Assessment, Five Cs Summary, Final Recommendation, and Explainability Notes.
        
        **Validates: Requirements 14.1, 14.2**
        """
        generator = CAMGenerator()
        
        cam_doc = generator.generate_cam(
            application_id="APP-001",
            company_data=company,
            financial_data=financial_data,
            research_data=research_data,
            loan_recommendation=loan_recommendation,
            audit_trail=audit_trail,
        )
        
        # Verify CAM document is created
        assert isinstance(cam_doc, CAMDocument)
        
        # Verify all required sections are present
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
            assert section in cam_doc.sections, f"Missing required section: {section}"
            assert isinstance(cam_doc.sections[section], str), \
                f"Section {section} is not a string"
            assert len(cam_doc.sections[section]) > 0, \
                f"Section {section} is empty"

    @settings(max_examples=50)
    @given(
        company=companies(),
        financial_data=financial_data_objects(),
        research_data=research_data_objects(),
        loan_recommendation=loan_recommendations(),
        audit_trail=audit_trails(),
    )
    def test_cam_sections_contain_key_content(
        self,
        company,
        financial_data,
        research_data,
        loan_recommendation,
        audit_trail,
    ):
        """For any generated CAM document, each section should contain relevant content."""
        generator = CAMGenerator()
        
        cam_doc = generator.generate_cam(
            application_id="APP-001",
            company_data=company,
            financial_data=financial_data,
            research_data=research_data,
            loan_recommendation=loan_recommendation,
            audit_trail=audit_trail,
        )
        
        # Executive summary should contain risk level and loan amount
        exec_summary = cam_doc.sections["executive_summary"]
        assert "Risk Assessment:" in exec_summary or "RISK" in exec_summary.upper()
        assert "Loan" in exec_summary or "loan" in exec_summary.lower()
        
        # Company overview should contain company name
        company_overview = cam_doc.sections["company_overview"]
        assert company.name in company_overview or "Company" in company_overview
        
        # Financial analysis should contain financial metrics
        financial_analysis = cam_doc.sections["financial_analysis"]
        assert "Revenue" in financial_analysis or "EBITDA" in financial_analysis or "Assets" in financial_analysis
        
        # Risk assessment should contain risk score
        risk_assessment = cam_doc.sections["risk_assessment"]
        assert "Risk" in risk_assessment or "Score" in risk_assessment
        
        # Five Cs summary should contain Five Cs
        five_cs_summary = cam_doc.sections["five_cs_summary"]
        assert "CHARACTER" in five_cs_summary or "CAPACITY" in five_cs_summary or "CAPITAL" in five_cs_summary
        
        # Final recommendation should contain recommendation
        final_recommendation = cam_doc.sections["final_recommendation"]
        assert "Recommendation" in final_recommendation or "recommendation" in final_recommendation.lower()
        
        # Explainability notes should contain explanations
        explainability_notes = cam_doc.sections["explainability_notes"]
        assert "Explanation" in explainability_notes or "explanation" in explainability_notes.lower()
        
        # Audit trail should contain events
        audit_trail_section = cam_doc.sections["audit_trail"]
        assert "Audit" in audit_trail_section or "AUDIT" in audit_trail_section or "Events" in audit_trail_section

    @settings(max_examples=30)
    @given(
        company=companies(),
        financial_data=financial_data_objects(),
        research_data=research_data_objects(),
        loan_recommendation=loan_recommendations(),
        audit_trail=audit_trails(),
    )
    def test_cam_document_metadata_preserved(
        self,
        company,
        financial_data,
        research_data,
        loan_recommendation,
        audit_trail,
    ):
        """For any generated CAM document, metadata should be preserved."""
        generator = CAMGenerator()
        
        application_id = "APP-TEST-001"
        cam_doc = generator.generate_cam(
            application_id=application_id,
            company_data=company,
            financial_data=financial_data,
            research_data=research_data,
            loan_recommendation=loan_recommendation,
            audit_trail=audit_trail,
        )
        
        # Verify metadata
        assert cam_doc.application_id == application_id
        assert cam_doc.company_name == company.name
        assert isinstance(cam_doc.generated_date, datetime)
        assert cam_doc.audit_trail == audit_trail
        assert cam_doc.version >= 1

    @settings(max_examples=30)
    @given(
        company=companies(),
        financial_data=financial_data_objects(),
        research_data=research_data_objects(),
        loan_recommendation=loan_recommendations(),
        audit_trail=audit_trails(),
    )
    def test_cam_sections_are_non_empty_strings(
        self,
        company,
        financial_data,
        research_data,
        loan_recommendation,
        audit_trail,
    ):
        """For any generated CAM document, all sections should be non-empty strings."""
        generator = CAMGenerator()
        
        cam_doc = generator.generate_cam(
            application_id="APP-001",
            company_data=company,
            financial_data=financial_data,
            research_data=research_data,
            loan_recommendation=loan_recommendation,
            audit_trail=audit_trail,
        )
        
        # Verify all sections are non-empty strings
        for section_name, section_content in cam_doc.sections.items():
            assert isinstance(section_content, str), \
                f"Section {section_name} is not a string, got {type(section_content)}"
            assert len(section_content) > 0, \
                f"Section {section_name} is empty"
            # Sections should have reasonable length (at least 20 characters)
            assert len(section_content) >= 20, \
                f"Section {section_name} is too short: {len(section_content)} chars"
