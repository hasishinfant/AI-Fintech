# Database Repository Layer

This module provides a comprehensive database repository layer for the Intelli-Credit system with CRUD operations, connection pooling, and transaction management.

## Architecture

The repository layer follows these design patterns:

- **Repository Pattern**: Encapsulates data access logic
- **Unit of Work Pattern**: Manages transactions across multiple repositories
- **Connection Pooling**: Efficient database connection management
- **Transaction Management**: Automatic commit/rollback handling

## Components

### 1. Database Connection (`database.py`)

Provides database connection management with connection pooling:

```python
from app.db import get_db, get_db_context, TransactionManager

# Using dependency injection (FastAPI)
@app.get("/companies/{id}")
def get_company(id: UUID, db: Session = Depends(get_db)):
    repo = CompanyRepository(db)
    return repo.get_by_id(id)

# Using context manager
with get_db_context() as db:
    repo = CompanyRepository(db)
    company = repo.create_company(name="Test Company")
```

**Connection Pool Configuration:**
- Pool size: 10 connections
- Max overflow: 20 additional connections
- Pool recycle: 3600 seconds (1 hour)
- Pre-ping: Enabled (verifies connections before use)

### 2. ORM Models (`models.py`)

SQLAlchemy ORM models for all database tables:

- `ApplicationModel` - Loan applications
- `CompanyModel` - Company information
- `PromoterModel` - Company promoters
- `DocumentModel` - Uploaded documents
- `FinancialDataModel` - Financial data records
- `ResearchDataModel` - Research and intelligence data
- `CreditAssessmentModel` - Credit assessment results
- `AuditTrailModel` - Audit trail events

### 3. Repositories (`repositories/`)

Repository classes for each entity with CRUD operations:

#### ApplicationRepository

```python
from app.db import ApplicationRepository

repo = ApplicationRepository(db)

# Create application
app = repo.create_application(
    company_id=company_id,
    loan_amount_requested=1000000.00,
    loan_purpose="Working capital",
    submitted_date=datetime.utcnow()
)

# Get by ID
app = repo.get_by_id(application_id)

# Get by company
apps = repo.get_by_company_id(company_id)

# Update status
repo.update_status(application_id, "approved")

# Add document
doc = repo.add_document(
    application_id=application_id,
    document_type="GST",
    file_path="s3://bucket/file.pdf",
    upload_date=datetime.utcnow()
)
```

#### CompanyRepository

```python
from app.db import CompanyRepository

repo = CompanyRepository(db)

# Create company
company = repo.create_company(
    name="ABC Corp",
    cin="U12345AB2020PTC123456",
    gstin="29ABCDE1234F1Z5",
    industry="Manufacturing"
)

# Get by CIN or GSTIN
company = repo.get_by_cin("U12345AB2020PTC123456")
company = repo.get_by_gstin("29ABCDE1234F1Z5")

# Search by name
companies = repo.search_by_name("ABC")

# Add promoter
promoter = repo.add_promoter(
    company_id=company_id,
    name="John Doe",
    din="12345678",
    shareholding=51.5,
    role="Managing Director"
)
```

#### FinancialDataRepository

```python
from app.db import FinancialDataRepository

repo = FinancialDataRepository(db)

# Create financial data
data = repo.create_financial_data(
    company_id=company_id,
    period="FY2023",
    revenue=5000000.00,
    expenses=3000000.00,
    ebitda=2000000.00,
    net_profit=1500000.00
)

# Get by company
all_data = repo.get_by_company_id(company_id)

# Get specific period
data = repo.get_by_period(company_id, "FY2023")

# Get latest
latest = repo.get_latest(company_id)

# Get historical (last N periods)
historical = repo.get_historical(company_id, num_periods=3)
```

#### ResearchDataRepository

```python
from app.db import ResearchDataRepository

repo = ResearchDataRepository(db)

# Create research data
research = repo.create_research_data(
    company_id=company_id,
    data_type="news",
    content={"title": "...", "body": "..."},
    retrieved_at=datetime.utcnow(),
    source_url="https://example.com/article",
    sentiment="positive"
)

# Get by type
news = repo.get_by_type(company_id, "news")
legal = repo.get_by_type(company_id, "legal")

# Get by sentiment
positive = repo.get_by_sentiment(company_id, "positive")

# Get recent (last N days)
recent = repo.get_recent(company_id, days=90)
```

#### CreditAssessmentRepository

