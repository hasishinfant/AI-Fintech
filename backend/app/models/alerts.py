"""Alert and detection models."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CircularTradingAlert:
    """Alert for detected circular trading patterns."""
    detected: bool
    severity: str  # "high", "medium", "low"
    discrepancies: List[str] = field(default_factory=list)
    gst_sales: float = 0.0
    bank_deposits: float = 0.0
    mismatch_percentage: float = 0.0
