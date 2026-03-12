"""Unit tests for ExplainabilityEngine."""

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
    Explanation,
)


@pytest.fixture
def explainability_engine():
    """Create ExplainabilityEngine instance."""
    return ExplainabilityEngine()


@pytest.fixture
def sample_five_cs():
    """Create sample FiveCsScores for testing."""
    return FiveCsScores(
        character=CharacterScore(
            score=75.0,
            litigation_count=1,
            governance_rating="good",
            credit_bureau_score=750.0,
            negative_factors=["One past litigation case"],
        ),
        capacity=CapacityScore(
            score=80.0,
            dscr=1.75,
            cash_flow=50_000_000.0,
            debt_service=28_571_428.0,
            trend="stable",
        ),
        capital=CapitalScore(
            score=70.0,
            debt_equity_ratio=1.2,
            net_worth=100_000_000.0,
            net_worth_trend="improving",
        ),
        collateral=CollateralScore(
            score=85.0,
            ltv=0.60,
            collateral_type="Real Estate",
            valuation_date=datetime.now(),
        ),
        conditions=ConditionsScore(
            score=65.0,
            sector_risk="moderate",
            regulatory_risk="low",
            commodity_risk="none",
            risk_factors=["Sector cyclicality"],
        ),
    )


@pytest.fixture
def sample_risk_score():
    """Create sample RiskScore for testing."""
    return RiskScore(
        overall_score=75.0,
        risk_level="low",
        top_risk_factors=["Moderate sector risk", "Moderate commodity exposure"],
        top_positive_factors=["Strong collateral", "Good capacity"],
    )


class TestExplainRiskScore:
    """Tests for explain_risk_score method."""

    def test_explain_risk_score_returns_explanation(
        self, explainability_engine, sample_five_cs, sample_risk_score
    ):
        """Test that explain_risk_score returns an Explanation object."""
        explanation = explainability_engine.explain_risk_score(
            sample_risk_score, sample_five_cs
        )

        assert isinstance(explanation, Explanation)
        assert explanation.summary is not None
        assert len(explanation.summary) > 0

    def test_explain_risk_score_includes_top_three_factors(
        self, explainability_engine, sample_five_cs, sample_risk_score
    ):
        """Test that explanation includes exactly three top factors."""
        explanation = explainability_engine.explain_risk_score(
            sample_risk_score, sample_five_cs
        )

        assert len(explanation.key_factors) == 3
        # Each factor should be a tuple of (name, contribution)
        for factor_name, contribution in explanation.key_factors:
            assert isinstance(factor_name, str)
            assert isinstance(contribution, float)
            assert 0 <= contribution <= 100

    def test_explain_risk_score_cites_sources(
        self, explainability_engine, sample_five_cs, sample_risk_score
    ):
        """Test that explanation includes data sources."""
        explanation = explainability_engine.explain_risk_score(
            sample_risk_score, sample_five_cs
        )

        assert len(explanation.data_sources) > 0
        # Should cite Character, Capacity, Capital, Collateral, Conditions sources
        assert any("Character" in source for source in explanation.data_sources)
        assert any("Capacity" in source for source in explanation.data_sources)

    def test_explain_risk_score_high_risk(self, explainability_engine, sample_five_cs):
        """Test explanation for high risk score."""
        high_risk_score = RiskScore(
            overall_score=35.0,
            risk_level="high",
            top_risk_factors=["Low character score", "Low capacity"],
        )

        explanation = explainability_engine.explain_risk_score(
            high_risk_score, sample_five_cs
        )

        assert "high risk" in explanation.summary.lower()

    def test_explain_risk_score_medium_risk(self, explainability_engine, sample_five_cs):
        """Test explanation for medium risk score."""
        medium_risk_score = RiskScore(
            overall_score=55.0,
            risk_level="medium",
            top_risk_factors=["Moderate sector risk"],
        )

        explanation = explainability_engine.explain_risk_score(
            medium_risk_score, sample_five_cs
        )

        assert "medium risk" in explanation.summary.lower()

    def test_explain_risk_score_low_risk(self, explainability_engine, sample_five_cs):
        """Test explanation for low risk score."""
        low_risk_score = RiskScore(
            overall_score=80.0,
            risk_level="low",
            top_risk_factors=["Strong collateral"],
        )

        explanation = explainability_engine.explain_risk_score(
            low_risk_score, sample_five_cs
        )

        assert "low risk" in explanation.summary.lower()

    def test_explain_risk_score_custom_weights(
        self, explainability_engine, sample_five_cs, sample_risk_score
    ):
        """Test explain_risk_score with custom weights."""
        custom_weights = {
            "character": 0.30,
            "capacity": 0.30,
            "capital": 0.15,
            "collateral": 0.15,
            "conditions": 0.10,
        }

        explanation = explainability_engine.explain_risk_score(
            sample_risk_score, sample_five_cs, custom_weights
        )

        assert isinstance(explanation, Explanation)
        assert len(explanation.key_factors) == 3


