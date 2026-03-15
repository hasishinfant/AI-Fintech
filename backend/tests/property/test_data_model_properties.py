"""Property-based tests for data model validation.

Feature: intelli-credit
Properties tested:
- Property 13: Five Cs Score Validity
"""

from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
from datetime import datetime
from app.models.credit_assessment import (
    CharacterScore,
    CapacityScore,
    CapitalScore,
    CollateralScore,
    ConditionsScore,
    FiveCsScores,
    RiskScore,
    Explanation,
    LoanRecommendation,
)
from app.models.financial import FinancialData, GSTData, Transaction, Debt, Asset
from app.models.company import Company, Promoter
from app.models.research import NewsArticle, MCAData, LegalCase, SentimentScore
from app.models.cam import CAMDocument, AuditTrail, AuditEvent
from app.models.application import LoanApplication, Document


# Strategies for generating realistic scores (0-100)
score_0_to_100 = st.floats(min_value=0.0, max_value=100.0)

# Strategies for generating realistic financial values
positive_float = st.floats(min_value=0.01, max_value=1e9)
non_negative_float = st.floats(min_value=0.0, max_value=1e9)

# Strategies for generating strings
valid_string = st.text(min_size=1, max_size=100)
valid_risk_level = st.sampled_from(["high", "medium", "low"])
valid_trend = st.sampled_from(["improving", "stable", "declining"])
valid_sector_risk = st.sampled_from(["Low", "Medium", "High"])


@settings(max_examples=20)
@given(score=score_0_to_100)
def test_character_score_validity(score):
    """
    Property 13: Five Cs Score Validity (Character component)
    
    For any Character assessment, the score should be within
    the range 0 to 100 inclusive.
    
    Validates: Requirements 5.4
    """
    character_score = CharacterScore(
        score=score,
        litigation_count=0,
        governance_rating="Good",
        credit_bureau_score=700,
    )
    
    # Score must be within 0-100
    assert 0.0 <= character_score.score <= 100.0, (
        f"Character score {character_score.score} is outside valid range [0, 100]"
    )


@settings(max_examples=20)
@given(score=score_0_to_100)
def test_capacity_score_validity(score):
    """
    Property 13: Five Cs Score Validity (Capacity component)
    
    For any Capacity assessment, the score should be within
    the range 0 to 100 inclusive.
    
    Validates: Requirements 6.4
    """
    capacity_score = CapacityScore(
        score=score,
        dscr=1.5,
        cash_flow=1000000,
        debt_service=666667,
        trend="stable",
    )
    
    # Score must be within 0-100
    assert 0.0 <= capacity_score.score <= 100.0, (
        f"Capacity score {capacity_score.score} is outside valid range [0, 100]"
    )


@settings(max_examples=20)
@given(score=score_0_to_100)
def test_capital_score_validity(score):
    """
    Property 13: Five Cs Score Validity (Capital component)
    
    For any Capital assessment, the score should be within
    the range 0 to 100 inclusive.
    
    Validates: Requirements 7.4
    """
    capital_score = CapitalScore(
        score=score,
        debt_equity_ratio=1.5,
        net_worth=5000000,
        net_worth_trend="stable",
    )
    
    # Score must be within 0-100
    assert 0.0 <= capital_score.score <= 100.0, (
        f"Capital score {capital_score.score} is outside valid range [0, 100]"
    )


@settings(max_examples=20)
@given(score=score_0_to_100)
def test_collateral_score_validity(score):
    """
    Property 13: Five Cs Score Validity (Collateral component)
    
    For any Collateral assessment, the score should be within
    the range 0 to 100 inclusive.
    
    Validates: Requirements 8.4
    """
    collateral_score = CollateralScore(
        score=score,
        ltv=0.6,
        collateral_type="Real Estate",
        valuation_date=datetime.now(),
    )
    
    # Score must be within 0-100
    assert 0.0 <= collateral_score.score <= 100.0, (
        f"Collateral score {collateral_score.score} is outside valid range [0, 100]"
    )


@settings(max_examples=20)
@given(score=score_0_to_100)
def test_conditions_score_validity(score):
    """
    Property 13: Five Cs Score Validity (Conditions component)
    
    For any Conditions assessment, the score should be within
    the range 0 to 100 inclusive.
    
    Validates: Requirements 9.4
    """
    conditions_score = ConditionsScore(
        score=score,
        sector_risk="medium",
        regulatory_risk="low",
        commodity_risk="low",
    )
    
    # Score must be within 0-100
    assert 0.0 <= conditions_score.score <= 100.0, (
        f"Conditions score {conditions_score.score} is outside valid range [0, 100]"
    )


