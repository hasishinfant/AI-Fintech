"""SQLAlchemy ORM models for database tables."""

from datetime import datetime, UTC
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import (
    Column, String, DateTime, Boolean, DECIMAL, Text, ForeignKey, Date, JSON, TypeDecorator, CHAR
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from .database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as string with no hyphens.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid4().__class__):
                from uuid import UUID
                try:
                    value = UUID(value)
                except ValueError:
                    return value
            return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid4().__class__):
                from uuid import UUID
                value = UUID(value)
            return value


from .database import Base


class ApplicationModel(Base):
    """Application database model."""
    __tablename__ = "applications"

    application_id = Column(GUID(), primary_key=True, default=uuid4)
    company_id = Column(GUID(), nullable=False)
    loan_amount_requested = Column(DECIMAL(15, 2))
    loan_purpose = Column(Text)
    submitted_date = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    documents = relationship("DocumentModel", back_populates="application", cascade="all, delete-orphan")
    credit_assessments = relationship("CreditAssessmentModel", back_populates="application", cascade="all, delete-orphan")
    audit_trail = relationship("AuditTrailModel", back_populates="application", cascade="all, delete-orphan")


class CompanyModel(Base):
    """Company database model."""
    __tablename__ = "companies"

    company_id = Column(GUID(), primary_key=True, default=uuid4)
    cin = Column(String(21), unique=True)
    gstin = Column(String(15))
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    incorporation_date = Column(Date)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    promoters = relationship("PromoterModel", back_populates="company", cascade="all, delete-orphan")
    financial_data = relationship("FinancialDataModel", back_populates="company", cascade="all, delete-orphan")
    research_data = relationship("ResearchDataModel", back_populates="company", cascade="all, delete-orphan")


class PromoterModel(Base):
    """Promoter database model."""
    __tablename__ = "promoters"

    promoter_id = Column(GUID(), primary_key=True, default=uuid4)
    company_id = Column(GUID(), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    din = Column(String(8))
    shareholding = Column(DECIMAL(5, 2))
    role = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    company = relationship("CompanyModel", back_populates="promoters")


class DocumentModel(Base):
    """Document database model."""
    __tablename__ = "documents"

    document_id = Column(GUID(), primary_key=True, default=uuid4)
    application_id = Column(GUID(), ForeignKey("applications.application_id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_path = Column(Text, nullable=False)
    upload_date = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    processed = Column(Boolean, default=False)
    confidence_score = Column(DECIMAL(5, 2))
    extracted_data = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    application = relationship("ApplicationModel", back_populates="documents")


class FinancialDataModel(Base):
    """Financial data database model."""
    __tablename__ = "financial_data"

    id = Column(GUID(), primary_key=True, default=uuid4)
    company_id = Column(GUID(), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False)
    period = Column(String(20), nullable=False)
    revenue = Column(DECIMAL(15, 2))
    expenses = Column(DECIMAL(15, 2))
    ebitda = Column(DECIMAL(15, 2))
    net_profit = Column(DECIMAL(15, 2))
    total_assets = Column(DECIMAL(15, 2))
    total_liabilities = Column(DECIMAL(15, 2))
    equity = Column(DECIMAL(15, 2))
    cash_flow = Column(DECIMAL(15, 2))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    company = relationship("CompanyModel", back_populates="financial_data")


class ResearchDataModel(Base):
    """Research data database model."""
    __tablename__ = "research_data"

    id = Column(GUID(), primary_key=True, default=uuid4)
    company_id = Column(GUID(), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False)
    data_type = Column(String(50), nullable=False)
    source_url = Column(Text)
    content = Column(JSON, nullable=False)
    sentiment = Column(String(20))
    retrieved_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    company = relationship("CompanyModel", back_populates="research_data")


class CreditAssessmentModel(Base):
    """Credit assessment database model."""
    __tablename__ = "credit_assessments"

    id = Column(GUID(), primary_key=True, default=uuid4)
    application_id = Column(GUID(), ForeignKey("applications.application_id", ondelete="CASCADE"), nullable=False)
    risk_score = Column(DECIMAL(5, 2), nullable=False)
    risk_level = Column(String(20), nullable=False)
    character_score = Column(DECIMAL(5, 2))
    capacity_score = Column(DECIMAL(5, 2))
    capital_score = Column(DECIMAL(5, 2))
    collateral_score = Column(DECIMAL(5, 2))
    conditions_score = Column(DECIMAL(5, 2))
    max_loan_amount = Column(DECIMAL(15, 2))
    recommended_rate = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    application = relationship("ApplicationModel", back_populates="credit_assessments")


class AuditTrailModel(Base):
    """Audit trail database model."""
    __tablename__ = "audit_trail"

    id = Column(GUID(), primary_key=True, default=uuid4)
    application_id = Column(GUID(), ForeignKey("applications.application_id", ondelete="CASCADE"))
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    user_id = Column(GUID())
    event_data = Column(JSON)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    application = relationship("ApplicationModel", back_populates="audit_trail")
