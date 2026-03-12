"""Property-based tests for Character analysis.

Feature: intelli-credit
Properties tested:
- Property 14: Character Assessment Data Sources
"""

from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
from datetime import datetime, timedelta
from app.services.credit_engine import FiveCsAnalyzer
from app.models.research import LegalCase, MCAData, SentimentScore, RBINotification
from app.models.credit_assessment import CharacterScore


# Strategies for generating realistic data
credit_bureau_scores = st.floats(min_value=300.0, max_value=900.0)
litigation_counts = st.integers(min_value=0, max_value=10)
compliance_statuses = st.sampled_from(["compliant", "partially_compliant", "non-compliant"])
governance_ratings = st.sampled_from(["Good", "Fair", "Poor"])


def generate_legal_case(case_number: str, case_type: str) -> LegalCase:
    """Helper to generate a legal case."""
    return LegalCase(
        case_number=case_number,
        court="High Court",
        filing_date=datetime.now() - timedelta(days=365),
        case_type=case_type,
        status="pending",
        summary=f"Test {case_type} case",
        parties=["Test Company", "Plaintiff"],
    )


def generate_mca_data(
    compliance_status: str = "compliant",
    days_since_filing: int = 30,
    has_directors: bool = True,
) -> MCAData:
    """Helper to generate MCA data."""
    return MCAData(
        cin="U12345AB2020PTC123456",
        company_name="Test Company",
        registration_date=datetime(2020, 1, 1),
        authorized_capital=1000000.0,
        paid_up_capital=500000.0,
        last_filing_date=datetime.now() - timedelta(days=days_since_filing),
        compliance_status=compliance_status,
        directors=[{"name": "John Doe", "din": "12345678"}] if has_directors else [],
    )


@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(
    credit_bureau_score=credit_bureau_scores,
    litigation_count=litigation_counts,
    compliance_status=compliance_statuses,
)
def test_character_assessment_data_sources(
    credit_bureau_score, litigation_count, compliance_status
):
    """
    Property 14: Character Assessment Data Sources
    
    For any Character assessment, the Credit_Engine should check litigation history,
    governance records, and credit bureau data.
    
    Validates: Requirements 5.1, 5.2, 5.3
    """
    promoter_data = {"name": "John Doe", "din": "12345678"}
    
    # Generate legal cases based on litigation_count
    legal_cases = [
        generate_legal_case(f"CASE{i:03d}", "civil dispute")
        for i in range(litigation_count)
    ]
    
    # Generate MCA data with specified compliance status
    mca_data = generate_mca_data(compliance_status=compliance_status)
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, credit_bureau_score
    )
    
    # Verify result is a CharacterScore
    assert isinstance(result, CharacterScore)
    
    # Verify all data sources are checked:
    # 1. Litigation history is checked (litigation_count should match)
    assert result.litigation_count == litigation_count
    
    # 2. Governance records are checked (governance_rating should be set)
    assert result.governance_rating in ["Good", "Fair", "Poor"]
    
    # 3. Credit bureau data is checked (credit_bureau_score should be stored)
    assert result.credit_bureau_score == credit_bureau_score
    
    # Verify score is within valid range
    assert 0 <= result.score <= 100


@settings(max_examples=20)
@given(
    credit_bureau_score=credit_bureau_scores,
)
def test_character_score_validity_range(credit_bureau_score):
    """
    Property 13: Five Cs Score Validity (Character component)
    
    For any completed Character assessment, the score should be within
    the range 0 to 100 inclusive.
    
    Validates: Requirements 5.4
    """
    promoter_data = {"name": "John Doe", "din": "12345678"}
    legal_cases = []
    mca_data = generate_mca_data()
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, credit_bureau_score
    )
    
    # Score must be within 0-100
    assert 0 <= result.score <= 100


@settings(max_examples=20)
@given(
    litigation_count=litigation_counts,
)
def test_character_score_decreases_with_litigation(litigation_count):
    """
    Property: Character score should decrease as litigation count increases.
    
    For any two scenarios where litigation_count1 > litigation_count2,
    the character score for scenario 1 should be less than or equal to scenario 2.
    
    Validates: Requirements 5.1, 5.4
    """
    promoter_data = {"name": "John Doe", "din": "12345678"}
    mca_data = generate_mca_data()
    credit_bureau_score = 750.0
    
    # Scenario 1: More litigation
    legal_cases_1 = [
        generate_legal_case(f"CASE{i:03d}", "fraud")
        for i in range(max(1, litigation_count))
    ]
    
    # Scenario 2: Less litigation
    legal_cases_2 = [
        generate_legal_case(f"CASE{i:03d}", "fraud")
        for i in range(max(0, litigation_count - 1))
    ]
    
    analyzer = FiveCsAnalyzer()
    result_1 = analyzer.analyze_character(
        promoter_data, legal_cases_1, mca_data, credit_bureau_score
    )
    result_2 = analyzer.analyze_character(
        promoter_data, legal_cases_2, mca_data, credit_bureau_score
    )
    
    # More litigation should result in lower or equal score
    assert result_1.score <= result_2.score