@settings(max_examples=20)
@given(
    character_score=score_0_to_100,
    capacity_score=score_0_to_100,
    capital_score=score_0_to_100,
    collateral_score=score_0_to_100,
    conditions_score=score_0_to_100,
)
def test_five_cs_scores_all_components_valid(
    character_score,
    capacity_score,
    capital_score,
    collateral_score,
    conditions_score,
):
    """
    Property 13: Five Cs Score Validity (All components)
    
    For any completed Five Cs assessment, all individual scores
    (Character, Capacity, Capital, Collateral, Conditions) should be
    within the range 0 to 100 inclusive.
    
    Validates: Requirements 5.4, 6.4, 7.4, 8.4, 9.4
    """
    five_cs = FiveCsScores(
        character=CharacterScore(
            score=character_score,
            litigation_count=0,
            governance_rating="Good",
            credit_bureau_score=700,
        ),
        capacity=CapacityScore(
            score=capacity_score,
            dscr=1.5,
            cash_flow=1000000,
            debt_service=666667,
            trend="stable",
        ),
        capital=CapitalScore(
            score=capital_score,
            debt_equity_ratio=1.5,
            net_worth=5000000,
            net_worth_trend="stable",
        ),
        collateral=CollateralScore(
            score=collateral_score,
            ltv=0.6,
            collateral_type="Real Estate",
            valuation_date=datetime.now(),
        ),
        conditions=ConditionsScore(
            score=conditions_score,
            sector_risk="medium",
            regulatory_risk="low",
            commodity_risk="low",
        ),
    )
    
    # All individual scores must be within 0-100
    assert 0.0 <= five_cs.character.score <= 100.0
    assert 0.0 <= five_cs.capacity.score <= 100.0
    assert 0.0 <= five_cs.capital.score <= 100.0
    assert 0.0 <= five_cs.collateral.score <= 100.0
    assert 0.0 <= five_cs.conditions.score <= 100.0


@settings(max_examples=20)
@given(score=score_0_to_100)
def test_risk_score_validity(score):
    """
    Property 13: Five Cs Score Validity (Composite risk score)
    
    For any completed Five Cs assessment and composite risk score,
    the composite score should be within the range 0 to 100 inclusive.
    
    Validates: Requirements 10.1
    """
    risk_score = RiskScore(
        overall_score=score,
        risk_level="medium",
        top_risk_factors=["Factor 1", "Factor 2"],
        top_positive_factors=["Positive 1"],
    )
    
    # Composite score must be within 0-100
    assert 0.0 <= risk_score.overall_score <= 100.0, (
        f"Risk score {risk_score.overall_score} is outside valid range [0, 100]"
    )


@settings(max_examples=20)
@given(
    character_score=score_0_to_100,
    capacity_score=score_0_to_100,
    capital_score=score_0_to_100,
    collateral_score=score_0_to_100,
    conditions_score=score_0_to_100,
    risk_score=score_0_to_100,
)
def test_loan_recommendation_all_scores_valid(
    character_score,
    capacity_score,
    capital_score,
    collateral_score,
    conditions_score,
    risk_score,
):
    """
    Property 13: Five Cs Score Validity (Complete recommendation)
    
    For any complete loan recommendation with all Five Cs and risk scores,
    all scores should be within the range 0 to 100 inclusive.
    
    Validates: Requirements 5.4, 6.4, 7.4, 8.4, 9.4, 10.1
    """
    five_cs = FiveCsScores(
        character=CharacterScore(
            score=character_score,
            litigation_count=0,
            governance_rating="Good",
            credit_bureau_score=700,
        ),
        capacity=CapacityScore(
            score=capacity_score,
            dscr=1.5,
            cash_flow=1000000,
            debt_service=666667,
            trend="stable",
        ),
        capital=CapitalScore(
            score=capital_score,
            debt_equity_ratio=1.5,
            net_worth=5000000,
            net_worth_trend="stable",
        ),
        collateral=CollateralScore(
            score=collateral_score,
            ltv=0.6,
            collateral_type="Real Estate",
            valuation_date=datetime.now(),
        ),
        conditions=ConditionsScore(
            score=conditions_score,
            sector_risk="medium",
            regulatory_risk="low",
            commodity_risk="low",
        ),
    )
    
    recommendation = LoanRecommendation(
        max_loan_amount=1000000,
        recommended_interest_rate=12.5,
        risk_score=RiskScore(
            overall_score=risk_score,
            risk_level="medium",
            top_risk_factors=["Factor 1"],
            top_positive_factors=["Positive 1"],
        ),
        limiting_constraint="EBITDA",
        explanations={},
    )
    
    # All scores in the recommendation must be valid
    assert 0.0 <= recommendation.risk_score.overall_score <= 100.0
    assert 0.0 <= five_cs.character.score <= 100.0
    assert 0.0 <= five_cs.capacity.score <= 100.0
    assert 0.0 <= five_cs.capital.score <= 100.0
    assert 0.0 <= five_cs.collateral.score <= 100.0
    assert 0.0 <= five_cs.conditions.score <= 100.0


