"""Domain models for Intelli-Credit system."""

# Financial models
from .financial import (
    FinancialData,
    GSTData,
    Transaction,
    Debt,
    Asset,
)

# Company models
from .company import (
    Company,
    Promoter,
)

# Research models
from .research import (
    NewsArticle,
    MCAData,
    LegalCase,
    SentimentScore,
)

# Credit assessment models
from .credit_assessment import (
    CharacterScore,
    CapacityScore,
    CapitalScore,
    CollateralScore,
    ConditionsScore,
    FiveCsScores,
    RiskScore,
    Explanation,
    LoanRecommendation,
)

# CAM models
from .cam import (
    AuditEvent,
    AuditTrail,
    CAMDocument,
)

# Application models
from .application import (
    Document,
    LoanApplication,
)

# Alert models
from .alerts import (
    CircularTradingAlert,
)

__all__ = [
    # Financial
    "FinancialData",
    "GSTData",
    "Transaction",
    "Debt",
    "Asset",
    # Company
    "Company",
    "Promoter",
    # Research
    "NewsArticle",
    "MCAData",
    "LegalCase",
    "SentimentScore",
    # Credit Assessment
    "CharacterScore",
    "CapacityScore",
    "CapitalScore",
    "CollateralScore",
    "ConditionsScore",
    "FiveCsScores",
    "RiskScore",
    "Explanation",
    "LoanRecommendation",
    # CAM
    "AuditEvent",
    "AuditTrail",
    "CAMDocument",
    # Application
    "Document",
    "LoanApplication",
    # Alerts
    "CircularTradingAlert",
]