@settings(max_examples=20)
@given(
    credit_bureau_score=credit_bureau_scores,
)
def test_character_score_increases_with_credit_bureau_score(credit_bureau_score):
    """
    Property: Character score should increase with credit bureau score.
    
    For any two scenarios where credit_bureau_score1 > credit_bureau_score2,
    the character score for scenario 1 should be greater than or equal to scenario 2.
    
    Validates: Requirements 5.3, 5.4
    """
    promoter_data = {"name": "John Doe", "din": "12345678"}
    legal_cases = []
    mca_data = generate_mca_data()
    
    # Scenario 1: Higher credit bureau score
    higher_score = min(900.0, credit_bureau_score + 50)
    
    # Scenario 2: Lower credit bureau score
    lower_score = max(300.0, credit_bureau_score - 50)
    
    analyzer = FiveCsAnalyzer()
    result_1 = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, higher_score
    )
    result_2 = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, lower_score
    )
    
    # Higher credit bureau score should result in higher or equal character score
    assert result_1.score >= result_2.score


@settings(max_examples=20)
@given(
    compliance_status=compliance_statuses,
)
def test_character_governance_rating_reflects_compliance(compliance_status):
    """
    Property: Character governance rating should reflect MCA compliance status.
    
    For any MCA compliance status, the governance rating should be set appropriately.
    
    Validates: Requirements 5.2, 5.4
    """
    promoter_data = {"name": "John Doe", "din": "12345678"}
    legal_cases = []
    mca_data = generate_mca_data(compliance_status=compliance_status)
    credit_bureau_score = 750.0
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, credit_bureau_score
    )
    
    # Governance rating should be set
    assert result.governance_rating in ["Good", "Fair", "Poor"]
    
    # Governance rating should reflect compliance status
    if compliance_status == "compliant":
        assert result.governance_rating == "Good"
    elif compliance_status == "partially_compliant":
        assert result.governance_rating == "Fair"
    elif compliance_status == "non-compliant":
        assert result.governance_rating == "Poor"


@settings(max_examples=20)
@given(
    litigation_count=litigation_counts,
)
def test_character_negative_factors_documented(litigation_count):
    """
    Property: Character assessment should document negative factors.
    
    For any Character assessment with negative indicators, the negative_factors
    list should contain descriptions of those indicators.
    
    Validates: Requirements 5.5
    """
    promoter_data = {"name": "John Doe", "din": "12345678"}
    
    # Generate legal cases
    legal_cases = [
        generate_legal_case(f"CASE{i:03d}", "fraud" if i % 2 == 0 else "civil dispute")
        for i in range(litigation_count)
    ]
    
    # Generate MCA data with non-compliance
    mca_data = generate_mca_data(
        compliance_status="non-compliant",
        days_since_filing=400,
        has_directors=False,
    )
    
    # Use low credit bureau score
    credit_bureau_score = 600.0
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, credit_bureau_score
    )
    
    # If there are negative indicators, they should be documented
    if litigation_count > 0 or credit_bureau_score < 650:
        assert len(result.negative_factors) > 0
        
        # Verify negative factors are strings
        for factor in result.negative_factors:
            assert isinstance(factor, str)
            assert len(factor) > 0


@settings(max_examples=20)
@given(
    credit_bureau_score=credit_bureau_scores,
)
def test_character_clean_record_high_score(credit_bureau_score):
    """
    Property: Character score should be high for clean records.
    
    For any Character assessment with no litigation, compliant governance,
    and good credit bureau score, the character score should be high (>= 80).
    
    Validates: Requirements 5.4
    """
    # Only test with good credit bureau scores
    if credit_bureau_score < 700:
        return
    
    promoter_data = {"name": "John Doe", "din": "12345678"}
    legal_cases = []  # No litigation
    mca_data = generate_mca_data(
        compliance_status="compliant",
        days_since_filing=30,
        has_directors=True,
    )
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, credit_bureau_score
    )
    
    # Clean record should have high score
    assert result.score >= 80


@settings(max_examples=20)
@given(
    litigation_count=st.integers(min_value=5, max_value=10),
)
def test_character_poor_record_low_score(litigation_count):
    """
    Property: Character score should be low for poor records.
    
    For any Character assessment with significant litigation, non-compliant governance,
    and low credit bureau score, the character score should be low (< 40).
    
    Validates: Requirements 5.4
    """
    promoter_data = {"name": "John Doe", "din": "12345678"}
    
    # Generate multiple high-severity cases
    legal_cases = [
        generate_legal_case(f"CASE{i:03d}", "fraud")
        for i in range(litigation_count)
    ]
    
    # Generate MCA data with non-compliance
    mca_data = generate_mca_data(
        compliance_status="non-compliant",
        days_since_filing=500,
        has_directors=False,
    )
    
    # Use low credit bureau score
    credit_bureau_score = 350.0
    
    analyzer = FiveCsAnalyzer()
    result = analyzer.analyze_character(
        promoter_data, legal_cases, mca_data, credit_bureau_score
    )
    
    # Poor record should have low score
    assert result.score < 40