class TestExplainLoanAmount:
    """Tests for explain_loan_amount method."""

    def test_explain_loan_amount_returns_explanation(self, explainability_engine):
        """Test that explain_loan_amount returns an Explanation object."""
        constraints = {
            "ebitda_based": 50_000_000.0,
            "collateral_based": 30_000_000.0,
            "dscr_based": 40_000_000.0,
        }

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=30_000_000.0,
            constraints=constraints,
            limiting_constraint="collateral_based",
            ebitda=125_000_000.0,
            collateral_value=40_000_000.0,
            dscr=1.75,
        )

        assert isinstance(explanation, Explanation)
        assert explanation.summary is not None

    def test_explain_loan_amount_identifies_limiting_constraint(
        self, explainability_engine
    ):
        """Test that explanation identifies the limiting constraint."""
        constraints = {
            "ebitda_based": 50_000_000.0,
            "collateral_based": 30_000_000.0,
            "dscr_based": 40_000_000.0,
        }

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=30_000_000.0,
            constraints=constraints,
            limiting_constraint="collateral_based",
            collateral_value=40_000_000.0,
        )

        assert "collateral" in explanation.summary.lower()
        assert "30,000,000" in explanation.summary or "30000000" in explanation.summary

    def test_explain_loan_amount_shows_all_constraints(self, explainability_engine):
        """Test that explanation shows all constraints."""
        constraints = {
            "ebitda_based": 50_000_000.0,
            "collateral_based": 30_000_000.0,
            "dscr_based": 40_000_000.0,
        }

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=30_000_000.0,
            constraints=constraints,
            limiting_constraint="collateral_based",
        )

        # Should have all three constraints in key_factors
        assert len(explanation.key_factors) == 3
        constraint_names = [name for name, _ in explanation.key_factors]
        assert "ebitda_based" in constraint_names
        assert "collateral_based" in constraint_names
        assert "dscr_based" in constraint_names

    def test_explain_loan_amount_cites_sources(self, explainability_engine):
        """Test that explanation includes data sources."""
        constraints = {
            "ebitda_based": 50_000_000.0,
            "collateral_based": 30_000_000.0,
            "dscr_based": 40_000_000.0,
        }

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=30_000_000.0,
            constraints=constraints,
            limiting_constraint="collateral_based",
            ebitda=125_000_000.0,
            collateral_value=40_000_000.0,
            dscr=1.75,
        )

        assert len(explanation.data_sources) > 0
        # Should cite EBITDA, collateral, and DSCR
        assert any("EBITDA" in source for source in explanation.data_sources)
        assert any("Collateral" in source for source in explanation.data_sources)
        assert any("DSCR" in source for source in explanation.data_sources)

    def test_explain_loan_amount_ebitda_constraint(self, explainability_engine):
        """Test explanation when EBITDA is the limiting constraint."""
        constraints = {
            "ebitda_based": 30_000_000.0,
            "collateral_based": 50_000_000.0,
            "dscr_based": 40_000_000.0,
        }

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=30_000_000.0,
            constraints=constraints,
            limiting_constraint="ebitda_based",
            ebitda=75_000_000.0,
        )

        assert "ebitda" in explanation.summary.lower()

    def test_explain_loan_amount_dscr_constraint(self, explainability_engine):
        """Test explanation when DSCR is the limiting constraint."""
        constraints = {
            "ebitda_based": 50_000_000.0,
            "collateral_based": 40_000_000.0,
            "dscr_based": 25_000_000.0,
        }

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=25_000_000.0,
            constraints=constraints,
            limiting_constraint="dscr_based",
            dscr=1.1,
        )

        assert "dscr" in explanation.summary.lower()


