"""Unit tests for RiskAggregator class."""

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


@pytest.fixture
def risk_aggregator():
    """Create a RiskAggregator instance for testing."""
    return RiskAggregator()


@pytest.fixture
def default_weights():
    """Default weights for Five Cs components."""
    return {
        'character': 0.25,
        'capacity': 0.25,
        'capital': 0.20,
        'collateral': 0.20,
        'conditions': 0.10,
    }


@pytest.fixture
def sample_five_cs():
    """Create a sample FiveCsScores object for testing."""
    return FiveCsScores(
        character=CharacterScore(
            score=75.0,
            litigation_count=1,
            governance_rating="Good",
            credit_bureau_score=700,
            negative_factors=["Minor litigation"],
        ),
        capacity=CapacityScore(
            score=80.0,
            dscr=1.5,
            cash_flow=1000000,
            debt_service=666667,
            trend="stable",
        ),
        capital=CapitalScore(
            score=70.0,
            debt_equity_ratio=1.5,
            net_worth=5000000,
            net_worth_trend="stable",
        ),
        collateral=CollateralScore(
            score=85.0,
            ltv=0.6,
            collateral_type="Real Estate",
            valuation_date=datetime.now(),
        ),
        conditions=ConditionsScore(
            score=65.0,
            sector_risk="medium",
            regulatory_risk="low",
            commodity_risk="low",
            risk_factors=["Sector volatility"],
        ),
    )


class TestCalculateCompositeRiskScore:
    """Tests for calculate_composite_risk_score method."""

    def test_basic_weighted_calculation(self, risk_aggregator, sample_five_cs, default_weights):
        """Test basic weighted calculation of composite risk score."""
        risk_score = risk_aggregator.calculate_composite_risk_score(sample_five_cs, default_weights)
        
        # Expected: 75*0.25 + 80*0.25 + 70*0.20 + 85*0.20 + 65*0.10
        # = 18.75 + 20 + 14 + 17 + 6.5 = 76.25
        expected_score = 76.25
        
        assert abs(risk_score.overall_score - expected_score) < 0.01
        assert risk_score.overall_score == pytest.approx(expected_score, abs=0.01)

    def test_score_within_valid_range(self, risk_aggregator, sample_five_cs, default_weights):
        """Test that composite score is always within 0-100 range."""
        risk_score = risk_aggregator.calculate_composite_risk_score(sample_five_cs, default_weights)
        
        assert 0.0 <= risk_score.overall_score <= 100.0

    def test_all_perfect_scores(self, risk_aggregator, default_weights):
        """Test with all Five Cs scores at 100."""
        perfect_five_cs = FiveCsScores(
            character=CharacterScore(score=100.0, litigation_count=0, governance_rating="Excellent", credit_bureau_score=900),
            capacity=CapacityScore(score=100.0, dscr=3.0, cash_flow=2000000, debt_service=500000, trend="improving"),
            capital=CapitalScore(score=100.0, debt_equity_ratio=0.5, net_worth=10000000, net_worth_trend="improving"),
            collateral=CollateralScore(score=100.0, ltv=0.3, collateral_type="Real Estate", valuation_date=datetime.now()),
            conditions=ConditionsScore(score=100.0, sector_risk="low", regulatory_risk="low", commodity_risk="low"),
        )
        
        risk_score = risk_aggregator.calculate_composite_risk_score(perfect_five_cs, default_weights)
        
        assert risk_score.overall_score == pytest.approx(100.0, abs=0.01)

    def test_all_zero_scores(self, risk_aggregator, default_weights):
        """Test with all Five Cs scores at 0."""
        zero_five_cs = FiveCsScores(
            character=CharacterScore(score=0.0, litigation_count=10, governance_rating="Poor", credit_bureau_score=300),
            capacity=CapacityScore(score=0.0, dscr=0.5, cash_flow=100000, debt_service=500000, trend="declining"),
            capital=CapitalScore(score=0.0, debt_equity_ratio=5.0, net_worth=100000, net_worth_trend="declining"),
            collateral=CollateralScore(score=0.0, ltv=1.5, collateral_type="None", valuation_date=datetime.now()),
            conditions=ConditionsScore(score=0.0, sector_risk="high", regulatory_risk="high", commodity_risk="high"),
        )
        
        risk_score = risk_aggregator.calculate_composite_risk_score(zero_five_cs, default_weights)
        
        assert risk_score.overall_score == pytest.approx(0.0, abs=0.01)

    def test_missing_weight_key_raises_error(self, risk_aggregator, sample_five_cs):
        """Test that missing weight key raises ValueError."""
        incomplete_weights = {
            'character': 0.25,
            'capacity': 0.25,
            'capital': 0.20,
            # Missing 'collateral' and 'conditions'
        }
        
        with pytest.raises(ValueError, match="Missing required weight keys"):
            risk_aggregator.calculate_composite_risk_score(sample_five_cs, incomplete_weights)

    def test_weights_not_summing_to_one_raises_error(self, risk_aggregator, sample_five_cs):
        """Test that weights not summing to 1.0 raises ValueError."""
        invalid_weights = {
            'character': 0.25,
            'capacity': 0.25,
            'capital': 0.20,
            'collateral': 0.20,
            'conditions': 0.05,  # Sum = 0.95, not 1.0
        }
        
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            risk_aggregator.calculate_composite_risk_score(sample_five_cs, invalid_weights)

    def test_different_weight_distributions(self, risk_aggregator, sample_five_cs):
        """Test with different weight distributions."""
        # Emphasize character and capacity
        weights_v1 = {
            'character': 0.40,
            'capacity': 0.40,
            'capital': 0.10,
            'collateral': 0.05,
            'conditions': 0.05,
        }
        
        risk_score_v1 = risk_aggregator.calculate_composite_risk_score(sample_five_cs, weights_v1)
        
        # Expected: 75*0.40 + 80*0.40 + 70*0.10 + 85*0.05 + 65*0.05
        # = 30 + 32 + 7 + 4.25 + 3.25 = 76.5
        expected_v1 = 76.5
        assert risk_score_v1.overall_score == pytest.approx(expected_v1, abs=0.01)

    def test_risk_level_classification_included(self, risk_aggregator, sample_five_cs, default_weights):
        """Test that risk level classification is included in result."""
        risk_score = risk_aggregator.calculate_composite_risk_score(sample_five_cs, default_weights)
        
        assert risk_score.risk_level in ["high", "medium", "low"]

    def test_top_factors_included(self, risk_aggregator, sample_five_cs, default_weights):
        """Test that top risk and positive factors are included."""
        risk_score = risk_aggregator.calculate_composite_risk_score(sample_five_cs, default_weights)
        
        assert isinstance(risk_score.top_risk_factors, list)
        assert isinstance(risk_score.top_positive_factors, list)
        assert len(risk_score.top_risk_factors) <= 3
        assert len(risk_score.top_positive_factors) <= 3


