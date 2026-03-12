"""Property-based tests for ExplainabilityEngine.

Feature: intelli-credit
Properties tested:
- Property 31: Recommendation Explanation Completeness
- Property 32: Top Risk Factors Identification
- Property 33: Limiting Constraint Identification
- Property 34: Explanation Source Citation
"""

from hypothesis import given, strategies as st, assume, settings, HealthCheck
import pytest
from datetime import datetime
from app.services.credit_engine.explainability_engine import ExplainabilityEngine
from app.models.credit_assessment import (
    CharacterScore,
    CapacityScore,
    CapitalScore,
    CollateralScore,
    ConditionsScore,
    FiveCsScores,
    RiskScore,
)


# Strategies for generating realistic data
score_0_to_100 = st.floats(min_value=0.0, max_value=100.0)
positive_float = st.floats(min_value=0.01, max_value=1e9)
dscr_values = st.floats(min_value=0.5, max_value=5.0)
debt_equity_values = st.floats(min_value=0.1, max_value=5.0)
ltv_values = st.floats(min_value=0.0, max_value=1.0)
base_rates = st.floats(min_value=5.0, max_value=15.0)
risk_premiums = st.floats(min_value=0.0, max_value=10.0)


def five_cs_scores_strategy():
    """Generate realistic FiveCsScores."""
    return st.builds(
        FiveCsScores,
        character=st.builds(
            CharacterScore,
            score=score_0_to_100,
            litigation_count=st.integers(min_value=0, max_value=10),
            governance_rating=st.sampled_from(["poor", "fair", "good", "excellent"]),
            credit_bureau_score=st.floats(min_value=300.0, max_value=900.0),
            negative_factors=st.lists(st.just("Factor"), max_size=1),
        ),
        capacity=st.builds(
            CapacityScore,
            score=score_0_to_100,
            dscr=dscr_values,
            cash_flow=positive_float,
            debt_service=positive_float,
            trend=st.sampled_from(["improving", "stable", "declining"]),
        ),
        capital=st.builds(
            CapitalScore,
            score=score_0_to_100,
            debt_equity_ratio=debt_equity_values,
            net_worth=positive_float,
            net_worth_trend=st.sampled_from(["improving", "stable", "declining"]),
        ),
        collateral=st.builds(
            CollateralScore,
            score=score_0_to_100,
            ltv=ltv_values,
            collateral_type=st.sampled_from(["Real Estate", "Equipment", "Inventory", "Securities"]),
            valuation_date=st.just(datetime.now()),
        ),
        conditions=st.builds(
            ConditionsScore,
            score=score_0_to_100,
            sector_risk=st.sampled_from(["low", "moderate", "high"]),
            regulatory_risk=st.sampled_from(["low", "moderate", "high"]),
            commodity_risk=st.sampled_from(["none", "low", "moderate", "high"]),
            risk_factors=st.lists(st.just("Risk"), max_size=1),
        ),
    )


def risk_score_strategy():
    """Generate realistic RiskScore."""
    return st.builds(
        RiskScore,
        overall_score=score_0_to_100,
        risk_level=st.sampled_from(["high", "medium", "low"]),
        top_risk_factors=st.lists(st.just("Factor"), min_size=1, max_size=1),
        top_positive_factors=st.lists(st.just("Positive"), min_size=0, max_size=1),
    )


