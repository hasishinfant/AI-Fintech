"""Company and promoter data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Promoter:
    """Company promoter/director information."""
    name: str
    din: str  # Director Identification Number
    shareholding: float
    role: str


@dataclass
class Company:
    """Company master data."""
    company_id: str
    cin: str
    gstin: str
    name: str
    industry: str
    incorporation_date: datetime
    promoters: List[Promoter] = field(default_factory=list)
