"""Property-based tests for LoanCalculator class."""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from app.services.credit_engine import LoanCalculator


# Feature: intelli-credit, Property 25: Maximum Loan Amount Calculation
@settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
@given(
    ebitda=st.floats(min_value=0.01, max_value=1e8),
    collateral_value=st.floats(min_value=0.01, max_value=1e8),
    dscr=st.floats(min_value=0.01, max_value=5.0),
)
def test_maximum_loan_amount_calculation(ebitda, collateral_value, dscr):
    """For any financial data with EBITDA value, the initial maximum loan amount
    should be calculated as 0.4 multiplied by EBITDA.
    
    **Validates: Requirements 11.1**
    """
    calculator = LoanCalculator()
    
    max_amount, breakdown = calculator.calculate_max_loan_amount(
        ebitda=ebitda,
        collateral_value=collateral_value,
        dscr=dscr,
    )
    
    # EBITDA-based amount should be exactly 0.4 × EBITDA
    expected_ebitda_based = ebitda * 0.4
    assert abs(breakdown.ebitda_based_amount - expected_ebitda_based) < 0.01


# Feature: intelli-credit, Property 26: Collateral-Based Loan Cap
@settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
@given(
    ebitda=st.floats(min_value=0.01, max_value=1e8),
    collateral_value=st.floats(min_value=0.01, max_value=1e8),
    dscr=st.floats(min_value=1.25, max_value=5.0),  # DSCR >= 1.25 to avoid reduction
)
def test_collateral_based_loan_cap(ebitda, collateral_value, dscr):
    """For any loan calculation where collateral value is lower than the EBITDA-based
    loan amount, the recommended loan amount should be capped at 75% of collateral value.
    
    **Validates: Requirements 11.2**
    """
    calculator = LoanCalculator()
    
    max_amount, breakdown = calculator.calculate_max_loan_amount(
        ebitda=ebitda,
        collateral_value=collateral_value,
        dscr=dscr,
    )
    
    # Collateral cap should be exactly 75% of collateral value
    expected_collateral_cap = collateral_value * 0.75
    assert abs(breakdown.collateral_based_cap - expected_collateral_cap) < 0.01
    
    # Final amount should never exceed collateral cap
    assert max_amount <= expected_collateral_cap + 0.01


# Feature: intelli-credit, Property 27: DSCR-Based Loan Reduction
@settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
@given(
    ebitda=st.floats(min_value=0.01, max_value=1e8),
    collateral_value=st.floats(min_value=0.01, max_value=1e8),
    dscr=st.floats(min_value=0.01, max_value=1.25),  # DSCR < 1.25 to trigger reduction
)
def test_dscr_based_loan_reduction(ebitda, collateral_value, dscr):
    """For any loan calculation where DSCR is below 1.25, the recommended loan amount
    should be reduced proportionally from the initial calculation.
    
    **Validates: Requirements 11.3**
    """
    calculator = LoanCalculator()
    
    max_amount, breakdown = calculator.calculate_max_loan_amount(
        ebitda=ebitda,
        collateral_value=collateral_value,
        dscr=dscr,
    )
    
    # DSCR reduction factor should be DSCR / 1.25
    expected_reduction_factor = dscr / 1.25
    assert abs(breakdown.dscr_based_reduction - expected_reduction_factor) < 0.0001
    
    # Final amount should be reduced by this factor
    amount_before_reduction = min(ebitda * 0.4, collateral_value * 0.75)
    expected_final = amount_before_reduction * expected_reduction_factor
    assert abs(max_amount - expected_final) < 0.01


