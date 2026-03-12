"""Unit tests for database repositories."""

import pytest
from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ApplicationModel,
    CompanyModel,
    FinancialDataModel,
    ResearchDataModel,
    CreditAssessmentModel,
    AuditTrailModel,
)
from app.db.repositories import (
    ApplicationRepository,
    CompanyRepository,
    FinancialDataRepository,
    ResearchDataRepository,
    CreditAssessmentRepository,
    AuditTrailRepository,
)
from app.db.unit_of_work import UnitOfWork


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()


class TestCompanyRepository:
    """Tests for CompanyRepository."""

    def test_create_company(self, test_db):
        """Test creating a company."""
        repo = CompanyRepository(test_db)
        company = repo.create_company(
            name="Test Company",
            cin="U12345AB2020PTC123456",
            gstin="29ABCDE1234F1Z5",
            industry="Manufacturing"
        )
        
        assert company.company_id is not None
        assert company.name == "Test Company"
        assert company.cin == "U12345AB2020PTC123456"
        assert company.gstin == "29ABCDE1234F1Z5"

    def test_get_by_cin(self, test_db):
        """Test getting company by CIN."""
        repo = CompanyRepository(test_db)
        company = repo.create_company(
            name="Test Company",
            cin="U12345AB2020PTC123456"
        )
        
        found = repo.get_by_cin("U12345AB2020PTC123456")
        assert found is not None
        assert found.company_id == company.company_id

    def test_add_promoter(self, test_db):
        """Test adding a promoter to a company."""
        repo = CompanyRepository(test_db)
        company = repo.create_company(name="Test Company")
        
        promoter = repo.add_promoter(
            company_id=company.company_id,
            name="John Doe",
            din="12345678",
            shareholding=51.5,
            role="Managing Director"
        )
        
        assert promoter is not None
        assert promoter.name == "John Doe"
        assert promoter.shareholding == 51.5


class TestApplicationRepository:
    """Tests for ApplicationRepository."""

    def test_create_application(self, test_db):
        """Test creating an application."""
        # First create a company
        company_repo = CompanyRepository(test_db)
        company = company_repo.create_company(name="Test Company")
        
        # Create application
        app_repo = ApplicationRepository(test_db)
        application = app_repo.create_application(
            company_id=company.company_id,
            loan_amount_requested=1000000.00,
            loan_purpose="Working capital",
            submitted_date=datetime.utcnow()
        )
        
        assert application.application_id is not None
        assert application.loan_amount_requested == 1000000.00
        assert application.status == "pending"

    def test_update_status(self, test_db):
        """Test updating application status."""
        company_repo = CompanyRepository(test_db)
        company = company_repo.create_company(name="Test Company")
        
        app_repo = ApplicationRepository(test_db)
        application = app_repo.create_application(
            company_id=company.company_id,
            loan_amount_requested=1000000.00,
            loan_purpose="Working capital",
            submitted_date=datetime.utcnow()
        )
        
        updated = app_repo.update_status(application.application_id, "approved")
        assert updated.status == "approved"


class TestFinancialDataRepository:
    """Tests for FinancialDataRepository."""

    def test_create_financial_data(self, test_db):
        """Test creating financial data."""
        company_repo = CompanyRepository(test_db)
        company = company_repo.create_company(name="Test Company")
        
        fin_repo = FinancialDataRepository(test_db)
        financial_data = fin_repo.create_financial_data(
            company_id=company.company_id,
            period="FY2023",
            revenue=5000000.00,
            expenses=3000000.00,
            ebitda=2000000.00,
            net_profit=1500000.00
        )
        
        assert financial_data.id is not None
        assert financial_data.revenue == 5000000.00
        assert financial_data.period == "FY2023"

    def test_get_by_company_id(self, test_db):
        """Test getting financial data by company ID."""
        company_repo = CompanyRepository(test_db)
        company = company_repo.create_company(name="Test Company")
        
        fin_repo = FinancialDataRepository(test_db)
        fin_repo.create_financial_data(
            company_id=company.company_id,
            period="FY2023",
            revenue=5000000.00
        )
        fin_repo.create_financial_data(
            company_id=company.company_id,
            period="FY2022",
            revenue=4000000.00
        )
        
        data = fin_repo.get_by_company_id(company.company_id)
        assert len(data) == 2


class TestUnitOfWork:
    """Tests for UnitOfWork pattern."""

    def test_unit_of_work_commit(self, test_db):
        """Test UnitOfWork with successful commit."""
        with UnitOfWork(test_db) as uow:
            company = uow.companies.create_company(name="Test Company")
            uow.financial_data.create_financial_data(
                company_id=company.company_id,
                period="FY2023",
                revenue=5000000.00
            )
        
        # Verify data was committed
        company_repo = CompanyRepository(test_db)
        companies = company_repo.get_all()
        assert len(companies) == 1

    def test_unit_of_work_rollback(self, test_db):
        """Test UnitOfWork with rollback on error."""
        # Create a company first to verify rollback works
        initial_count = len(CompanyRepository(test_db).get_all())
        
        try:
            with UnitOfWork(test_db) as uow:
                # Create company but don't commit yet
                company = CompanyModel(name="Test Company")
                uow.db.add(company)
                uow.db.flush()  # Flush to DB but don't commit
                raise Exception("Test error")
        except Exception:
            pass
        
        # Verify data was rolled back
        company_repo = CompanyRepository(test_db)
        companies = company_repo.get_all()
        assert len(companies) == initial_count


class TestAuditTrailRepository:
    """Tests for AuditTrailRepository."""

    def test_create_audit_event(self, test_db):
        """Test creating an audit event."""
        audit_repo = AuditTrailRepository(test_db)
        event = audit_repo.create_audit_event(
            event_type="data_ingestion",
            description="Uploaded GST return",
            event_data={"file": "gst_return.pdf"}
        )
        
        assert event.id is not None
        assert event.event_type == "data_ingestion"
        assert event.description == "Uploaded GST return"
