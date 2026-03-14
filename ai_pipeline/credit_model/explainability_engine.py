"""Explainability engine for credit decisions using SHAP values and constraint analysis."""

from typing import Dict, List, Tuple, Optional
import numpy as np
from app.models.credit_assessment import (
    FiveCsScores,
    RiskScore,
    Explanation,
    LoanRecommendation,
)


class ExplainabilityEngine:
    """
    Generates explainable recommendations for credit decisions.
    
    Provides interpretable explanations for:
    - Risk scores (using SHAP-like feature importance)
    - Loan amounts (identifying limiting constraints)
    - Interest rates (documenting risk factors)
    
    All explanations include source citations for data points.
    
    Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
    """

    def explain_risk_score(
        self,
        risk_score: RiskScore,
        five_cs: FiveCsScores,
        base_weights: Optional[Dict[str, float]] = None,
    ) -> Explanation:
        """
        Generate explanation for risk score using SHAP-like feature importance.
        
        Requirement 13.1: Provide explanations for each component of the decision
        Requirement 13.2: Identify the top three factors contributing to the score
        Requirement 13.5: Cite specific data points and their sources
        
        Uses a simplified SHAP-like approach to calculate feature importance:
        - Each Five Cs component contributes to the overall risk score
        - Contribution = component_score * weight
        - Factors are ranked by absolute contribution magnitude
        
        Args:
            risk_score: RiskScore object with overall_score and risk_level
            five_cs: FiveCsScores object with all five component scores
            base_weights: Optional weights for each component. Defaults to equal weights.
        
        Returns:
            Explanation object with:
            - summary: High-level explanation of the risk score
            - key_factors: List of (factor_name, contribution_percentage) tuples
            - data_sources: List of source citations
            - reasoning: Detailed reasoning about the score
        
        Example:
            >>> risk_score = RiskScore(overall_score=65, risk_level="medium", ...)
            >>> five_cs = FiveCsScores(...)
            >>> engine = ExplainabilityEngine()
            >>> explanation = engine.explain_risk_score(risk_score, five_cs)
            >>> print(explanation.summary)
            >>> for factor, contribution in explanation.key_factors:
            ...     print(f"{factor}: {contribution:.1f}%")
        """
        # Default equal weights if not provided
        if base_weights is None:
            base_weights = {
                "character": 0.20,
                "capacity": 0.20,
                "capital": 0.20,
                "collateral": 0.20,
                "conditions": 0.20,
            }

        # Calculate SHAP-like feature importance for each component
        # Contribution = (component_score / 100) * weight * 100
        component_contributions = {
            "Character": (five_cs.character.score / 100.0) * base_weights["character"] * 100,
            "Capacity": (five_cs.capacity.score / 100.0) * base_weights["capacity"] * 100,
            "Capital": (five_cs.capital.score / 100.0) * base_weights["capital"] * 100,
            "Collateral": (five_cs.collateral.score / 100.0) * base_weights["collateral"] * 100,
            "Conditions": (five_cs.conditions.score / 100.0) * base_weights["conditions"] * 100,
        }

        # Sort by absolute contribution (descending)
        sorted_contributions = sorted(
            component_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        # Extract top 3 factors
        top_factors = sorted_contributions[:3]
        key_factors: List[Tuple[str, float]] = [
            (name, contribution) for name, contribution in top_factors
        ]

        # Generate summary
        risk_level_description = {
            "high": "high risk",
            "medium": "medium risk",
            "low": "low risk",
        }.get(risk_score.risk_level, "unknown risk")

        summary = (
            f"Overall risk score of {risk_score.overall_score:.1f} indicates {risk_level_description}. "
            f"The score is primarily driven by {key_factors[0][0]} "
            f"({five_cs.__dict__[key_factors[0][0].lower()].score:.1f}/100), "
            f"{key_factors[1][0]} ({five_cs.__dict__[key_factors[1][0].lower()].score:.1f}/100), "
            f"and {key_factors[2][0]} ({five_cs.__dict__[key_factors[2][0].lower()].score:.1f}/100)."
        )

        # Collect data sources
        data_sources = self._collect_risk_score_sources(five_cs)

        # Generate detailed reasoning
        reasoning = self._generate_risk_score_reasoning(five_cs, risk_score.risk_level)

        return Explanation(
            summary=summary,
            key_factors=key_factors,
            data_sources=data_sources,
            reasoning=reasoning,
        )

    def explain_loan_amount(
        self,
        loan_amount: float,
        constraints: Dict[str, float],
        limiting_constraint: str,
        ebitda: Optional[float] = None,
        collateral_value: Optional[float] = None,
        dscr: Optional[float] = None,
    ) -> Explanation:
        """
        Generate explanation for loan amount with constraint identification.
        
        Requirement 13.3: Show which constraint was the limiting factor
        Requirement 13.4: Document the calculation methodology
        Requirement 13.5: Cite specific data points and their sources
        
        Identifies which constraint (EBITDA-based, collateral-based, or DSCR-based)
        limited the final loan amount recommendation.
        
        Args:
            loan_amount: Final recommended loan amount
            constraints: Dict with constraint names and their calculated limits:
                - "ebitda_based": 0.4 * EBITDA
                - "collateral_based": 0.75 * collateral_value
                - "dscr_based": DSCR-adjusted amount
            limiting_constraint: Name of the constraint that limited the amount
            ebitda: EBITDA value (optional, for source citation)
            collateral_value: Collateral value (optional, for source citation)
            dscr: DSCR value (optional, for source citation)
        
        Returns:
            Explanation object with:
            - summary: High-level explanation of the loan amount
            - key_factors: List of (constraint_name, amount) tuples
            - data_sources: List of source citations
            - reasoning: Detailed reasoning about the limiting constraint
        
        Example:
            >>> constraints = {
            ...     "ebitda_based": 50_000_000,
            ...     "collateral_based": 30_000_000,
            ...     "dscr_based": 40_000_000,
            ... }
            >>> engine = ExplainabilityEngine()
            >>> explanation = engine.explain_loan_amount(
            ...     loan_amount=30_000_000,
            ...     constraints=constraints,
            ...     limiting_constraint="collateral_based",
            ...     collateral_value=40_000_000,
            ... )
            >>> print(explanation.summary)
        """
        # Create key factors list showing all constraints
        key_factors: List[Tuple[str, float]] = [
            (name, amount) for name, amount in constraints.items()
        ]

        # Sort by amount (descending) to show hierarchy
        key_factors.sort(key=lambda x: x[1], reverse=True)

        # Generate summary
        limiting_constraint_display = limiting_constraint.replace("_", " ").title()
        summary = (
            f"Maximum recommended loan amount is ₹{loan_amount:,.0f}. "
            f"This is limited by {limiting_constraint_display} constraint "
            f"(₹{constraints[limiting_constraint]:,.0f}), which is the most conservative of the three constraints."
        )

        # Generate detailed reasoning
        reasoning = self._generate_loan_amount_reasoning(
            constraints, limiting_constraint, ebitda, collateral_value, dscr
        )

        # Collect data sources
        data_sources = self._collect_loan_amount_sources(
            ebitda, collateral_value, dscr
        )

        return Explanation(
            summary=summary,
            key_factors=key_factors,
            data_sources=data_sources,
            reasoning=reasoning,
        )

    def explain_interest_rate(
        self,
        base_rate: float,
        risk_premium: float,
        final_rate: float,
        risk_score: RiskScore,
        risk_factors: List[str],
    ) -> Explanation:
        """
        Generate explanation for interest rate with risk factor documentation.
        
        Requirement 13.4: Document which risk factors drove the premium
        Requirement 13.5: Cite specific data points and their sources
        
        Explains how the interest rate was determined from base rate and risk premium,
        and which risk factors contributed to the premium.
        
        Args:
            base_rate: Base interest rate (e.g., 8.5%)
            risk_premium: Risk premium applied (e.g., 2.5%)
            final_rate: Final recommended interest rate (base_rate + risk_premium)
            risk_score: RiskScore object with risk_level and top_risk_factors
            risk_factors: List of specific risk factors that drove the premium
        
        Returns:
            Explanation object with:
            - summary: High-level explanation of the interest rate
            - key_factors: List of (factor_name, contribution) tuples
            - data_sources: List of source citations
            - reasoning: Detailed reasoning about the rate components
        
        Example:
            >>> risk_score = RiskScore(overall_score=45, risk_level="medium", ...)
            >>> engine = ExplainabilityEngine()
            >>> explanation = engine.explain_interest_rate(
            ...     base_rate=8.5,
            ...     risk_premium=2.5,
            ...     final_rate=11.0,
            ...     risk_score=risk_score,
            ...     risk_factors=["Low DSCR", "High Debt-to-Equity"],
            ... )
            >>> print(explanation.summary)
        """
        # Create key factors showing rate components
        key_factors: List[Tuple[str, float]] = [
            ("Base Rate", base_rate),
            ("Risk Premium", risk_premium),
        ]

        # Generate summary
        premium_tier = self._classify_premium_tier(risk_score.risk_level)
        summary = (
            f"Recommended interest rate is {final_rate:.2f}% "
            f"({base_rate:.2f}% base rate + {risk_premium:.2f}% risk premium). "
            f"The {premium_tier} risk premium reflects the {risk_score.risk_level} risk classification."
        )

        # Generate detailed reasoning
        reasoning = self._generate_interest_rate_reasoning(
            base_rate, risk_premium, risk_score, risk_factors
        )

        # Collect data sources
        data_sources = self._collect_interest_rate_sources(risk_score)

        return Explanation(
            summary=summary,
            key_factors=key_factors,
            data_sources=data_sources,
            reasoning=reasoning,
        )

    # Helper methods for source citation and reasoning

    def _collect_risk_score_sources(self, five_cs: FiveCsScores) -> List[str]:
        """Collect data sources for risk score explanation."""
        sources = [
            "Character Score: Litigation history (e-Courts), Governance records (MCA), Credit bureau (CIBIL)",
            f"Capacity Score: DSCR calculation (Cash flow: ₹{five_cs.capacity.cash_flow:,.0f}, "
            f"Debt service: ₹{five_cs.capacity.debt_service:,.0f})",
            f"Capital Score: Debt-to-Equity ratio ({five_cs.capital.debt_equity_ratio:.2f}), "
            f"Net worth: ₹{five_cs.capital.net_worth:,.0f}",
            f"Collateral Score: LTV ratio ({five_cs.collateral.ltv:.2f}), "
            f"Collateral type: {five_cs.collateral.collateral_type}",
            f"Conditions Score: Sector risk ({five_cs.conditions.sector_risk}), "
            f"Regulatory risk ({five_cs.conditions.regulatory_risk})",
        ]
        return sources

    def _collect_loan_amount_sources(
        self,
        ebitda: Optional[float],
        collateral_value: Optional[float],
        dscr: Optional[float],
    ) -> List[str]:
        """Collect data sources for loan amount explanation."""
        sources = []
        if ebitda is not None:
            sources.append(f"EBITDA-based limit: 0.4 × ₹{ebitda:,.0f} = ₹{0.4 * ebitda:,.0f}")
        if collateral_value is not None:
            sources.append(
                f"Collateral-based limit: 0.75 × ₹{collateral_value:,.0f} = ₹{0.75 * collateral_value:,.0f}"
            )
        if dscr is not None:
            sources.append(f"DSCR-based adjustment: DSCR = {dscr:.2f}")
        return sources

    def _collect_interest_rate_sources(self, risk_score: RiskScore) -> List[str]:
        """Collect data sources for interest rate explanation."""
        sources = [
            f"Risk classification: {risk_score.risk_level.upper()} (Score: {risk_score.overall_score:.1f}/100)",
            f"Top risk factors: {', '.join(risk_score.top_risk_factors[:3])}",
            "Premium tiers: High risk (5-7%), Medium risk (2-5%), Low risk (0-2%)",
        ]
        return sources

    def _generate_risk_score_reasoning(
        self, five_cs: FiveCsScores, risk_level: str
    ) -> str:
        """Generate detailed reasoning for risk score."""
        reasoning_parts = []

        # Character analysis
        if five_cs.character.score < 50:
            reasoning_parts.append(
                f"Character score ({five_cs.character.score:.1f}) is concerning due to "
                f"{five_cs.character.litigation_count} litigation cases and weak governance."
            )
        elif five_cs.character.score < 70:
            reasoning_parts.append(
                f"Character score ({five_cs.character.score:.1f}) is moderate with "
                f"{five_cs.character.litigation_count} litigation cases."
            )
        else:
            reasoning_parts.append(
                f"Character score ({five_cs.character.score:.1f}) is strong with "
                f"clean litigation history and good governance."
            )

        # Capacity analysis
        if five_cs.capacity.dscr < 1.25:
            reasoning_parts.append(
                f"Capacity score ({five_cs.capacity.score:.1f}) is weak with DSCR of {five_cs.capacity.dscr:.2f}, "
                f"below the 1.25 threshold for adequate repayment capacity."
            )
        elif five_cs.capacity.dscr < 1.75:
            reasoning_parts.append(
                f"Capacity score ({five_cs.capacity.score:.1f}) is moderate with DSCR of {five_cs.capacity.dscr:.2f}."
            )
        else:
            reasoning_parts.append(
                f"Capacity score ({five_cs.capacity.score:.1f}) is strong with DSCR of {five_cs.capacity.dscr:.2f}."
            )

        # Capital analysis
        if five_cs.capital.debt_equity_ratio > 2.0:
            reasoning_parts.append(
                f"Capital score ({five_cs.capital.score:.1f}) is weak with Debt-to-Equity ratio of "
                f"{five_cs.capital.debt_equity_ratio:.2f}, exceeding the 2.0 threshold."
            )
        elif five_cs.capital.debt_equity_ratio > 1.5:
            reasoning_parts.append(
                f"Capital score ({five_cs.capital.score:.1f}) is moderate with Debt-to-Equity ratio of "
                f"{five_cs.capital.debt_equity_ratio:.2f}."
            )
        else:
            reasoning_parts.append(
                f"Capital score ({five_cs.capital.score:.1f}) is strong with Debt-to-Equity ratio of "
                f"{five_cs.capital.debt_equity_ratio:.2f}."
            )

        # Collateral analysis
        if five_cs.collateral.ltv > 0.75:
            reasoning_parts.append(
                f"Collateral score ({five_cs.collateral.score:.1f}) is weak with LTV of {five_cs.collateral.ltv:.2f}, "
                f"exceeding the 0.75 threshold."
            )
        elif five_cs.collateral.ltv > 0.60:
            reasoning_parts.append(
                f"Collateral score ({five_cs.collateral.score:.1f}) is moderate with LTV of {five_cs.collateral.ltv:.2f}."
            )
        else:
            reasoning_parts.append(
                f"Collateral score ({five_cs.collateral.score:.1f}) is strong with LTV of {five_cs.collateral.ltv:.2f}."
            )

        # Conditions analysis
        if five_cs.conditions.score < 50:
            reasoning_parts.append(
                f"Conditions score ({five_cs.conditions.score:.1f}) is weak due to "
                f"{five_cs.conditions.sector_risk} sector risk and {five_cs.conditions.regulatory_risk} regulatory risk."
            )
        else:
            reasoning_parts.append(
                f"Conditions score ({five_cs.conditions.score:.1f}) reflects "
                f"{five_cs.conditions.sector_risk} sector risk and {five_cs.conditions.regulatory_risk} regulatory risk."
            )

        return " ".join(reasoning_parts)

    def _generate_loan_amount_reasoning(
        self,
        constraints: Dict[str, float],
        limiting_constraint: str,
        ebitda: Optional[float],
        collateral_value: Optional[float],
        dscr: Optional[float],
    ) -> str:
        """Generate detailed reasoning for loan amount."""
        reasoning_parts = []

        # Explain each constraint
        if "ebitda_based" in constraints and ebitda is not None:
            reasoning_parts.append(
                f"EBITDA-based limit: 0.4 × ₹{ebitda:,.0f} = ₹{constraints['ebitda_based']:,.0f}"
            )

        if "collateral_based" in constraints and collateral_value is not None:
            reasoning_parts.append(
                f"Collateral-based limit: 0.75 × ₹{collateral_value:,.0f} = ₹{constraints['collateral_based']:,.0f}"
            )

        if "dscr_based" in constraints and dscr is not None:
            reasoning_parts.append(
                f"DSCR-based limit: Adjusted based on DSCR of {dscr:.2f} = ₹{constraints['dscr_based']:,.0f}"
            )

        # Explain limiting constraint
        limiting_display = limiting_constraint.replace("_", " ").title()
        reasoning_parts.append(
            f"The most conservative constraint is {limiting_display} "
            f"(₹{constraints[limiting_constraint]:,.0f}), which becomes the maximum recommended loan amount."
        )

        return " ".join(reasoning_parts)

    def _generate_interest_rate_reasoning(
        self,
        base_rate: float,
        risk_premium: float,
        risk_score: RiskScore,
        risk_factors: List[str],
    ) -> str:
        """Generate detailed reasoning for interest rate."""
        reasoning_parts = [
            f"Base rate of {base_rate:.2f}% is the market reference rate.",
        ]

        # Explain premium based on risk level
        if risk_score.risk_level == "high":
            reasoning_parts.append(
                f"High risk classification (score: {risk_score.overall_score:.1f}) warrants "
                f"a {risk_premium:.2f}% premium (5-7% range)."
            )
        elif risk_score.risk_level == "medium":
            reasoning_parts.append(
                f"Medium risk classification (score: {risk_score.overall_score:.1f}) warrants "
                f"a {risk_premium:.2f}% premium (2-5% range)."
            )
        else:
            reasoning_parts.append(
                f"Low risk classification (score: {risk_score.overall_score:.1f}) warrants "
                f"a {risk_premium:.2f}% premium (0-2% range)."
            )

        # Explain key risk factors
        if risk_factors:
            reasoning_parts.append(
                f"Key risk factors driving the premium: {', '.join(risk_factors[:3])}."
            )

        return " ".join(reasoning_parts)

    def _classify_premium_tier(self, risk_level: str) -> str:
        """Classify premium tier based on risk level."""
        tier_map = {
            "high": "high (5-7%)",
            "medium": "moderate (2-5%)",
            "low": "low (0-2%)",
        }
        return tier_map.get(risk_level, "standard")
