"""Unit of Work pattern for managing database transactions."""

from typing import Optional
from sqlalchemy.orm import Session

from .database import SessionLocal, TransactionManager
from .repositories import (
    ApplicationRepository,
    CompanyRepository,
    FinancialDataRepository,
    ResearchDataRepository,
    CreditAssessmentRepository,
    AuditTrailRepository,
)


class UnitOfWork:
    """
    Unit of Work pattern implementation for managing database transactions
    across multiple repositories.
    """

    def __init__(self, db: Optional[Session] = None):
        self._db = db
        self._owned_session = db is None
        self._transaction_manager: Optional[TransactionManager] = None
        
        # Repository instances
        self._applications: Optional[ApplicationRepository] = None
        self._companies: Optional[CompanyRepository] = None
        self._financial_data: Optional[FinancialDataRepository] = None
        self._research_data: Optional[ResearchDataRepository] = None
        self._credit_assessments: Optional[CreditAssessmentRepository] = None
        self._audit_trail: Optional[AuditTrailRepository] = None

    def __enter__(self):
        """Enter context manager."""
        if self._owned_session:
            self._db = SessionLocal()
        self._transaction_manager = TransactionManager(self._db)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        
        if self._owned_session and self._db:
            self._db.close()

    @property
    def db(self) -> Session:
        """Get the database session."""
        if self._db is None:
            raise RuntimeError("UnitOfWork must be used as a context manager")
        return self._db

    @property
    def applications(self) -> ApplicationRepository:
        """Get application repository."""
        if self._applications is None:
            self._applications = ApplicationRepository(self.db)
        return self._applications

    @property
    def companies(self) -> CompanyRepository:
        """Get company repository."""
        if self._companies is None:
            self._companies = CompanyRepository(self.db)
        return self._companies

    @property
    def financial_data(self) -> FinancialDataRepository:
        """Get financial data repository."""
        if self._financial_data is None:
            self._financial_data = FinancialDataRepository(self.db)
        return self._financial_data

    @property
    def research_data(self) -> ResearchDataRepository:
        """Get research data repository."""
        if self._research_data is None:
            self._research_data = ResearchDataRepository(self.db)
        return self._research_data

    @property
    def credit_assessments(self) -> CreditAssessmentRepository:
        """Get credit assessment repository."""
        if self._credit_assessments is None:
            self._credit_assessments = CreditAssessmentRepository(self.db)
        return self._credit_assessments

    @property
    def audit_trail(self) -> AuditTrailRepository:
        """Get audit trail repository."""
        if self._audit_trail is None:
            self._audit_trail = AuditTrailRepository(self.db)
        return self._audit_trail

    def commit(self):
        """Commit the current transaction."""
        if self._transaction_manager:
            self._transaction_manager.commit()

    def rollback(self):
        """Rollback the current transaction."""
        if self._transaction_manager:
            self._transaction_manager.rollback()

    def flush(self):
        """Flush pending changes to the database."""
        if self._transaction_manager:
            self._transaction_manager.flush()