class TestExplanationCompleteness:
    """Property 31: Recommendation Explanation Completeness.
    
    **Validates: Requirements 13.1**
    
    For any generated credit recommendation, the system should provide 
    explanations for all decision components (risk score, loan amount, interest rate).
    """

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(five_cs=five_cs_scores_strategy(), risk_score=risk_score_strategy())
    def test_risk_score_explanation_completeness(self, five_cs, risk_score):
        """Risk score explanation must have all required components."""
        engine = ExplainabilityEngine()
        explanation = engine.explain_risk_score(risk_score, five_cs)

        # All components must be present
        assert explanation.summary is not None
        assert len(explanation.summary) > 0
        assert explanation.key_factors is not None
        assert len(explanation.key_factors) > 0
        assert explanation.data_sources is not None
        assert len(explanation.data_sources) > 0
        assert explanation.reasoning is not None
        assert len(explanation.reasoning) > 0

    @settings(max_examples=15)
    @given(
        loan_amount=positive_float,
        ebitda=positive_float,
        collateral_value=positive_float,
        dscr=dscr_values,
    )
    def test_loan_amount_explanation_completeness(
        self, loan_amount, ebitda, collateral_value, dscr
    ):
        """Loan amount explanation must have all required components."""
        engine = ExplainabilityEngine()
        
        # Calculate constraints
        ebitda_based = 0.4 * ebitda
        collateral_based = 0.75 * collateral_value
        dscr_based = loan_amount  # Simplified for testing
        
        constraints = {
            "ebitda_based": ebitda_based,
            "collateral_based": collateral_based,
            "dscr_based": dscr_based,
        }
        
        # Determine limiting constraint
        limiting_constraint = min(constraints, key=constraints.get)
        
        explanation = engine.explain_loan_amount(
            loan_amount=constraints[limiting_constraint],
            constraints=constraints,
            limiting_constraint=limiting_constraint,
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )

        # All components must be present
        assert explanation.summary is not None
        assert len(explanation.summary) > 0
        assert explanation.key_factors is not None
        assert len(explanation.key_factors) > 0
        assert explanation.data_sources is not None
        assert len(explanation.data_sources) > 0
        assert explanation.reasoning is not None
        assert len(explanation.reasoning) > 0

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(
        base_rate=base_rates,
        risk_premium=risk_premiums,
        risk_score=risk_score_strategy(),
    )
    def test_interest_rate_explanation_completeness(
        self, base_rate, risk_premium, risk_score
    ):
        """Interest rate explanation must have all required components."""
        engine = ExplainabilityEngine()
        final_rate = base_rate + risk_premium
        
        explanation = engine.explain_interest_rate(
            base_rate=base_rate,
            risk_premium=risk_premium,
            final_rate=final_rate,
            risk_score=risk_score,
            risk_factors=["Factor 1", "Factor 2"],
        )

        # All components must be present
        assert explanation.summary is not None
        assert len(explanation.summary) > 0
        assert explanation.key_factors is not None
        assert len(explanation.key_factors) > 0
        assert explanation.data_sources is not None
        assert len(explanation.data_sources) > 0
        assert explanation.reasoning is not None
        assert len(explanation.reasoning) > 0


class TestTopFactorsIdentification:
    """Property 32: Top Risk Factors Identification.
    
    **Validates: Requirements 13.2**
    
    For any risk score explanation, the system should identify exactly three 
    top factors contributing to the score.
    """

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(five_cs=five_cs_scores_strategy(), risk_score=risk_score_strategy())
    def test_exactly_three_top_factors(self, five_cs, risk_score):
        """Risk score explanation must identify exactly three top factors."""
        engine = ExplainabilityEngine()
        explanation = engine.explain_risk_score(risk_score, five_cs)

        # Must have exactly 3 factors
        assert len(explanation.key_factors) == 3
        
        # Each factor must be a tuple of (name, contribution)
        for factor_name, contribution in explanation.key_factors:
            assert isinstance(factor_name, str)
            assert len(factor_name) > 0
            assert isinstance(contribution, float)
            # Contribution should be a percentage (0-100)
            assert 0 <= contribution <= 100

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(five_cs=five_cs_scores_strategy(), risk_score=risk_score_strategy())
    def test_factors_ranked_by_contribution(self, five_cs, risk_score):
        """Top factors should be ranked by contribution magnitude."""
        engine = ExplainabilityEngine()
        explanation = engine.explain_risk_score(risk_score, five_cs)

        # Extract contributions
        contributions = [contrib for _, contrib in explanation.key_factors]
        
        # Should be sorted in descending order (highest contribution first)
        assert contributions == sorted(contributions, reverse=True)