class TestClassifyRiskLevel:
    """Tests for classify_risk_level method."""

    def test_high_risk_classification(self, risk_aggregator):
        """Test classification of high risk (score < 40)."""
        assert risk_aggregator.classify_risk_level(0) == "high"
        assert risk_aggregator.classify_risk_level(20) == "high"
        assert risk_aggregator.classify_risk_level(39.9) == "high"

    def test_medium_risk_classification(self, risk_aggregator):
        """Test classification of medium risk (40 <= score <= 70)."""
        assert risk_aggregator.classify_risk_level(40) == "medium"
        assert risk_aggregator.classify_risk_level(55) == "medium"
        assert risk_aggregator.classify_risk_level(70) == "medium"

    def test_low_risk_classification(self, risk_aggregator):
        """Test classification of low risk (score > 70)."""
        assert risk_aggregator.classify_risk_level(70.1) == "low"
        assert risk_aggregator.classify_risk_level(85) == "low"
        assert risk_aggregator.classify_risk_level(100) == "low"

    def test_boundary_values(self, risk_aggregator):
        """Test boundary values for risk classification."""
        # Boundary at 40
        assert risk_aggregator.classify_risk_level(39.99) == "high"
        assert risk_aggregator.classify_risk_level(40.0) == "medium"
        
        # Boundary at 70
        assert risk_aggregator.classify_risk_level(70.0) == "medium"
        assert risk_aggregator.classify_risk_level(70.01) == "low"

    def test_invalid_score_below_zero_raises_error(self, risk_aggregator):
        """Test that score below 0 raises ValueError."""
        with pytest.raises(ValueError, match="Risk score must be between 0 and 100"):
            risk_aggregator.classify_risk_level(-1)

    def test_invalid_score_above_100_raises_error(self, risk_aggregator):
        """Test that score above 100 raises ValueError."""
        with pytest.raises(ValueError, match="Risk score must be between 0 and 100"):
            risk_aggregator.classify_risk_level(101)

    def test_all_valid_scores(self, risk_aggregator):
        """Test that all valid scores (0-100) return valid classifications."""
        for score in range(0, 101, 10):
            result = risk_aggregator.classify_risk_level(float(score))
            assert result in ["high", "medium", "low"]


