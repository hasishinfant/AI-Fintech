"""Research and external data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class NewsArticle:
    """News article data from web research."""
    title: str
    source: str
    url: str
    published_date: datetime
    content: str
    sentiment: str  # "positive", "neutral", "negative"


@dataclass
class MCAData:
    """Ministry of Corporate Affairs filing data."""
    cin: str
    company_name: str
    registration_date: datetime
    authorized_capital: float
    paid_up_capital: float
    last_filing_date: datetime
    compliance_status: str
    directors: List[Dict] = field(default_factory=list)


@dataclass
class LegalCase:
    """Legal case information from e-Courts."""
    case_number: str
    court: str
    filing_date: datetime
    case_type: str
    status: str
    summary: str
    parties: List[str] = field(default_factory=list)


@dataclass
class SentimentScore:
    """Aggregated sentiment analysis results."""
    overall: float  # -1 to 1
    positive_count: int
    neutral_count: int
    negative_count: int
    key_themes: List[str] = field(default_factory=list)


@dataclass
class RBINotification:
    """RBI notification or regulatory update."""
    notification_id: str
    title: str
    url: str
    published_date: datetime
    sector: str
    content: str
    summary: str