class TestExplainInterestRate:
    """Tests for explain_interest_rate method."""

    def test_explain_interest_rate_returns_explanation(
        self, explainability_engine, sample_risk_score
    ):
        """Test that explain_interest_rate returns an Explanation object."""
        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=2.5,
            final_rate=11.0,
            risk_score=sample_risk_score,
            risk_factors=["Moderate sector risk"],
        )

        assert isinstance(explanation, Explanation)
        assert explanation.summary is not None

    def test_explain_interest_rate_shows_components(
        self, explainability_engine, sample_risk_score
    ):
        """Test that explanation shows base rate and risk premium."""
        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=2.5,
            final_rate=11.0,
            risk_score=sample_risk_score,
            risk_factors=["Moderate sector risk"],
        )

        # Should have base rate and risk premium in key_factors
        assert len(explanation.key_factors) == 2
        factor_names = [name for name, _ in explanation.key_factors]
        assert "Base Rate" in factor_names
        assert "Risk Premium" in factor_names

    def test_explain_interest_rate_cites_sources(
        self, explainability_engine, sample_risk_score
    ):
        """Test that explanation includes data sources."""
        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=2.5,
            final_rate=11.0,
            risk_score=sample_risk_score,
            risk_factors=["Moderate sector risk"],
        )

        assert len(explanation.data_sources) > 0
        # Should cite risk classification and factors
        assert any("Risk" in source for source in explanation.data_sources)

    def test_explain_interest_rate_high_risk(self, explainability_engine):
        """Test explanation for high risk interest rate."""
        high_risk_score = RiskScore(
            overall_score=35.0,
            risk_level="high",
            top_risk_factors=["Low character", "Low capacity"],
        )

        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=6.0,
            final_rate=14.5,
            risk_score=high_risk_score,
            risk_factors=["Low character", "Low capacity"],
        )

        assert "high" in explanation.summary.lower()
        assert "14.50" in explanation.summary or "14.5" in explanation.summary

    def test_explain_interest_rate_medium_risk(self, explainability_engine):
        """Test explanation for medium risk interest rate."""
        medium_risk_score = RiskScore(
            overall_score=55.0,
            risk_level="medium",
            top_risk_factors=["Moderate sector risk"],
        )

        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=3.5,
            final_rate=12.0,
            risk_score=medium_risk_score,
            risk_factors=["Moderate sector risk"],
        )

        assert "medium" in explanation.summary.lower()

    def test_explain_interest_rate_low_risk(self, explainability_engine):
        """Test explanation for low risk interest rate."""
        low_risk_score = RiskScore(
            overall_score=80.0,
            risk_level="low",
            top_risk_factors=["Strong collateral"],
        )

        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=1.0,
            final_rate=9.5,
            risk_score=low_risk_score,
            risk_factors=["Strong collateral"],
        )

        assert "low" in explanation.summary.lower()

    def test_explain_interest_rate_includes_risk_factors(
        self, explainability_engine, sample_risk_score
    ):
        """Test that explanation includes specific risk factors."""
        risk_factors = ["Low DSCR", "High Debt-to-Equity", "Sector cyclicality"]

        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=2.5,
            final_rate=11.0,
            risk_score=sample_risk_score,
            risk_factors=risk_factors,
        )

        # Should mention risk factors in reasoning
        assert len(explanation.reasoning) > 0