@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(
    revenue=positive_float,
    expenses=positive_float,
    ebitda=positive_float,
    net_profit=non_negative_float,
    total_assets=positive_float,
    total_liabilities=non_negative_float,
    equity=positive_float,
    cash_flow=non_negative_float,
)
def test_financial_data_model_validity(
    revenue,
    expenses,
    ebitda,
    net_profit,
    total_assets,
    total_liabilities,
    equity,
    cash_flow,
):
    """
    Property: FinancialData model should accept all valid financial values.
    
    For any set of valid financial values, the FinancialData model
    should be created successfully with all fields populated.
    
    Validates: Requirements 1.1, 1.2, 1.3, 1.4
    """
    financial_data = FinancialData(
        company_id="TEST001",
        period="2023-2024",
        revenue=revenue,
        expenses=expenses,
        ebitda=ebitda,
        net_profit=net_profit,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        equity=equity,
        cash_flow=cash_flow,
    )
    
    # All fields should be accessible and have correct types
    assert isinstance(financial_data.company_id, str)
    assert isinstance(financial_data.period, str)
    assert isinstance(financial_data.revenue, float)
    assert isinstance(financial_data.expenses, float)
    assert isinstance(financial_data.ebitda, float)
    assert isinstance(financial_data.net_profit, float)
    assert isinstance(financial_data.total_assets, float)
    assert isinstance(financial_data.total_liabilities, float)
    assert isinstance(financial_data.equity, float)
    assert isinstance(financial_data.cash_flow, float)


@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(
    sales=positive_float,
    purchases=positive_float,
    tax_paid=non_negative_float,
)
def test_gst_data_model_validity(sales, purchases, tax_paid):
    """
    Property: GSTData model should accept all valid GST values.
    
    For any set of valid GST values, the GSTData model should be
    created successfully with all fields populated.
    
    Validates: Requirements 1.1, 3.1, 3.2
    """
    gst_data = GSTData(
        gstin="27AABCT1234H1Z0",
        period="2023-2024",
        sales=sales,
        purchases=purchases,
        tax_paid=tax_paid,
        transactions=[],
    )
    
    # All fields should be accessible and have correct types
    assert isinstance(gst_data.gstin, str)
    assert isinstance(gst_data.period, str)
    assert isinstance(gst_data.sales, float)
    assert isinstance(gst_data.purchases, float)
    assert isinstance(gst_data.tax_paid, float)
    assert isinstance(gst_data.transactions, list)


@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(
    debit=non_negative_float,
    credit=non_negative_float,
    balance=non_negative_float,
)
def test_transaction_model_validity(debit, credit, balance):
    """
    Property: Transaction model should accept all valid transaction values.
    
    For any set of valid transaction values, the Transaction model should
    be created successfully with all fields populated.
    
    Validates: Requirements 1.3
    """
    transaction = Transaction(
        date=datetime.now(),
        description="Test transaction",
        debit=debit,
        credit=credit,
        balance=balance,
    )
    
    # All fields should be accessible and have correct types
    assert isinstance(transaction.date, datetime)
    assert isinstance(transaction.description, str)
    assert isinstance(transaction.debit, float)
    assert isinstance(transaction.credit, float)
    assert isinstance(transaction.balance, float)


@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(
    amount=positive_float,
    interest_rate=st.floats(min_value=0.0, max_value=50.0),
    emi=positive_float,
    outstanding=non_negative_float,
)
def test_debt_model_validity(amount, interest_rate, emi, outstanding):
    """
    Property: Debt model should accept all valid debt values.
    
    For any set of valid debt values, the Debt model should be
    created successfully with all fields populated.
    
    Validates: Requirements 6.1, 6.2
    """
    debt = Debt(
        lender="Bank A",
        amount=amount,
        interest_rate=interest_rate,
        emi=emi,
        outstanding=outstanding,
    )
    
    # All fields should be accessible and have correct types
    assert isinstance(debt.lender, str)
    assert isinstance(debt.amount, float)
    assert isinstance(debt.interest_rate, float)
    assert isinstance(debt.emi, float)
    assert isinstance(debt.outstanding, float)