class TestExtractTopRiskFactors:
    """Tests for _extract_top_risk_factors method."""

    def test_extracts_from_character_negative_factors(self, risk_aggregator):
        """Test extraction of risk factors from Character component."""
        five_cs = FiveCsScores(
            character=CharacterScore(
                score=30.0,
                litigation_count=5,
                governance_rating="Poor",
                credit_bureau_score=400,
                negative_factors=["High litigation", "Poor governance"],
            ),
            capacity=CapacityScore(score=80.0, dscr=2.0, cash_flow=1000000, debt_service=500000, trend="stable"),
            capital=CapitalScore(score=80.0, debt_equity_ratio=1.0, net_worth=5000000, net_worth_trend="stable"),
            collateral=CollateralScore(score=80.0, ltv=0.5, collateral_type="Real Estate", valuation_date=datetime.now()),
            conditions=ConditionsScore(score=80.0, sector_risk="low", regulatory_risk="low", commodity_risk="low"),
        )
        
        factors = risk_aggregator._extract_top_risk_factors(five_cs)
        
        assert len(factors) > 0
        assert any("High litigation" in f or "Poor governance" in f for f in factors)

    def test_extracts_from_conditions_risk_factors(self, risk_aggregator):
        """Test extraction of risk factors from Conditions component."""
        five_cs = FiveCsScores(
            character=CharacterScore(score=80.0, litigation_count=0, governance_rating="Good", credit_bureau_score=800),
            capacity=CapacityScore(score=80.0, dscr=2.0, cash_flow=1000000, debt_service=500000, trend="stable"),
            capital=CapitalScore(score=80.0, debt_equity_ratio=1.0, net_worth=5000000, net_worth_trend="stable"),
            collateral=CollateralScore(score=80.0, ltv=0.5, collateral_type="Real Estate", valuation_date=datetime.now()),
            conditions=ConditionsScore(
                score=30.0,
                sector_risk="high",
                regulatory_risk="high",
                commodity_risk="high",
                risk_factors=["Sector downturn", "Regulatory changes"],
            ),
        )
        
        factors = risk_aggregator._extract_top_risk_factors(five_cs)
        
        assert len(factors) > 0
        assert any("Sector downturn" in f or "Regulatory changes" in f for f in factors)

    def test_returns_max_three_factors(self, risk_aggregator):
        """Test that at most 3 risk factors are returned."""
        five_cs = FiveCsScores(
            character=CharacterScore(
                score=20.0,
                litigation_count=10,
                governance_rating="Poor",
                credit_bureau_score=300,
                negative_factors=["Factor 1", "Factor 2", "Factor 3", "Factor 4"],
            ),
            capacity=CapacityScore(score=80.0, dscr=2.0, cash_flow=1000000, debt_service=500000, trend="stable"),
            capital=CapitalScore(score=80.0, debt_equity_ratio=1.0, net_worth=5000000, net_worth_trend="stable"),
            collateral=CollateralScore(score=80.0, ltv=0.5, collateral_type="Real Estate", valuation_date=datetime.now()),
            conditions=ConditionsScore(score=80.0, sector_risk="low", regulatory_risk="low", commodity_risk="low"),
        )
        
        factors = risk_aggregator._extract_top_risk_factors(five_cs)
        
        assert len(factors) <= 3


class TestExtractTopPositiveFactors:
    """Tests for _extract_top_positive_factors method."""

    def test_extracts_strong_components(self, risk_aggregator):
        """Test extraction of positive factors from strong components."""
        five_cs = FiveCsScores(
            character=CharacterScore(score=90.0, litigation_count=0, governance_rating="Excellent", credit_bureau_score=850),
            capacity=CapacityScore(score=85.0, dscr=2.5, cash_flow=2000000, debt_service=500000, trend="improving"),
            capital=CapitalScore(score=20.0, debt_equity_ratio=3.0, net_worth=1000000, net_worth_trend="declining"),
            collateral=CollateralScore(score=30.0, ltv=1.2, collateral_type="None", valuation_date=datetime.now()),
            conditions=ConditionsScore(score=40.0, sector_risk="high", regulatory_risk="high", commodity_risk="high"),
        )
        
        factors = risk_aggregator._extract_top_positive_factors(five_cs)
        
        assert len(factors) > 0
        assert any("Character" in f for f in factors)
        assert any("Capacity" in f for f in factors)

    def test_returns_max_three_factors(self, risk_aggregator):
        """Test that at most 3 positive factors are returned."""
        five_cs = FiveCsScores(
            character=CharacterScore(score=95.0, litigation_count=0, governance_rating="Excellent", credit_bureau_score=880),
            capacity=CapacityScore(score=90.0, dscr=3.0, cash_flow=3000000, debt_service=500000, trend="improving"),
            capital=CapitalScore(score=85.0, debt_equity_ratio=0.8, net_worth=8000000, net_worth_trend="improving"),
            collateral=CollateralScore(score=80.0, ltv=0.4, collateral_type="Real Estate", valuation_date=datetime.now()),
            conditions=ConditionsScore(score=75.0, sector_risk="low", regulatory_risk="low", commodity_risk="low"),
        )
        
        factors = risk_aggregator._extract_top_positive_factors(five_cs)
        
        assert len(factors) <= 3

    def test_no_positive_factors_for_low_scores(self, risk_aggregator):
        """Test that no positive factors are extracted when all scores are low."""
        five_cs = FiveCsScores(
            character=CharacterScore(score=30.0, litigation_count=5, governance_rating="Poor", credit_bureau_score=400),
            capacity=CapacityScore(score=25.0, dscr=0.8, cash_flow=200000, debt_service=500000, trend="declining"),
            capital=CapitalScore(score=20.0, debt_equity_ratio=4.0, net_worth=500000, net_worth_trend="declining"),
            collateral=CollateralScore(score=15.0, ltv=1.5, collateral_type="None", valuation_date=datetime.now()),
            conditions=ConditionsScore(score=10.0, sector_risk="high", regulatory_risk="high", commodity_risk="high"),
        )
        
        factors = risk_aggregator._extract_top_positive_factors(five_cs)
        
        # Should have few or no positive factors
        assert len(factors) <= 1
