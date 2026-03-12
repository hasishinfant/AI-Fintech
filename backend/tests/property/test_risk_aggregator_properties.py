"""Property-based tests for RiskAggregator.

Feature: intelli-credit
Properties tested:
- Property 24: Weighted Risk Score Calculation
"""

from hypothesis import given, strategies as st, assume, settings, HealthCheck
import pytest
from datetime import datetime
from app.services.credit_engine import RiskAggregator
from app.models.credit_assessment import (
    CharacterScore,
    CapacityScore,
    CapitalScore,
    CollateralScore,
    ConditionsScore,
    FiveCsScores,
)


# Strategies for generating realistic scores (0-100)
score_0_to_100 = st.floats(min_value=0.0, max_value=100.0)

# Strategy for generating valid weight distributions
def weight_distribution():
    """Generate a valid weight distribution that sums to 1.0."""
    # Generate 5 random weights and normalize them
    weights = st.lists(
        st.floats(min_value=0.01, max_value=1.0),
        min_size=5,
        max_size=5,
    )
    
    def normalize_weights(w):
        total = sum(w)
        return {
            'character': w[0] / total,
            'capacity': w[1] / total,
            'capital': w[2] / total,
            'collateral': w[3] / total,
            'conditions': w[4] / total,
        }
    
    return weights.map(normalize_weights)


@settings(max_examples=10, suppress_health_check=[HealthCheck.data_too_large])
@given(
    character_score=score_0_to_100,
    capacity_score=score_0_to_100,
    capital_score=score_0_to_100,
    collateral_score=score_0_to_100,
    conditions_score=score_0_to_100,
    weights=weight_distribution(),
)
def test_weighted_risk_score_calculation(
    character_score,
    capacity_score,
    capital_score,
    collateral_score,
    conditions_score,
    weights,
):
    """
    Property 24: Weighted Risk Score Calculation
    
    For any completed Five Cs assessment with configured weights,
    the composite risk score should be calculated as the weighted sum
    of the five individual scores.
    
    Validates: Requirements 10.2
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
    
    aggregator = RiskAggregator()
    risk_score = aggregator.calculate_composite_risk_score(five_cs, weights)
    
    # Calculate expected score manually
    expected_score = (
        character_score * weights['character'] +
        capacity_score * weights['capacity'] +
        capital_score * weights['capital'] +
        collateral_score * weights['collateral'] +
        conditions_score * weights['conditions']
    )
    
    # The result should match the expected weighted sum (within floating point precision)
    assert abs(risk_score.overall_score - expected_score) < 0.01, (
        f"Expected {expected_score}, got {risk_score.overall_score}"
    )


@settings(max_examples=15)
@given(
    character_score=score_0_to_100,
    capacity_score=score_0_to_100,
    capital_score=score_0_to_100,
    collateral_score=score_0_to_100,
    conditions_score=score_0_to_100,
)
def test_composite_score_always_in_valid_range(
    character_score,
    capacity_score,
    capital_score,
    collateral_score,
    conditions_score,
):
    """
    Property 13: Five Cs Score Validity (Composite Score)
    
    For any completed Five Cs assessment and composite risk score,
    the composite score should be within the range 0 to 100 inclusive.
    
    Validates: Requirements 10.1
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
    
    # Use default weights
    weights = {
        'character': 0.25,
        'capacity': 0.25,
        'capital': 0.20,
        'collateral': 0.20,
        'conditions': 0.10,
    }
    
    aggregator = RiskAggregator()
    risk_score = aggregator.calculate_composite_risk_score(five_cs, weights)
    
    # Composite score must be in valid range
    assert 0.0 <= risk_score.overall_score <= 100.0, (
        f"Score {risk_score.overall_score} is outside valid range [0, 100]"
    )


@settings(max_examples=15)
@given(risk_score=score_0_to_100)
def test_risk_level_classification_valid(risk_score):
    """
    Property 25: Risk Level Classification Validity
    
    For any risk score in the valid range (0-100), the classification
    should return exactly one of: "high", "medium", or "low".
    
    Validates: Requirements 10.3, 10.4, 10.5
    """
    aggregator = RiskAggregator()
    risk_level = aggregator.classify_risk_level(risk_score)
    
    # Must be one of the three valid classifications
    assert risk_level in ["high", "medium", "low"], (
        f"Invalid risk level: {risk_level}"
    )


@settings(max_examples=15)
@given(risk_score=score_0_to_100)
def test_risk_level_classification_consistency(risk_score):
    """
    Property 26: Risk Level Classification Consistency
    
    For any risk score, calling classify_risk_level multiple times
    should always return the same classification.
    
    Validates: Requirements 10.3, 10.4, 10.5
    """
    aggregator = RiskAggregator()
    
    # Call multiple times
    result1 = aggregator.classify_risk_level(risk_score)
    result2 = aggregator.classify_risk_level(risk_score)
    result3 = aggregator.classify_risk_level(risk_score)
    
    # All results should be identical
    assert result1 == result2 == result3, (
        f"Inconsistent classifications: {result1}, {result2}, {result3}"
    )


@settings(max_examples=15)
@given(risk_score=score_0_to_100)
def test_risk_level_classification_thresholds(risk_score):
    """
    Property 27: Risk Level Classification Thresholds
    
    For any risk score, the classification should follow the correct thresholds:
    - score < 40: "high"
    - 40 <= score <= 70: "medium"
    - score > 70: "low"
    
    Validates: Requirements 10.3, 10.4, 10.5
    """
    aggregator = RiskAggregator()
    risk_level = aggregator.classify_risk_level(risk_score)
    
    if risk_score < 40:
        assert risk_level == "high", (
            f"Score {risk_score} should be 'high' but got '{risk_level}'"
        )
    elif risk_score <= 70:
        assert risk_level == "medium", (
            f"Score {risk_score} should be 'medium' but got '{risk_level}'"
        )
    else:
        assert risk_level == "low", (
            f"Score {risk_score} should be 'low' but got '{risk_level}'"
        )


@settings(max_examples=15)
@given(
    character_score=score_0_to_100,
    capacity_score=score_0_to_100,
    capital_score=score_0_to_100,
    collateral_score=score_0_to_100,
    conditions_score=score_0_to_100,
)
def test_risk_score_result_has_required_fields(
    character_score,
    capacity_score,
    capital_score,
    collateral_score,
    conditions_score,
):
    """
    Property 28: Risk Score Result Completeness
    
    For any Five Cs assessment, the returned RiskScore should contain
    all required fields: overall_score, risk_level, top_risk_factors,
    and top_positive_factors.
    
    Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
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
    
    weights = {
        'character': 0.25,
        'capacity': 0.25,
        'capital': 0.20,
        'collateral': 0.20,
        'conditions': 0.10,
    }
    
    aggregator = RiskAggregator()
    risk_score = aggregator.calculate_composite_risk_score(five_cs, weights)
    
    # Check all required fields exist
    assert hasattr(risk_score, 'overall_score')
    assert hasattr(risk_score, 'risk_level')
    assert hasattr(risk_score, 'top_risk_factors')
    assert hasattr(risk_score, 'top_positive_factors')
    
    # Check field types
    assert isinstance(risk_score.overall_score, float)
    assert isinstance(risk_score.risk_level, str)
    assert isinstance(risk_score.top_risk_factors, list)
    assert isinstance(risk_score.top_positive_factors, list)
