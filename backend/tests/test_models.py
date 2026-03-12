"""Basic tests for domain models."""

from datetime import datetime
import pytest

from app.models import (
    FinancialData,
    GSTData,
    Transaction,
    Debt,
    Asset,
    Company,
    Promoter,
    NewsArticle,
    MCAData,
    LegalCase,
    SentimentScore,
    CharacterScore,
    CapacityScore,
    CapitalScore,
    CollateralScore,
    ConditionsScore,
    FiveCsScores,
    RiskScore,
    Explanation,
    LoanRecommendation,
    AuditEvent,
    AuditTrail,
    CAMDocument,
    Document,
    LoanApplication,
    CircularTradingAlert,
)


def test_financial_data_creation():
    """Test FinancialData model instantiation."""
    data = FinancialData(
        company_id="C001",
        period="FY2023",
        revenue=10000000.0,
        expenses=8000000.0,
        ebitda=2000000.0,
        net_profit=1500000.0,
        total_assets=50000000.0,
        total_liabilities=30000000.0,
        equity=20000000.0,
        cash_flow=2500000.0,
        confidence_scores={"revenue": 0.95, "expenses": 0.92},
    )
    assert data.company_id == "C001"
    assert data.revenue == 10000000.0
    assert data.confidence_scores["revenue"] == 0.95


def test_gst_data_creation():
    """Test GSTData model instantiation."""
    gst = GSTData(
        gstin="29ABCDE1234F1Z5",
        period="2023-Q1",
        sales=5000000.0,
        purchases=3000000.0,
        tax_paid=500000.0,
        transactions=[{"id": "T001", "amount": 100000.0}],
    )
    assert gst.gstin == "29ABCDE1234F1Z5"
    assert len(gst.transactions) == 1


def test_transaction_creation():
    """Test Transaction model instantiation."""
    txn = Transaction(
        date=datetime(2023, 1, 15),
        description="Payment received",
        debit=0.0,
        credit=50000.0,
        balance=150000.0,
    )
    assert txn.credit == 50000.0
    assert txn.date.year == 2023


def test_company_creation():
    """Test Company model instantiation."""
    promoter = Promoter(
        name="John Doe",
        din="12345678",
        shareholding=51.0,
        role="Managing Director",
    )
    company = Company(
        company_id="C001",
        cin="U12345KA2020PTC123456",
        gstin="29ABCDE1234F1Z5",
        name="Test Company Ltd",
        industry="Manufacturing",
        incorporation_date=datetime(2020, 1, 1),
        promoters=[promoter],
    )
    assert company.name == "Test Company Ltd"
    assert len(company.promoters) == 1
    assert company.promoters[0].name == "John Doe"


def test_news_article_creation():
    """Test NewsArticle model instantiation."""
    article = NewsArticle(
        title="Company expands operations",
        source="Business Times",
        url="https://example.com/article",
        published_date=datetime(2023, 6, 1),
        content="Company announces expansion...",
        sentiment="positive",
    )
    assert article.sentiment == "positive"
    assert article.source == "Business Times"


def test_five_cs_scores_creation():
    """Test FiveCsScores model instantiation."""
    character = CharacterScore(
        score=85.0,
        litigation_count=0,
        governance_rating="Good",
        credit_bureau_score=750.0,
        negative_factors=[],
    )
    capacity = CapacityScore(
        score=75.0,
        dscr=1.5,
        cash_flow=2500000.0,
        debt_service=1666666.67,
        trend="stable",
    )
    capital = CapitalScore(
        score=70.0,
        debt_equity_ratio=1.5,
        net_worth=20000000.0,
        net_worth_trend="improving",
    )
    collateral = CollateralScore(
        score=80.0,
        ltv=0.65,
        collateral_type="Real Estate",
        valuation_date=datetime(2023, 1, 1),
    )
    conditions = ConditionsScore(
        score=65.0,
        sector_risk="Medium",
        regulatory_risk="Low",
        commodity_risk="Medium",
        risk_factors=["Market volatility"],
    )
    
    five_cs = FiveCsScores(
        character=character,
        capacity=capacity,
        capital=capital,
        collateral=collateral,
        conditions=conditions,
    )
    
    assert five_cs.character.score == 85.0
    assert five_cs.capacity.dscr == 1.5
    assert five_cs.capital.debt_equity_ratio == 1.5
    assert five_cs.collateral.ltv == 0.65
    assert five_cs.conditions.score == 65.0


def test_loan_recommendation_creation():
    """Test LoanRecommendation model instantiation."""
    risk_score = RiskScore(
        overall_score=72.0,
        risk_level="low",
        top_risk_factors=["Market volatility"],
        top_positive_factors=["Strong cash flow", "Good governance"],
    )
    
    explanation = Explanation(
        summary="Loan amount limited by collateral value",
        key_factors=[("EBITDA", 0.4), ("Collateral", 0.75)],
        data_sources=["Annual Report 2023", "Valuation Report"],
        reasoning="Collateral value is the limiting constraint",
    )
    
    recommendation = LoanRecommendation(
        max_loan_amount=15000000.0,
        recommended_interest_rate=9.5,
        risk_score=risk_score,
        limiting_constraint="collateral",
        explanations={"loan_amount": explanation},
    )
    
    assert recommendation.max_loan_amount == 15000000.0
    assert recommendation.risk_score.overall_score == 72.0
    assert recommendation.limiting_constraint == "collateral"


def test_cam_document_creation():
    """Test CAMDocument model instantiation."""
    event = AuditEvent(
        timestamp=datetime(2023, 6, 1, 10, 30),
        event_type="data_ingestion",
        description="Uploaded annual report",
        user="credit_officer_1",
        data={"file": "annual_report_2023.pdf"},
    )
    
    audit_trail = AuditTrail(events=[event])
    
    cam = CAMDocument(
        application_id="APP001",
        company_name="Test Company Ltd",
        generated_date=datetime(2023, 6, 1),
        sections={
            "executive_summary": "This is a summary...",
            "company_overview": "Company details...",
        },
        audit_trail=audit_trail,
        version=1,
    )
    
    assert cam.application_id == "APP001"
    assert len(cam.sections) == 2
    assert len(cam.audit_trail.events) == 1


def test_loan_application_creation():
    """Test LoanApplication model instantiation."""
    doc = Document(
        document_id="DOC001",
        document_type="AnnualReport",
        file_path="/uploads/annual_report.pdf",
        upload_date=datetime(2023, 6, 1),
        processed=True,
        confidence_score=0.92,
        extracted_data={"revenue": 10000000.0},
    )
    
    application = LoanApplication(
        application_id="APP001",
        company_id="C001",
        company_name="Test Company Ltd",
        cin="U12345KA2020PTC123456",
        gstin="29ABCDE1234F1Z5",
        loan_amount_requested=20000000.0,
        loan_purpose="Working capital",
        submitted_date=datetime(2023, 6, 1),
        status="processing",
        documents=[doc],
    )
    
    assert application.loan_amount_requested == 20000000.0
    assert len(application.documents) == 1
    assert application.documents[0].confidence_score == 0.92


def test_circular_trading_alert_creation():
    """Test CircularTradingAlert model instantiation."""
    alert = CircularTradingAlert(
        detected=True,
        severity="high",
        discrepancies=["GST sales exceed bank deposits by 40%"],
        gst_sales=10000000.0,
        bank_deposits=6000000.0,
        mismatch_percentage=40.0,
    )
    
    assert alert.detected is True
    assert alert.severity == "high"
    assert alert.mismatch_percentage == 40.0