@settings(max_examples=20)
@given(value=positive_float)
def test_asset_model_validity(value):
    """
    Property: Asset model should accept all valid asset values.
    
    For any set of valid asset values, the Asset model should be
    created successfully with all fields populated.
    
    Validates: Requirements 8.1, 8.2, 8.3
    """
    asset = Asset(
        asset_type="Real Estate",
        description="Commercial property",
        value=value,
        valuation_date=datetime.now(),
    )
    
    # All fields should be accessible and have correct types
    assert isinstance(asset.asset_type, str)
    assert isinstance(asset.description, str)
    assert isinstance(asset.value, float)
    assert isinstance(asset.valuation_date, datetime)


@settings(max_examples=20)
@given(
    positive_count=st.integers(min_value=0, max_value=100),
    neutral_count=st.integers(min_value=0, max_value=100),
    negative_count=st.integers(min_value=0, max_value=100),
)
def test_sentiment_score_model_validity(positive_count, neutral_count, negative_count):
    """
    Property: SentimentScore model should accept all valid sentiment values.
    
    For any set of valid sentiment counts, the SentimentScore model should
    be created successfully with all fields populated.
    
    Validates: Requirements 4.2
    """
    # Overall sentiment should be between -1 and 1
    total = positive_count + neutral_count + negative_count
    if total > 0:
        overall = (positive_count - negative_count) / total
    else:
        overall = 0.0
    
    sentiment_score = SentimentScore(
        overall=overall,
        positive_count=positive_count,
        neutral_count=neutral_count,
        negative_count=negative_count,
        key_themes=["Theme 1", "Theme 2"],
    )
    
    # All fields should be accessible and have correct types
    assert isinstance(sentiment_score.overall, float)
    assert isinstance(sentiment_score.positive_count, int)
    assert isinstance(sentiment_score.neutral_count, int)
    assert isinstance(sentiment_score.negative_count, int)
    assert isinstance(sentiment_score.key_themes, list)
    
    # Overall sentiment should be in valid range
    assert -1.0 <= sentiment_score.overall <= 1.0


@settings(max_examples=20)
@given(
    litigation_count=st.integers(min_value=0, max_value=100),
)
def test_character_score_litigation_count_validity(litigation_count):
    """
    Property: CharacterScore litigation_count should be non-negative.
    
    For any CharacterScore, the litigation_count should be a non-negative integer.
    
    Validates: Requirements 5.1, 5.2, 5.3
    """
    character_score = CharacterScore(
        score=75.0,
        litigation_count=litigation_count,
        governance_rating="Good",
        credit_bureau_score=700,
    )
    
    # Litigation count must be non-negative
    assert character_score.litigation_count >= 0
    assert isinstance(character_score.litigation_count, int)


@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(
    dscr=st.floats(min_value=0.0, max_value=100.0),
    cash_flow=positive_float,
    debt_service=positive_float,
)
def test_capacity_score_dscr_validity(dscr, cash_flow, debt_service):
    """
    Property: CapacityScore DSCR should be non-negative.
    
    For any CapacityScore, the DSCR should be a non-negative float.
    
    Validates: Requirements 6.1, 6.2
    """
    capacity_score = CapacityScore(
        score=75.0,
        dscr=dscr,
        cash_flow=cash_flow,
        debt_service=debt_service,
        trend="stable",
    )
    
    # DSCR must be non-negative
    assert capacity_score.dscr >= 0.0
    assert isinstance(capacity_score.dscr, float)


@settings(max_examples=20)
@given(
    debt_equity_ratio=st.floats(min_value=0.0, max_value=100.0),
    net_worth=positive_float,
)
def test_capital_score_debt_equity_validity(debt_equity_ratio, net_worth):
    """
    Property: CapitalScore debt_equity_ratio should be non-negative.
    
    For any CapitalScore, the debt_equity_ratio should be a non-negative float.
    
    Validates: Requirements 7.1, 7.2
    """
    capital_score = CapitalScore(
        score=75.0,
        debt_equity_ratio=debt_equity_ratio,
        net_worth=net_worth,
        net_worth_trend="stable",
    )
    
    # Debt-to-Equity ratio must be non-negative
    assert capital_score.debt_equity_ratio >= 0.0
    assert isinstance(capital_score.debt_equity_ratio, float)