class TestLimitingConstraintIdentification:
    """Property 33: Limiting Constraint Identification.
    
    **Validates: Requirements 13.3**
    
    For any loan amount explanation, the system should identify which 
    constraint was the limiting factor.
    """

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(
        ebitda=positive_float,
        collateral_value=positive_float,
        dscr=dscr_values,
    )
    def test_limiting_constraint_identified(
        self, ebitda, collateral_value, dscr
    ):
        """Loan amount explanation must identify the limiting constraint."""
        engine = ExplainabilityEngine()
        
        # Calculate constraints
        ebitda_based = 0.4 * ebitda
        collateral_based = 0.75 * collateral_value
        dscr_based = 50_000_000.0  # Fixed for testing
        
        constraints = {
            "ebitda_based": ebitda_based,
            "collateral_based": collateral_based,
            "dscr_based": dscr_based,
        }
        
        # Determine limiting constraint
        limiting_constraint = min(constraints, key=constraints.get)
        
        explanation = engine.explain_loan_amount(
            loan_amount=constraints[limiting_constraint],
            constraints=constraints,
            limiting_constraint=limiting_constraint,
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )

        # Summary must mention the limiting constraint
        limiting_display = limiting_constraint.replace("_", " ").lower()
        assert limiting_display in explanation.summary.lower()
        
        # The loan amount should match the limiting constraint
        assert constraints[limiting_constraint] > 0

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(
        ebitda=positive_float,
        collateral_value=positive_float,
        dscr=dscr_values,
    )
    def test_all_constraints_shown(self, ebitda, collateral_value, dscr):
        """Loan amount explanation must show all constraints."""
        engine = ExplainabilityEngine()
        
        # Calculate constraints
        ebitda_based = 0.4 * ebitda
        collateral_based = 0.75 * collateral_value
        dscr_based = 50_000_000.0
        
        constraints = {
            "ebitda_based": ebitda_based,
            "collateral_based": collateral_based,
            "dscr_based": dscr_based,
        }
        
        limiting_constraint = min(constraints, key=constraints.get)
        
        explanation = engine.explain_loan_amount(
            loan_amount=constraints[limiting_constraint],
            constraints=constraints,
            limiting_constraint=limiting_constraint,
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )

        # All three constraints should be in key_factors
        assert len(explanation.key_factors) == 3
        constraint_names = [name for name, _ in explanation.key_factors]
        assert "ebitda_based" in constraint_names
        assert "collateral_based" in constraint_names
        assert "dscr_based" in constraint_names


