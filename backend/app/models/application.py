"""Loan application and document models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class Document:
    """Uploaded document metadata and extraction results."""
    document_id: str
    document_type: str  # "GST", "ITR", "BankStatement", "AnnualReport", etc.
    file_path: str
    upload_date: datetime
    processed: bool
    confidence_score: float
    extracted_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoanApplication:
    """Loan application master record."""
    application_id: str
    company_id: str
    company_name: str
    cin: str
    gstin: str
    loan_amount_requested: float
    loan_purpose: str
    submitted_date: datetime
    status: str
    documents: List[Document] = field(default_factory=list)
