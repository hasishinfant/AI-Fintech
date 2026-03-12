"""Unit tests for LoanCalculator class."""

import pytest
from app.services.credit_engine.loan_calculator import LoanCalculator, LoanCalculationBreakdown


class TestLoanCalculatorMaxLoanAmount:
    """Tests for calculate_max_loan_amount method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = LoanCalculator()
    
    def test_ebitda_based_calculation_basic(self):
        """Test basic EBITDA-based calculation (0.4 × EBITDA)."""
        ebitda = 1000000
        collateral_value = 5000000
        dscr = 1.5
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        expected_ebitda_based = ebitda * 0.4
        assert breakdown.ebitda_based_amount == expected_ebitda_based
        assert max_amount == expected_ebitda_based
        assert breakdown.limiting_constraint == "EBITDA-based calculation (0.4 × EBITDA)"
    
    def test_collateral_cap_applies_when_lower(self):
        """Test that collateral cap (75%) applies when lower than EBITDA-based."""
        ebitda = 1000000
        collateral_value = 400000  # 75% = 300,000 < 400,000 (0.4 × EBITDA)
        dscr = 1.5
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        expected_collateral_cap = collateral_value * 0.75
        assert breakdown.collateral_based_cap == expected_collateral_cap
        assert max_amount == expected_collateral_cap
        assert breakdown.limiting_constraint == "Collateral value (75% cap)"
    
    def test_dscr_reduction_below_threshold(self):
        """Test DSCR-based reduction when DSCR < 1.25."""
        ebitda = 1000000
        collateral_value = 5000000
        dscr = 1.0  # Below 1.25 threshold
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        # Expected: 400,000 × (1.0 / 1.25) = 320,000
        expected_amount = (ebitda * 0.4) * (dscr / 1.25)
        assert abs(max_amount - expected_amount) < 0.01
        assert breakdown.limiting_constraint == "Low DSCR (below 1.25)"
    
    def test_dscr_no_reduction_above_threshold(self):
        """Test no DSCR reduction when DSCR >= 1.25."""
        ebitda = 1000000
        collateral_value = 5000000
        dscr = 1.5  # Above 1.25 threshold
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        expected_amount = ebitda * 0.4
        assert abs(max_amount - expected_amount) < 0.01
        assert breakdown.dscr_based_reduction == 1.0
    
    def test_most_conservative_constraint_applied(self):
        """Test that most conservative constraint is applied."""
        ebitda = 1000000
        collateral_value = 300000  # 75% = 225,000
        dscr = 1.0  # Reduction factor = 0.8
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        # EBITDA-based: 400,000
        # Collateral cap: 225,000 (most restrictive)
        # DSCR reduction: 225,000 × 0.8 = 180,000 (most restrictive)
        expected_amount = 225000 * (dscr / 1.25)
        assert abs(max_amount - expected_amount) < 0.01
        assert breakdown.limiting_constraint == "Low DSCR (below 1.25)"
    
    def test_calculation_breakdown_structure(self):
        """Test that breakdown contains all required information."""
        ebitda = 1000000
        collateral_value = 5000000
        dscr = 1.5
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        assert isinstance(breakdown, LoanCalculationBreakdown)
        assert breakdown.ebitda_based_amount > 0
        assert breakdown.collateral_based_cap > 0
        assert breakdown.final_amount > 0
        assert breakdown.limiting_constraint
        assert len(breakdown.calculation_steps) > 0
        assert "constraints_applied" in breakdown.__dict__
    
    def test_zero_ebitda(self):
        """Test with zero EBITDA."""
        ebitda = 0
        collateral_value = 1000000
        dscr = 1.5
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        assert max_amount == 0
        assert breakdown.ebitda_based_amount == 0
    
    def test_high_dscr_no_reduction(self):
        """Test with high DSCR (no reduction)."""
        ebitda = 1000000
        collateral_value = 5000000
        dscr = 3.0
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        expected_amount = ebitda * 0.4
        assert abs(max_amount - expected_amount) < 0.01
    
    def test_invalid_ebitda_negative(self):
        """Test that negative EBITDA raises ValueError."""
        with pytest.raises(ValueError, match="EBITDA must be non-negative"):
            self.calculator.calculate_max_loan_amount(
                ebitda=-100000,
                collateral_value=1000000,
                dscr=1.5,
            )
    
    def test_invalid_collateral_zero(self):
        """Test that zero collateral raises ValueError."""
        with pytest.raises(ValueError, match="Collateral value must be positive"):
            self.calculator.calculate_max_loan_amount(
                ebitda=1000000,
                collateral_value=0,
                dscr=1.5,
            )
    
    def test_invalid_dscr_negative(self):
        """Test that negative DSCR raises ValueError."""
        with pytest.raises(ValueError, match="DSCR must be non-negative"):
            self.calculator.calculate_max_loan_amount(
                ebitda=1000000,
                collateral_value=1000000,
                dscr=-0.5,
            )


class TestLoanCalculatorInterestRate:
    """Tests for determine_interest_rate method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = LoanCalculator()
    
    def test_high_risk_premium(self):
        """Test high risk (score < 40) gets 5%+ premium."""
        base_rate = 8.0
        risk_score = 30
        
        interest_rate, risk_premium, classification = self.calculator.determine_interest_rate(
            base_rate=base_rate,
            risk_score=risk_score,
        )
        
        assert risk_premium >= 5.0
        assert classification == "high"
        assert interest_rate == base_rate + risk_premium
    
    def test_medium_risk_premium(self):
        """Test medium risk (40-70) gets 2-5% premium."""
        base_rate = 8.0
        risk_score = 55
        
        interest_rate, risk_premium, classification = self.calculator.determine_interest_rate(
            base_rate=base_rate,
            risk_score=risk_score,
        )
        
        assert 2.0 <= risk_premium <= 5.0
        assert classification == "medium"
        assert interest_rate == base_rate + risk_premium
    
    def test_low_risk_premium(self):
        """Test low risk (score > 70) gets 0-2% premium."""
        base_rate = 8.0
        risk_score = 80
        
        interest_rate, risk_premium, classification = self.calculator.determine_interest_rate(
            base_rate=base_rate,
            risk_score=risk_score,
        )
        
        assert 0.0 <= risk_premium <= 2.0
        assert classification == "low"
        assert interest_rate == base_rate + risk_premium
    
    def test_boundary_risk_score_40(self):
        """Test boundary at risk score 40."""
        base_rate = 8.0
        risk_score = 40
        
        interest_rate, risk_premium, classification = self.calculator.determine_interest_rate(
            base_rate=base_rate,
            risk_score=risk_score,
        )
        
        assert classification == "medium"
        assert 2.0 <= risk_premium <= 5.0
    
    def test_boundary_risk_score_70(self):
        """Test boundary at risk score 70."""
        base_rate = 8.0
        risk_score = 70
        
        interest_rate, risk_premium, classification = self.calculator.determine_interest_rate(
            base_rate=base_rate,
            risk_score=risk_score,
        )
        
        assert classification == "low"
        assert 0.0 <= risk_premium <= 2.0
    
    def test_extreme_high_risk(self):
        """Test extreme high risk (score 0)."""
        base_rate = 8.0
        risk_score = 0
        
        interest_rate, risk_premium, classification = self.calculator.determine_interest_rate(
            base_rate=base_rate,
            risk_score=risk_score,
        )
        
        assert classification == "high"
        assert risk_premium >= 5.0
    
    def test_extreme_low_risk(self):
        """Test extreme low risk (score 100)."""
        base_rate = 8.0
        risk_score = 100
        
        interest_rate, risk_premium, classification = self.calculator.determine_interest_rate(
            base_rate=base_rate,
            risk_score=risk_score,
        )
        
        assert classification == "low"
        assert 0.0 <= risk_premium <= 2.0
    
    def test_invalid_base_rate_negative(self):
        """Test that negative base rate raises ValueError."""
        with pytest.raises(ValueError, match="Base rate must be non-negative"):
            self.calculator.determine_interest_rate(
                base_rate=-1.0,
                risk_score=50,
            )
    
    def test_invalid_risk_score_below_zero(self):
        """Test that risk score below 0 raises ValueError."""
        with pytest.raises(ValueError, match="Risk score must be between 0 and 100"):
            self.calculator.determine_interest_rate(
                base_rate=8.0,
                risk_score=-10,
            )
    
    def test_invalid_risk_score_above_100(self):
        """Test that risk score above 100 raises ValueError."""
        with pytest.raises(ValueError, match="Risk score must be between 0 and 100"):
            self.calculator.determine_interest_rate(
                base_rate=8.0,
                risk_score=110,
            )