```python
from app.db import CreditAssessmentRepository

repo = CreditAssessmentRepository(db)

# Create assessment
assessment = repo.create_assessment(
    application_id=application_id,
    risk_score=75.5,
    risk_level="low",
    character_score=80.0,
    capacity_score=70.0,
    capital_score=75.0,
    collateral_score=80.0,
    conditions_score=72.0,
    max_loan_amount=800000.00,
    recommended_rate=9.5
)

# Get latest assessment
latest = repo.get_by_application_id(application_id)

# Get all assessments (historical)
all_assessments = repo.get_all_by_application_id(application_id)

# Get by risk level
high_risk = repo.get_by_risk_level("high")
```

#### AuditTrailRepository

```python
from app.db import AuditTrailRepository

repo = AuditTrailRepository(db)

# Create audit event
event = repo.create_audit_event(
    event_type="data_ingestion",
    description="Uploaded GST return",
    application_id=application_id,
    user_id=user_id,
    event_data={"file": "gst_return.pdf", "size": 1024}
)

# Get by application
events = repo.get_by_application_id(application_id)

# Get by event type
ingestion_events = repo.get_by_event_type("data_ingestion")

# Get by date range
events = repo.get_by_date_range(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    application_id=application_id
)
```

### 4. Unit of Work (`unit_of_work.py`)

Manages transactions across multiple repositories:

```python
from app.db import UnitOfWork

# Basic usage
with UnitOfWork() as uow:
    # Create company
    company = uow.companies.create_company(name="ABC Corp")
    
    # Add financial data
    uow.financial_data.create_financial_data(
        company_id=company.company_id,
        period="FY2023",
        revenue=5000000.00
    )
    
    # Add research data
    uow.research_data.create_research_data(
        company_id=company.company_id,
        data_type="news",
        content={"title": "..."},
        retrieved_at=datetime.utcnow()
    )
    
    # All changes committed automatically on exit
    # Or rolled back if exception occurs

# Manual transaction control
with UnitOfWork() as uow:
    company = uow.companies.create_company(name="ABC Corp")
    uow.flush()  # Flush to DB without committing
    
    # Do more work...
    
    uow.commit()  # Explicit commit
```

## Transaction Management

The `TransactionManager` class provides transaction control:

```python
from app.db import TransactionManager

manager = TransactionManager(db)

# Context manager (recommended)
with manager.transaction():
    # All operations in this block are transactional
    repo.create_company(name="Test")
    # Automatically commits on success, rolls back on error

# Manual control
manager.begin()
try:
    repo.create_company(name="Test")
    manager.commit()
except Exception:
    manager.rollback()
    raise
```

## Testing

The repository layer includes comprehensive unit tests:

```bash
# Run all repository tests
pytest tests/test_repositories.py -v

# Run specific test class
pytest tests/test_repositories.py::TestCompanyRepository -v

# Run specific test
pytest tests/test_repositories.py::TestCompanyRepository::test_create_company -v
```

## Database Schema

The schema is defined in `schema.sql` and includes:

- Applications and documents
- Companies and promoters
- Financial data
- Research data
- Credit assessments
- Audit trail

All tables include:
- UUID primary keys
- Timestamps (created_at, updated_at)
- Foreign key constraints with CASCADE delete
- Indexes for performance

## Best Practices

1. **Use Unit of Work for multi-repository operations**
   ```python
   with UnitOfWork() as uow:
       # Multiple repository operations
       # Automatic transaction management
   ```

2. **Use dependency injection in FastAPI**
   ```python
   def endpoint(db: Session = Depends(get_db)):
       repo = CompanyRepository(db)
   ```

3. **Handle exceptions properly**
   ```python
   try:
       with UnitOfWork() as uow:
           # Operations
   except Exception as e:
       # Handle error
       # Rollback is automatic
   ```

4. **Use context managers for sessions**
   ```python
   with get_db_context() as db:
       # Session automatically closed
   ```

5. **Leverage connection pooling**
   - Pool is configured automatically
   - Connections are reused efficiently
   - Pre-ping ensures connection validity

## Performance Considerations

- **Connection pooling**: 10 base connections + 20 overflow
- **Indexes**: All foreign keys and frequently queried fields
- **Pagination**: Use `skip` and `limit` parameters
- **Lazy loading**: Relationships loaded on demand
- **Query optimization**: Use specific queries instead of loading all data

## Future Enhancements

- [ ] Add caching layer (Redis)
- [ ] Implement soft deletes
- [ ] Add full-text search
- [ ] Implement data versioning
- [ ] Add query result caching
- [ ] Implement read replicas support