# Feature: intelli-credit, Property 28: Loan Amount Calculation Breakdown
@settings(max_examples=15, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(
    ebitda=st.floats(min_value=0.01, max_value=1e8),
    collateral_value=st.floats(min_value=0.01, max_value=1e8),
    dscr=st.floats(min_value=0.01, max_value=5.0),
)
def test_loan_amount_calculation_breakdown(ebitda, collateral_value, dscr):
    """For any calculated loan amount, the system should provide a breakdown
    of the calculation methodology.
    
    **Validates: Requirements 11.4**
    """
    calculator = LoanCalculator()
    
    max_amount, breakdown = calculator.calculate_max_loan_amount(
        ebitda=ebitda,
        collateral_value=collateral_value,
        dscr=dscr,
    )
    
    # Breakdown should contain all required fields
    assert breakdown.ebitda_based_amount >= 0
    assert breakdown.collateral_based_cap >= 0
    assert breakdown.dscr_based_reduction >= 0
    assert breakdown.final_amount >= 0
    assert breakdown.limiting_constraint
    assert len(breakdown.calculation_steps) > 0
    assert "constraints_applied" in breakdown.__dict__


# Feature: intelli-credit, Property 29: Most Conservative Constraint Application
@settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
@given(
    ebitda=st.floats(min_value=0.01, max_value=1e8),
    collateral_value=st.floats(min_value=0.01, max_value=1e8),
    dscr=st.floats(min_value=0.01, max_value=5.0),
)
def test_most_conservative_constraint_application(ebitda, collateral_value, dscr):
    """For any loan calculation with multiple limiting factors (EBITDA, collateral, DSCR),
    the system should apply the most conservative (lowest) constraint as the final recommendation.
    
    **Validates: Requirements 11.5**
    """
    calculator = LoanCalculator()
    
    max_amount, breakdown = calculator.calculate_max_loan_amount(
        ebitda=ebitda,
        collateral_value=collateral_value,
        dscr=dscr,
    )
    
    # Calculate all constraints
    ebitda_based = ebitda * 0.4
    collateral_cap = collateral_value * 0.75
    
    # Apply collateral cap first
    amount_after_collateral = min(ebitda_based, collateral_cap)
    
    # Apply DSCR reduction
    dscr_reduction_factor = dscr / 1.25 if dscr < 1.25 else 1.0
    expected_final = amount_after_collateral * dscr_reduction_factor
    
    # Final amount should match the most conservative constraint
    assert abs(max_amount - expected_final) < 0.01
    
    # Final amount should never exceed any individual constraint
    assert max_amount <= ebitda_based + 0.01
    assert max_amount <= collateral_cap + 0.01


# Feature: intelli-credit, Property 30: Interest Rate Formula
@settings(max_examples=15)
@given(
    base_rate=st.floats(min_value=0.0, max_value=20.0),
    risk_score=st.floats(min_value=0.0, max_value=100.0),
)
def test_interest_rate_formula(base_rate, risk_score):
    """For any calculated risk score, the determined interest rate should equal
    base rate plus risk premium.
    
    **Validates: Requirements 12.1**
    """
    calculator = LoanCalculator()
    
    interest_rate, risk_premium, classification = calculator.determine_interest_rate(
        base_rate=base_rate,
        risk_score=risk_score,
    )
    
    # Interest rate should equal base rate + risk premium
    expected_rate = base_rate + risk_premium
    assert abs(interest_rate - expected_rate) < 0.01


# Feature: intelli-credit, Property 31: High Risk Premium (5%+)
@settings(max_examples=15)
@given(
    base_rate=st.floats(min_value=0.0, max_value=20.0),
    risk_score=st.floats(min_value=0.0, max_value=39.99),  # High risk: < 40
)
def test_high_risk_premium(base_rate, risk_score):
    """For any risk score below 40 (high risk), the system should apply
    a risk premium of at least 5 percentage points.
    
    **Validates: Requirements 12.2**
    """
    calculator = LoanCalculator()
    
    interest_rate, risk_premium, classification = calculator.determine_interest_rate(
        base_rate=base_rate,
        risk_score=risk_score,
    )
    
    # High risk should have premium >= 5%
    assert risk_premium >= 5.0
    assert classification == "high"


# Feature: intelli-credit, Property 32: Medium Risk Premium (2-5%)
@settings(max_examples=15)
@given(
    base_rate=st.floats(min_value=0.0, max_value=20.0),
    risk_score=st.floats(min_value=40.0, max_value=69.99),  # Medium risk: 40-70
)
def test_medium_risk_premium(base_rate, risk_score):
    """For any risk score between 40 and 70 (medium risk), the system should apply
    a risk premium between 2 and 5 percentage points.
    
    **Validates: Requirements 12.3**
    """
    calculator = LoanCalculator()
    
    interest_rate, risk_premium, classification = calculator.determine_interest_rate(
        base_rate=base_rate,
        risk_score=risk_score,
    )
    
    # Medium risk should have premium between 2% and 5%
    assert 2.0 <= risk_premium <= 5.0
    assert classification == "medium"


# Feature: intelli-credit, Property 33: Low Risk Premium (0-2%)
@settings(max_examples=15)
@given(
    base_rate=st.floats(min_value=0.0, max_value=20.0),
    risk_score=st.floats(min_value=70.0, max_value=100.0),  # Low risk: > 70
)
def test_low_risk_premium(base_rate, risk_score):
    """For any risk score above 70 (low risk), the system should apply
    a risk premium between 0 and 2 percentage points.
    
    **Validates: Requirements 12.4**
    """
    calculator = LoanCalculator()
    
    interest_rate, risk_premium, classification = calculator.determine_interest_rate(
        base_rate=base_rate,
        risk_score=risk_score,
    )
    
    # Low risk should have premium between 0% and 2%
    assert 0.0 <= risk_premium <= 2.0
    assert classification == "low"


# Feature: intelli-credit, Property 34: Loan Explanation Completeness
@settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
@given(
    ebitda=st.floats(min_value=0.01, max_value=1e8),
    collateral_value=st.floats(min_value=0.01, max_value=1e8),
    dscr=st.floats(min_value=0.01, max_value=5.0),
)
def test_loan_explanation_completeness(ebitda, collateral_value, dscr):
    """For any calculated loan amount, the system should provide a breakdown
    of the calculation methodology with explanations.
    
    **Validates: Requirements 11.4, 13.3**
    """
    calculator = LoanCalculator()
    
    max_amount, breakdown = calculator.calculate_max_loan_amount(
        ebitda=ebitda,
        collateral_value=collateral_value,
        dscr=dscr,
    )
    
    explanation = calculator.generate_loan_explanation(
        breakdown=breakdown,
        ebitda=ebitda,
        collateral_value=collateral_value,
        dscr=dscr,
    )
    
    # Explanation should have all required components
    assert explanation.summary
    assert len(explanation.key_factors) > 0
    assert len(explanation.data_sources) > 0
    assert explanation.reasoning
    
    # Explanation should reference the limiting constraint
    assert breakdown.limiting_constraint in explanation.summary or \
           breakdown.limiting_constraint.lower() in explanation.summary.lower()


# Feature: intelli-credit, Property 35: Rate Explanation Completeness
@settings(max_examples=15)
@given(
    base_rate=st.floats(min_value=0.0, max_value=20.0),
    risk_score=st.floats(min_value=0.0, max_value=100.0),
)
def test_rate_explanation_completeness(base_rate, risk_score):
    """For any calculated interest rate, the system should provide explanations
    for the rate components (base rate and risk premium).
    
    **Validates: Requirements 12.5, 13.4**
    """
    calculator = LoanCalculator()
    
    interest_rate, risk_premium, classification = calculator.determine_interest_rate(
        base_rate=base_rate,
        risk_score=risk_score,
    )
    
    explanation = calculator.generate_rate_explanation(
        interest_rate=interest_rate,
        base_rate=base_rate,
        risk_premium=risk_premium,
        risk_classification=classification,
        risk_score=risk_score,
    )
    
    # Explanation should have all required components
    assert explanation.summary
    assert len(explanation.key_factors) > 0
    assert len(explanation.data_sources) > 0
    assert explanation.reasoning
    
    # Explanation should reference the risk classification
    assert classification in explanation.summary.lower()
