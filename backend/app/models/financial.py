"""Financial data models for Intelli-Credit system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class FinancialData:
    """Core financial data extracted from financial statements."""
    company_id: str
    period: str
    revenue: float
    expenses: float
    ebitda: float
    net_profit: float
    total_assets: float
    total_liabilities: float
    equity: float
    cash_flow: float
    confidence_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class GSTData:
    """GST return data (GSTR-2A, GSTR-3B)."""
    gstin: str
    period: str
    sales: float
    purchases: float
    tax_paid: float
    transactions: List[Dict] = field(default_factory=list)


@dataclass
class Transaction:
    """Bank transaction record."""
    date: datetime
    description: str
    debit: float
    credit: float
    balance: float


@dataclass
class Debt:
    """Debt obligation details."""
    lender: str
    amount: float
    interest_rate: float
    emi: float
    outstanding: float


@dataclass
class Asset:
    """Collateral asset details."""
    asset_type: str
    description: str
    value: float
    valuation_date: datetime
