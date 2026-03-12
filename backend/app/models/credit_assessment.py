"""Credit assessment and Five Cs scoring models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple, Dict


@dataclass
class CharacterScore:
    """Character assessment (promoter credibility)."""
    score: float  # 0-100
    litigation_count: int
    governance_rating: str
    credit_bureau_score: float
    negative_factors: List[str] = field(default_factory=list)


@dataclass
class CapacityScore:
    """Capacity assessment (ability to repay)."""
    score: float  # 0-100
    dscr: float
    cash_flow: float
    debt_service: float
    trend: str  # "improving", "stable", "declining"


@dataclass
class CapitalScore:
    """Capital assessment (equity strength)."""
    score: float  # 0-100
    debt_equity_ratio: float
    net_worth: float
    net_worth_trend: str


@dataclass
class CollateralScore:
    """Collateral assessment (security adequacy)."""
    score: float  # 0-100
    ltv: float
    collateral_type: str
    valuation_date: datetime


@dataclass
class ConditionsScore:
    """Conditions assessment (external risk factors)."""
    score: float  # 0-100
    sector_risk: str
    regulatory_risk: str
    commodity_risk: str
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class FiveCsScores:
    """Aggregated Five Cs assessment."""
    character: CharacterScore
    capacity: CapacityScore
    capital: CapitalScore
    collateral: CollateralScore
    conditions: ConditionsScore


@dataclass
class RiskScore:
    """Overall risk assessment."""
    overall_score: float  # 0-100
    risk_level: str  # "high", "medium", "low"
    top_risk_factors: List[str] = field(default_factory=list)
    top_positive_factors: List[str] = field(default_factory=list)


@dataclass
class Explanation:
    """Explainability information for a decision."""
    summary: str
    key_factors: List[Tuple[str, float]] = field(default_factory=list)  # (factor_name, contribution)
    data_sources: List[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class LoanRecommendation:
    """Final loan recommendation with explanations."""
    max_loan_amount: float
    recommended_interest_rate: float
    risk_score: RiskScore
    limiting_constraint: str
    explanations: Dict[str, Explanation] = field(default_factory=dict)