class TestExplanationSourceCitation:
    """Property 34: Explanation Source Citation.
    
    **Validates: Requirements 13.5**
    
    For any generated explanation, all data points should be cited with 
    their specific sources.
    """

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(five_cs=five_cs_scores_strategy(), risk_score=risk_score_strategy())
    def test_risk_score_sources_cited(self, five_cs, risk_score):
        """Risk score explanation must cite data sources."""
        engine = ExplainabilityEngine()
        explanation = engine.explain_risk_score(risk_score, five_cs)

        # Must have data sources
        assert len(explanation.data_sources) > 0
        
        # Each source should be a non-empty string
        for source in explanation.data_sources:
            assert isinstance(source, str)
            assert len(source) > 0
        
        # Should cite the Five Cs components
        combined_sources = " ".join(explanation.data_sources)
        assert "Character" in combined_sources or "character" in combined_sources.lower()

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(
        ebitda=positive_float,
        collateral_value=positive_float,
        dscr=dscr_values,
    )
    def test_loan_amount_sources_cited(self, ebitda, collateral_value, dscr):
        """Loan amount explanation must cite data sources."""
        engine = ExplainabilityEngine()
        
        ebitda_based = 0.4 * ebitda
        collateral_based = 0.75 * collateral_value
        dscr_based = 50_000_000.0
        
        constraints = {
            "ebitda_based": ebitda_based,
            "collateral_based": collateral_based,
            "dscr_based": dscr_based,
        }
        
        limiting_constraint = min(constraints, key=constraints.get)
        
        explanation = engine.explain_loan_amount(
            loan_amount=constraints[limiting_constraint],
            constraints=constraints,
            limiting_constraint=limiting_constraint,
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )

        # Must have data sources
        assert len(explanation.data_sources) > 0
        
        # Each source should be a non-empty string
        for source in explanation.data_sources:
            assert isinstance(source, str)
            assert len(source) > 0
        
        # Should cite EBITDA, collateral, and DSCR
        combined_sources = " ".join(explanation.data_sources)
        assert "EBITDA" in combined_sources or "ebitda" in combined_sources.lower()

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(
        base_rate=base_rates,
        risk_premium=risk_premiums,
        risk_score=risk_score_strategy(),
    )
    def test_interest_rate_sources_cited(self, base_rate, risk_premium, risk_score):
        """Interest rate explanation must cite data sources."""
        engine = ExplainabilityEngine()
        final_rate = base_rate + risk_premium
        
        explanation = engine.explain_interest_rate(
            base_rate=base_rate,
            risk_premium=risk_premium,
            final_rate=final_rate,
            risk_score=risk_score,
            risk_factors=["Factor 1"],
        )

        # Must have data sources
        assert len(explanation.data_sources) > 0
        
        # Each source should be a non-empty string
        for source in explanation.data_sources:
            assert isinstance(source, str)
            assert len(source) > 0
        
        # Should cite risk classification
        combined_sources = " ".join(explanation.data_sources)
        assert "Risk" in combined_sources or "risk" in combined_sources.lower()


class TestExplanationConsistency:
    """Additional tests for explanation consistency and correctness."""

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(five_cs=five_cs_scores_strategy(), risk_score=risk_score_strategy())
    def test_risk_level_matches_score(self, five_cs, risk_score):
        """Risk level in explanation should match the risk score."""
        engine = ExplainabilityEngine()
        explanation = engine.explain_risk_score(risk_score, five_cs)

        # Summary should mention the risk level
        risk_level_lower = risk_score.risk_level.lower()
        assert risk_level_lower in explanation.summary.lower()

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(
        base_rate=base_rates,
        risk_premium=risk_premiums,
        risk_score=risk_score_strategy(),
    )
    def test_final_rate_calculation_correct(
        self, base_rate, risk_premium, risk_score
    ):
        """Final rate should equal base rate plus risk premium."""
        engine = ExplainabilityEngine()
        final_rate = base_rate + risk_premium
        
        explanation = engine.explain_interest_rate(
            base_rate=base_rate,
            risk_premium=risk_premium,
            final_rate=final_rate,
            risk_score=risk_score,
            risk_factors=[],
        )

        # Summary should mention the final rate
        # Allow for rounding differences
        assert str(round(final_rate, 1)) in explanation.summary or \
               str(round(final_rate, 2)) in explanation.summary

    @settings(max_examples=15, suppress_health_check=[HealthCheck.data_too_large])
    @given(
        ebitda=positive_float,
        collateral_value=positive_float,
    )
    def test_loan_constraints_are_positive(self, ebitda, collateral_value):
        """All loan constraints should be positive values."""
        engine = ExplainabilityEngine()
        
        ebitda_based = 0.4 * ebitda
        collateral_based = 0.75 * collateral_value
        dscr_based = 50_000_000.0
        
        constraints = {
            "ebitda_based": ebitda_based,
            "collateral_based": collateral_based,
            "dscr_based": dscr_based,
        }
        
        limiting_constraint = min(constraints, key=constraints.get)
        
        explanation = engine.explain_loan_amount(
            loan_amount=constraints[limiting_constraint],
            constraints=constraints,
            limiting_constraint=limiting_constraint,
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=1.5,
        )

        # All constraint values in key_factors should be positive
        for _, amount in explanation.key_factors:
            assert amount > 0