class TestExplanationCompleteness:
    """Tests for explanation completeness and data citation."""

    def test_risk_score_explanation_has_all_components(
        self, explainability_engine, sample_five_cs, sample_risk_score
    ):
        """Test that risk score explanation has all required components."""
        explanation = explainability_engine.explain_risk_score(
            sample_risk_score, sample_five_cs
        )

        # Should have all components
        assert explanation.summary
        assert explanation.key_factors
        assert explanation.data_sources
        assert explanation.reasoning

    def test_loan_amount_explanation_has_all_components(
        self, explainability_engine
    ):
        """Test that loan amount explanation has all required components."""
        constraints = {
            "ebitda_based": 50_000_000.0,
            "collateral_based": 30_000_000.0,
            "dscr_based": 40_000_000.0,
        }

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=30_000_000.0,
            constraints=constraints,
            limiting_constraint="collateral_based",
            ebitda=125_000_000.0,
            collateral_value=40_000_000.0,
            dscr=1.75,
        )

        # Should have all components
        assert explanation.summary
        assert explanation.key_factors
        assert explanation.data_sources
        assert explanation.reasoning

    def test_interest_rate_explanation_has_all_components(
        self, explainability_engine, sample_risk_score
    ):
        """Test that interest rate explanation has all required components."""
        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=2.5,
            final_rate=11.0,
            risk_score=sample_risk_score,
            risk_factors=["Moderate sector risk"],
        )

        # Should have all components
        assert explanation.summary
        assert explanation.key_factors
        assert explanation.data_sources
        assert explanation.reasoning

    def test_explanations_cite_specific_values(
        self, explainability_engine, sample_five_cs, sample_risk_score
    ):
        """Test that explanations cite specific data values."""
        explanation = explainability_engine.explain_risk_score(
            sample_risk_score, sample_five_cs
        )

        # Should cite specific values like DSCR, LTV, etc.
        combined_text = (
            explanation.summary
            + " ".join(explanation.data_sources)
            + explanation.reasoning
        )
        assert "1.75" in combined_text or "DSCR" in combined_text
        assert "0.60" in combined_text or "LTV" in combined_text


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_explain_risk_score_with_zero_scores(self, explainability_engine):
        """Test explanation with all zero scores."""
        five_cs = FiveCsScores(
            character=CharacterScore(
                score=0.0,
                litigation_count=10,
                governance_rating="poor",
                credit_bureau_score=0.0,
                negative_factors=["Multiple litigations"],
            ),
            capacity=CapacityScore(
                score=0.0, dscr=0.5, cash_flow=0.0, debt_service=1_000_000.0, trend="declining"
            ),
            capital=CapitalScore(
                score=0.0, debt_equity_ratio=5.0, net_worth=0.0, net_worth_trend="declining"
            ),
            collateral=CollateralScore(
                score=0.0, ltv=1.0, collateral_type="None", valuation_date=datetime.now()
            ),
            conditions=ConditionsScore(
                score=0.0,
                sector_risk="high",
                regulatory_risk="high",
                commodity_risk="high",
                risk_factors=["Multiple risks"],
            ),
        )

        risk_score = RiskScore(
            overall_score=0.0, risk_level="high", top_risk_factors=["All factors weak"]
        )

        explanation = explainability_engine.explain_risk_score(risk_score, five_cs)

        assert explanation.summary
        assert "high" in explanation.summary.lower()

    def test_explain_risk_score_with_perfect_scores(self, explainability_engine):
        """Test explanation with all perfect scores."""
        five_cs = FiveCsScores(
            character=CharacterScore(
                score=100.0,
                litigation_count=0,
                governance_rating="excellent",
                credit_bureau_score=900.0,
                negative_factors=[],
            ),
            capacity=CapacityScore(
                score=100.0,
                dscr=3.0,
                cash_flow=100_000_000.0,
                debt_service=33_333_333.0,
                trend="improving",
            ),
            capital=CapitalScore(
                score=100.0,
                debt_equity_ratio=0.5,
                net_worth=500_000_000.0,
                net_worth_trend="improving",
            ),
            collateral=CollateralScore(
                score=100.0, ltv=0.3, collateral_type="Real Estate", valuation_date=datetime.now()
            ),
            conditions=ConditionsScore(
                score=100.0,
                sector_risk="low",
                regulatory_risk="low",
                commodity_risk="none",
                risk_factors=[],
            ),
        )

        risk_score = RiskScore(
            overall_score=100.0, risk_level="low", top_risk_factors=["All factors strong"]
        )

        explanation = explainability_engine.explain_risk_score(risk_score, five_cs)

        assert explanation.summary
        assert "low" in explanation.summary.lower()

    def test_explain_loan_amount_with_single_constraint(self, explainability_engine):
        """Test explanation with only one constraint."""
        constraints = {"ebitda_based": 50_000_000.0}

        explanation = explainability_engine.explain_loan_amount(
            loan_amount=50_000_000.0,
            constraints=constraints,
            limiting_constraint="ebitda_based",
            ebitda=125_000_000.0,
        )

        assert explanation.summary
        assert "ebitda" in explanation.summary.lower()

    def test_explain_interest_rate_with_zero_premium(self, explainability_engine):
        """Test explanation with zero risk premium."""
        low_risk_score = RiskScore(
            overall_score=95.0, risk_level="low", top_risk_factors=["Excellent credit"]
        )

        explanation = explainability_engine.explain_interest_rate(
            base_rate=8.5,
            risk_premium=0.0,
            final_rate=8.5,
            risk_score=low_risk_score,
            risk_factors=[],
        )

        assert explanation.summary
        assert "8.5" in explanation.summary or "8.50" in explanation.summary
