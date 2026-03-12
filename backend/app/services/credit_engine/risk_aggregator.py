"""Risk aggregation and scoring module for Intelli-Credit system."""

from typing import Dict
from app.models.credit_assessment import FiveCsScores, RiskScore


class RiskAggregator:
    """Aggregates Five Cs scores into composite risk score and classification."""

    def calculate_composite_risk_score(
        self, five_cs: FiveCsScores, weights: Dict[str, float]
    ) -> RiskScore:
        """
        Calculate composite risk score from Five Cs using weighted aggregation.
        
        Requirements: 10.1, 10.2
        
        The composite risk score is calculated as a weighted sum of the five individual
        component scores (Character, Capacity, Capital, Collateral, Conditions).
        
        Args:
            five_cs: FiveCsScores object containing all five component scores
            weights: Dictionary with keys 'character', 'capacity', 'capital', 'collateral', 'conditions'
                    and float values representing the weight for each component.
                    Weights should sum to 1.0 for normalized scoring.
        
        Returns:
            RiskScore object with overall_score (0-100), risk_level classification,
            and lists of top risk and positive factors.
        
        Raises:
            ValueError: If weights dictionary is missing required keys or weights don't sum to 1.0
        
        Example:
            >>> five_cs = FiveCsScores(
            ...     character=CharacterScore(score=75, ...),
            ...     capacity=CapacityScore(score=80, ...),
            ...     capital=CapitalScore(score=70, ...),
            ...     collateral=CollateralScore(score=85, ...),
            ...     conditions=ConditionsScore(score=65, ...)
            ... )
            >>> weights = {
            ...     'character': 0.25,
            ...     'capacity': 0.25,
            ...     'capital': 0.20,
            ...     'collateral': 0.20,
            ...     'conditions': 0.10
            ... }
            >>> aggregator = RiskAggregator()
            >>> risk_score = aggregator.calculate_composite_risk_score(five_cs, weights)
            >>> print(risk_score.overall_score)  # Should be 75.5
            >>> print(risk_score.risk_level)  # Should be "low"
        """
        # Validate weights dictionary
        required_keys = {'character', 'capacity', 'capital', 'collateral', 'conditions'}
        provided_keys = set(weights.keys())
        
        if not required_keys.issubset(provided_keys):
            missing_keys = required_keys - provided_keys
            raise ValueError(f"Missing required weight keys: {missing_keys}")
        
        # Validate that weights sum to approximately 1.0 (allow small floating point error)
        total_weight = sum(weights.values())
        if not (0.99 <= total_weight <= 1.01):
            raise ValueError(
                f"Weights must sum to 1.0, but sum to {total_weight}. "
                f"Provided weights: {weights}"
            )
        
        # Requirement 10.2: Calculate weighted sum of Five Cs scores
        # Requirement 10.1: Result must be 0-100
        composite_score = (
            five_cs.character.score * weights['character'] +
            five_cs.capacity.score * weights['capacity'] +
            five_cs.capital.score * weights['capital'] +
            five_cs.collateral.score * weights['collateral'] +
            five_cs.conditions.score * weights['conditions']
        )
        
        # Ensure score is within valid range (0-100)
        composite_score = max(0.0, min(100.0, composite_score))
        
        # Classify risk level
        risk_level = self.classify_risk_level(composite_score)
        
        # Identify top risk and positive factors
        top_risk_factors = self._extract_top_risk_factors(five_cs)
        top_positive_factors = self._extract_top_positive_factors(five_cs)
        
        return RiskScore(
            overall_score=composite_score,
            risk_level=risk_level,
            top_risk_factors=top_risk_factors,
            top_positive_factors=top_positive_factors,
        )

    def classify_risk_level(self, risk_score: float) -> str:
        """
        Classify risk level based on composite risk score.
        
        Requirements: 10.3, 10.4, 10.5
        
        Classification thresholds:
        - risk_score < 40: "high" risk
        - 40 <= risk_score <= 70: "medium" risk
        - risk_score > 70: "low" risk
        
        Args:
            risk_score: Composite risk score (0-100)
        
        Returns:
            String classification: "high", "medium", or "low"
        
        Raises:
            ValueError: If risk_score is outside 0-100 range
        
        Example:
            >>> aggregator = RiskAggregator()
            >>> aggregator.classify_risk_level(35)  # Returns "high"
            >>> aggregator.classify_risk_level(55)  # Returns "medium"
            >>> aggregator.classify_risk_level(75)  # Returns "low"
        """
        # Validate input
        if not (0.0 <= risk_score <= 100.0):
            raise ValueError(
                f"Risk score must be between 0 and 100, got {risk_score}"
            )
        
        # Requirement 10.3: risk_score < 40 → high risk
        if risk_score < 40:
            return "high"
        # Requirement 10.4: 40 <= risk_score <= 70 → medium risk
        elif risk_score <= 70:
            return "medium"
        # Requirement 10.5: risk_score > 70 → low risk
        else:
            return "low"

    def _extract_top_risk_factors(self, five_cs: FiveCsScores) -> list[str]:
        """
        Extract top risk factors from Five Cs scores.
        
        Identifies the components with lowest scores and their associated risk factors.
        
        Args:
            five_cs: FiveCsScores object containing all five component scores
        
        Returns:
            List of risk factor strings, prioritized by component score (lowest first)
        """
        # Create list of (component_name, score, factors) tuples
        components = [
            ("Character", five_cs.character.score, five_cs.character.negative_factors),
            ("Capacity", five_cs.capacity.score, []),  # Capacity doesn't have negative_factors
            ("Capital", five_cs.capital.score, []),  # Capital doesn't have negative_factors
            ("Collateral", five_cs.collateral.score, []),  # Collateral doesn't have negative_factors
            ("Conditions", five_cs.conditions.score, five_cs.conditions.risk_factors),
        ]
        
        # Sort by score (lowest first) to identify weakest components
        sorted_components = sorted(components, key=lambda x: x[1])
        
        # Collect risk factors from lowest-scoring components
        risk_factors = []
        
        for component_name, score, factors in sorted_components:
            if factors:
                # Add specific factors from the component
                risk_factors.extend(factors)
            else:
                # If no specific factors, add a generic factor based on score
                if score < 40:
                    risk_factors.append(f"Low {component_name} score: {score:.1f}")
                elif score < 60:
                    risk_factors.append(f"Weak {component_name} score: {score:.1f}")
            
            # Stop after collecting enough factors
            if len(risk_factors) >= 3:
                break
        
        # Return top 3 factors
        return risk_factors[:3]

    def _extract_top_positive_factors(self, five_cs: FiveCsScores) -> list[str]:
        """
        Extract top positive factors from Five Cs scores.
        
        Identifies the components with highest scores as positive indicators.
        
        Args:
            five_cs: FiveCsScores object containing all five component scores
        
        Returns:
            List of positive factor strings, prioritized by component score (highest first)
        """
        # Create list of (component_name, score) tuples
        components = [
            ("Character", five_cs.character.score),
            ("Capacity", five_cs.capacity.score),
            ("Capital", five_cs.capital.score),
            ("Collateral", five_cs.collateral.score),
            ("Conditions", five_cs.conditions.score),
        ]
        
        # Sort by score (highest first) to identify strongest components
        sorted_components = sorted(components, key=lambda x: x[1], reverse=True)
        
        # Collect positive factors from highest-scoring components
        positive_factors = []
        
        for component_name, score in sorted_components:
            if score >= 80:
                positive_factors.append(f"Strong {component_name} score: {score:.1f}")
            elif score >= 60:
                positive_factors.append(f"Good {component_name} score: {score:.1f}")
            
            # Stop after collecting enough factors
            if len(positive_factors) >= 3:
                break
        
        # Return top 3 factors
        return positive_factors[:3]
