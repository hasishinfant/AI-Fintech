"""Database module with ORM models, repositories, and transaction management."""

from .database import (
    engine,
    SessionLocal,
    Base,
    get_db,
    get_db_context,
    TransactionManager,
)
from .models import (
    ApplicationModel,
    CompanyModel,
    PromoterModel,
    DocumentModel,
    FinancialDataModel,
    ResearchDataModel,
    CreditAssessmentModel,
    AuditTrailModel,
)
from .repositories import (
    ApplicationRepository,
    CompanyRepository,
    FinancialDataRepository,
    ResearchDataRepository,
    CreditAssessmentRepository,
    AuditTrailRepository,
)
from .unit_of_work import UnitOfWork

__all__ = [
    # Database
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "get_db_context",
    "TransactionManager",
    # Models
    "ApplicationModel",
    "CompanyModel",
    "PromoterModel",
    "DocumentModel",
    "FinancialDataModel",
    "ResearchDataModel",
    "CreditAssessmentModel",
    "AuditTrailModel",
    # Repositories
    "ApplicationRepository",
    "CompanyRepository",
    "FinancialDataRepository",
    "ResearchDataRepository",
    "CreditAssessmentRepository",
    "AuditTrailRepository",
    # Unit of Work
    "UnitOfWork",
]