class TestLoanCalculatorExplanations:
    """Tests for explanation generation methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = LoanCalculator()
    
    def test_loan_explanation_generation(self):
        """Test loan amount explanation generation."""
        ebitda = 1000000
        collateral_value = 5000000
        dscr = 1.5
        
        max_amount, breakdown = self.calculator.calculate_max_loan_amount(
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        explanation = self.calculator.generate_loan_explanation(
            breakdown=breakdown,
            ebitda=ebitda,
            collateral_value=collateral_value,
            dscr=dscr,
        )
        
        assert explanation.summary
        assert len(explanation.key_factors) > 0
        assert len(explanation.data_sources) > 0
        assert explanation.reasoning
    
    def test_rate_explanation_generation(self):
        """Test interest rate explanation generation."""
        interest_rate = 10.5
        base_rate = 8.0
        risk_premium = 2.5
        risk_classification = "medium"
        risk_score = 55
        
        explanation = self.calculator.generate_rate_explanation(
            interest_rate=interest_rate,
            base_rate=base_rate,
            risk_premium=risk_premium,
            risk_classification=risk_classification,
            risk_score=risk_score,
        )
        
        assert explanation.summary
        assert len(explanation.key_factors) > 0
        assert len(explanation.data_sources) > 0
        assert explanation.reasoning
        assert str(interest_rate) in explanation.summary
