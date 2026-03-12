"""CAM (Credit Appraisal Memo) document models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class AuditEvent:
    """Single audit trail event."""
    timestamp: datetime
    event_type: str
    description: str
    user: Optional[str]
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditTrail:
    """Complete audit trail for a loan application."""
    events: List[AuditEvent] = field(default_factory=list)


@dataclass
class CAMDocument:
    """Complete Credit Appraisal Memo document."""
    application_id: str
    company_name: str
    generated_date: datetime
    sections: Dict[str, str] = field(default_factory=dict)
    audit_trail: AuditTrail = field(default_factory=AuditTrail)
    version: int = 1