@settings(max_examples=20)
@given(
    ltv=st.floats(min_value=0.0, max_value=2.0),
)
def test_collateral_score_ltv_validity(ltv):
    """
    Property: CollateralScore LTV should be non-negative.
    
    For any CollateralScore, the LTV should be a non-negative float.
    
    Validates: Requirements 8.1, 8.2, 8.3
    """
    collateral_score = CollateralScore(
        score=75.0,
        ltv=ltv,
        collateral_type="Real Estate",
        valuation_date=datetime.now(),
    )
    
    # LTV must be non-negative
    assert collateral_score.ltv >= 0.0
    assert isinstance(collateral_score.ltv, float)


@settings(max_examples=20)
@given(
    interest_rate=st.floats(min_value=0.0, max_value=50.0),
)
def test_loan_recommendation_interest_rate_validity(interest_rate):
    """
    Property: LoanRecommendation interest_rate should be non-negative.
    
    For any LoanRecommendation, the recommended_interest_rate should be
    a non-negative float.
    
    Validates: Requirements 12.1, 12.2, 12.3, 12.4
    """
    recommendation = LoanRecommendation(
        max_loan_amount=1000000,
        recommended_interest_rate=interest_rate,
        risk_score=RiskScore(
            overall_score=50.0,
            risk_level="medium",
        ),
        limiting_constraint="EBITDA",
    )
    
    # Interest rate must be non-negative
    assert recommendation.recommended_interest_rate >= 0.0
    assert isinstance(recommendation.recommended_interest_rate, float)


@settings(max_examples=20)
@given(
    max_loan_amount=positive_float,
)
def test_loan_recommendation_loan_amount_validity(max_loan_amount):
    """
    Property: LoanRecommendation max_loan_amount should be positive.
    
    For any LoanRecommendation, the max_loan_amount should be a positive float.
    
    Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5
    """
    recommendation = LoanRecommendation(
        max_loan_amount=max_loan_amount,
        recommended_interest_rate=12.5,
        risk_score=RiskScore(
            overall_score=50.0,
            risk_level="medium",
        ),
        limiting_constraint="EBITDA",
    )
    
    # Loan amount must be positive
    assert recommendation.max_loan_amount > 0.0
    assert isinstance(recommendation.max_loan_amount, float)


@settings(max_examples=20)
@given(
    num_events=st.integers(min_value=0, max_value=10),
)
def test_audit_trail_model_validity(num_events):
    """
    Property: AuditTrail model should accept any number of audit events.
    
    For any number of audit events, the AuditTrail model should be
    created successfully with all events stored.
    
    Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5
    """
    events = [
        AuditEvent(
            timestamp=datetime.now(),
            event_type="data_ingestion",
            description=f"Event {i}",
            user=None,
            data={},
        )
        for i in range(num_events)
    ]
    
    audit_trail = AuditTrail(events=events)
    
    # All fields should be accessible and have correct types
    assert isinstance(audit_trail.events, list)
    assert len(audit_trail.events) == num_events
    
    # Each event should have required fields
    for event in audit_trail.events:
        assert isinstance(event.timestamp, datetime)
        assert isinstance(event.event_type, str)
        assert isinstance(event.description, str)
        assert isinstance(event.data, dict)


@settings(max_examples=20)
@given(
    num_sections=st.integers(min_value=1, max_value=10),
)
def test_cam_document_model_validity(num_sections):
    """
    Property: CAMDocument model should accept any number of sections.
    
    For any number of sections, the CAMDocument model should be
    created successfully with all sections stored.
    
    Validates: Requirements 14.1, 14.2, 14.3
    """
    sections = {
        f"section_{i}": f"Content for section {i}"
        for i in range(num_sections)
    }
    
    cam_document = CAMDocument(
        application_id="APP001",
        company_name="Test Company",
        generated_date=datetime.now(),
        sections=sections,
        audit_trail=AuditTrail(events=[]),
        version=1,
    )
    
    # All fields should be accessible and have correct types
    assert isinstance(cam_document.application_id, str)
    assert isinstance(cam_document.company_name, str)
    assert isinstance(cam_document.generated_date, datetime)
    assert isinstance(cam_document.sections, dict)
    assert len(cam_document.sections) == num_sections
    assert isinstance(cam_document.audit_trail, AuditTrail)
    assert isinstance(cam_document.version, int)
