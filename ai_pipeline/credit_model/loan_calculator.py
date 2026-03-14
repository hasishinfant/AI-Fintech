"""Loan amount calculation and interest rate determination."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from app.models.financial import FinancialData, Asset
from app.models.credit_assessment import Explanation


@dataclass
class LoanCalculationBreakdown:
    """Detailed breakdown of loan amount calculation."""
    ebitda_based_amount: float
    collateral_based_cap: float
    dscr_based_reduction: float
    final_amount: float
    limiting_constraint: str
    constraints_applied: Dict[str, float] = field(default_factory=dict)
    calculation_steps: List[str] = field(default_factory=list)


class LoanCalculator:
    """Calculates maximum loan amount and determines interest rates."""
    
    # Constants for loan calculation
    EBITDA_MULTIPLIER = 0.4  # 0.4 × EBITDA
    COLLATERAL_CAP_PERCENTAGE = 0.75  # 75% of collateral value
    DSCR_THRESHOLD = 1.25  # DSCR below this triggers reduction
    
    def __init__(self):
        """Initialize the LoanCalculator."""
        pass
    
    def calculate_max_loan_amount(
        self,
        ebitda: float,
        collateral_value: float,
        dscr: float,
        cash_flow: Optional[float] = None,
        debt_service: Optional[float] = None,
    ) -> Tuple[float, LoanCalculationBreakdown]:
        """
        Calculate maximum recommended loan amount.
        
        Applies three constraints in order:
        1. EBITDA-based: 0.4 × EBITDA
        2. Collateral-based: 75% of collateral value
        3. DSCR-based: Reduction if DSCR < 1.25
        
        Returns the most conservative (lowest) amount.
        
        Requirement 11.1: Calculate maximum loan amount as 0.4 × EBITDA
        Requirement 11.2: Cap at 75% of collateral value if lower
        Requirement 11.3: Reduce proportionally if DSCR < 1.25
        Requirement 11.4: Provide calculation breakdown
        Requirement 11.5: Apply most conservative constraint
        
        Args:
            ebitda: EBITDA value (positive)
            collateral_value: Total collateral value (positive)
            dscr: Debt Service Coverage Ratio
            cash_flow: Operating cash flow (optional, for DSCR validation)
            debt_service: Total debt service (optional, for DSCR validation)
            
        Returns:
            Tuple of (max_loan_amount, breakdown)
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if ebitda < 0:
            raise ValueError("EBITDA must be non-negative")
        if collateral_value <= 0:
            raise ValueError("Collateral value must be positive")
        if dscr < 0:
            raise ValueError("DSCR must be non-negative")
        
        breakdown = LoanCalculationBreakdown(
            ebitda_based_amount=0.0,
            collateral_based_cap=0.0,
            dscr_based_reduction=0.0,
            final_amount=0.0,
            limiting_constraint="",
            constraints_applied={},
            calculation_steps=[],
        )
        
        # Step 1: Calculate EBITDA-based amount
        ebitda_based = ebitda * self.EBITDA_MULTIPLIER
        breakdown.ebitda_based_amount = ebitda_based
        breakdown.constraints_applied["ebitda_based"] = ebitda_based
        breakdown.calculation_steps.append(
            f"EBITDA-based amount: {ebitda} × {self.EBITDA_MULTIPLIER} = {ebitda_based:.2f}"
        )
        
        # Step 2: Calculate collateral-based cap
        collateral_cap = collateral_value * self.COLLATERAL_CAP_PERCENTAGE
        breakdown.collateral_based_cap = collateral_cap
        breakdown.constraints_applied["collateral_cap"] = collateral_cap
        breakdown.calculation_steps.append(
            f"Collateral-based cap: {collateral_value} × {self.COLLATERAL_CAP_PERCENTAGE} = {collateral_cap:.2f}"
        )
        
        # Step 3: Apply collateral cap (most conservative so far)
        amount_after_collateral = min(ebitda_based, collateral_cap)
        breakdown.calculation_steps.append(
            f"After collateral cap: min({ebitda_based:.2f}, {collateral_cap:.2f}) = {amount_after_collateral:.2f}"
        )
        
        # Step 4: Apply DSCR-based reduction if DSCR < 1.25
        dscr_reduction_factor = 1.0
        if dscr < self.DSCR_THRESHOLD and dscr > 0:
            # Reduce proportionally: reduction_factor = DSCR / DSCR_THRESHOLD
            dscr_reduction_factor = dscr / self.DSCR_THRESHOLD
            breakdown.dscr_based_reduction = dscr_reduction_factor
            breakdown.constraints_applied["dscr_reduction_factor"] = dscr_reduction_factor
            breakdown.calculation_steps.append(
                f"DSCR {dscr:.2f} < {self.DSCR_THRESHOLD}: Apply reduction factor {dscr_reduction_factor:.4f}"
            )
        else:
            breakdown.dscr_based_reduction = 1.0
            breakdown.constraints_applied["dscr_reduction_factor"] = 1.0
            breakdown.calculation_steps.append(
                f"DSCR {dscr:.2f} >= {self.DSCR_THRESHOLD}: No reduction applied"
            )
        
        # Step 5: Apply DSCR reduction
        final_amount = amount_after_collateral * dscr_reduction_factor
        breakdown.final_amount = final_amount
        breakdown.calculation_steps.append(
            f"After DSCR reduction: {amount_after_collateral:.2f} × {dscr_reduction_factor:.4f} = {final_amount:.2f}"
        )
        
        # Step 6: Determine limiting constraint
        limiting_constraint = self._determine_limiting_constraint(
            ebitda_based, collateral_cap, dscr_reduction_factor
        )
        breakdown.limiting_constraint = limiting_constraint
        breakdown.calculation_steps.append(
            f"Limiting constraint: {limiting_constraint}"
        )
        
        return final_amount, breakdown
    
    def _determine_limiting_constraint(
        self,
        ebitda_based: float,
        collateral_cap: float,
        dscr_reduction_factor: float,
    ) -> str:
        """
        Determine which constraint is the limiting factor.
        
        Requirement 11.5: Identify the most conservative constraint
        
        Args:
            ebitda_based: EBITDA-based loan amount
            collateral_cap: Collateral-based cap
            dscr_reduction_factor: DSCR reduction factor (1.0 if no reduction)
            
        Returns:
            String describing the limiting constraint
        """
        constraints = []
        
        # Check which constraint is most restrictive
        if collateral_cap < ebitda_based:
            constraints.append(("collateral_cap", collateral_cap))
        else:
            constraints.append(("ebitda_based", ebitda_based))
        
        if dscr_reduction_factor < 1.0:
            constraints.append(("dscr_reduction", dscr_reduction_factor))
        
        if not constraints:
            return "EBITDA-based calculation"
        
        # Find the most restrictive constraint
        if len(constraints) == 1:
            constraint_name, _ = constraints[0]
            if constraint_name == "collateral_cap":
                return "Collateral value (75% cap)"
            elif constraint_name == "ebitda_based":
                return "EBITDA-based calculation (0.4 × EBITDA)"
            elif constraint_name == "dscr_reduction":
                return "Low DSCR (below 1.25)"
        else:
            # Multiple constraints - determine which is most restrictive
            if dscr_reduction_factor < 1.0:
                return "Low DSCR (below 1.25)"
            elif collateral_cap < ebitda_based:
                return "Collateral value (75% cap)"
            else:
                return "EBITDA-based calculation (0.4 × EBITDA)"
    
    def determine_interest_rate(
        self,
        base_rate: float,
        risk_score: float,
    ) -> Tuple[float, float, str]:
        """
        Determine interest rate based on risk score.
        
        Risk premium tiers:
        - High risk (score < 40): 5%+ premium
        - Medium risk (40-70): 2-5% premium
        - Low risk (score > 70): 0-2% premium
        
        Requirement 12.1: Interest rate = base rate + risk premium
        Requirement 12.2: High risk (< 40) = 5%+ premium
        Requirement 12.3: Medium risk (40-70) = 2-5% premium
        Requirement 12.4: Low risk (> 70) = 0-2% premium
        Requirement 12.5: Document rate components
        
        Args:
            base_rate: Base interest rate (e.g., 8.5)
            risk_score: Overall risk score (0-100)
            
        Returns:
            Tuple of (interest_rate, risk_premium, risk_classification)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if base_rate < 0:
            raise ValueError("Base rate must be non-negative")
        if not (0 <= risk_score <= 100):
            raise ValueError("Risk score must be between 0 and 100")
        
        # Determine risk premium based on score
        if risk_score < 40:
            # High risk: 5%+ premium
            # Scale from 5% to 8% as score goes from 40 to 0
            risk_premium = 5.0 + (40 - risk_score) * (3.0 / 40)
            risk_classification = "high"
        elif risk_score < 70:
            # Medium risk: 2-5% premium
            # Scale from 5% to 2% as score goes from 40 to 70
            risk_premium = 5.0 - (risk_score - 40) * (3.0 / 30)
            risk_classification = "medium"
        else:
            # Low risk: 0-2% premium
            # Scale from 2% to 0% as score goes from 70 to 100
            risk_premium = 2.0 - (risk_score - 70) * (2.0 / 30)
            risk_classification = "low"
        
        # Ensure premium is within bounds
        risk_premium = max(0.0, min(risk_premium, 8.0))
        
        interest_rate = base_rate + risk_premium
        
        return interest_rate, risk_premium, risk_classification
    
    def generate_loan_explanation(
        self,
        breakdown: LoanCalculationBreakdown,
        ebitda: float,
        collateral_value: float,
        dscr: float,
    ) -> Explanation:
        """
        Generate explanation for loan amount calculation.
        
        Requirement 13.3: Explain which constraint was limiting
        Requirement 13.4: Provide calculation breakdown
        Requirement 13.5: Cite data sources
        
        Args:
            breakdown: LoanCalculationBreakdown object
            ebitda: EBITDA value used
            collateral_value: Collateral value used
            dscr: DSCR value used
            
        Returns:
            Explanation object with reasoning and key factors
        """
        summary = (
            f"Maximum loan amount of {breakdown.final_amount:,.2f} determined by "
            f"{breakdown.limiting_constraint}. "
            f"EBITDA-based calculation: {breakdown.ebitda_based_amount:,.2f}, "
            f"Collateral cap: {breakdown.collateral_based_cap:,.2f}, "
            f"DSCR reduction factor: {breakdown.dscr_based_reduction:.4f}."
        )
        
        key_factors = [
            ("EBITDA-based amount (0.4 × EBITDA)", breakdown.ebitda_based_amount),
            ("Collateral-based cap (75% of value)", breakdown.collateral_based_cap),
            ("DSCR reduction factor", breakdown.dscr_based_reduction * 100),
        ]
        
        reasoning = "\n".join(breakdown.calculation_steps)
        
        return Explanation(
            summary=summary,
            key_factors=key_factors,
            data_sources=[
                "Financial Data: EBITDA",
                "Collateral Data: Asset Valuation",
                "Capacity Analysis: DSCR",
            ],
            reasoning=reasoning,
        )
    
    def generate_rate_explanation(
        self,
        interest_rate: float,
        base_rate: float,
        risk_premium: float,
        risk_classification: str,
        risk_score: float,
    ) -> Explanation:
        """
        Generate explanation for interest rate determination.
        
        Requirement 13.4: Explain interest rate components
        Requirement 13.5: Cite data sources
        
        Args:
            interest_rate: Final interest rate
            base_rate: Base rate component
            risk_premium: Risk premium component
            risk_classification: Risk level classification
            risk_score: Overall risk score
            
        Returns:
            Explanation object with rate components
        """
        summary = (
            f"Interest rate of {interest_rate:.2f}% determined as base rate "
            f"{base_rate:.2f}% plus {risk_classification} risk premium {risk_premium:.2f}% "
            f"(based on risk score {risk_score:.1f}/100)."
        )
        
        key_factors = [
            ("Base rate", base_rate),
            ("Risk premium", risk_premium),
            ("Risk classification", 0),  # Placeholder for classification
        ]
        
        reasoning = (
            f"Risk score {risk_score:.1f} falls in {risk_classification} risk category. "
            f"Applied {risk_premium:.2f}% premium to base rate {base_rate:.2f}% "
            f"resulting in {interest_rate:.2f}% final rate."
        )
        
        return Explanation(
            summary=summary,
            key_factors=key_factors,
            data_sources=[
                "Risk Assessment: Overall Risk Score",
                "Market Data: Base Rate",
            ],
            reasoning=reasoning,
        )
