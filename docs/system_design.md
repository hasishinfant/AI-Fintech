# Intelli-Credit System Design

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Design](#component-design)
3. [Database Schema](#database-schema)
4. [API Design](#api-design)
5. [AI Pipeline Design](#ai-pipeline-design)
6. [Integration Points](#integration-points)

## System Overview

Intelli-Credit is designed as a three-tier architecture:
- **Presentation Layer**: React frontend
- **Application Layer**: FastAPI backend
- **Data Layer**: AI pipeline + Database

## Component Design

### Frontend Components

#### 1. Dashboard Component
**Purpose**: Main landing page showing all credit applications

**Features**:
- Application list with status
- Quick stats (total, pending, approved)
- Search and filter functionality
- Navigation to detailed views

**State Management**:
- Uses TanStack Query for server state
- Local state for UI interactions

#### 2. Upload Panel Component
**Purpose**: Handle document uploads for credit applications

**Features**:
- Multi-file upload support
- Progress indication
- File type validation
- Drag-and-drop interface

**Props**:
```typescript
interface UploadPanelProps {
  applicationId: string;
  onUploadComplete?: () => void;
}
```

#### 3. Risk Score Card Component
**Purpose**: Display credit risk assessment results

**Features**:
- Visual risk score display
- Risk level indicator (Low/Medium/High)
- Maximum loan amount recommendation
- Color-coded indicators

**Props**:
```typescript
interface RiskScoreCardProps {
  riskScore: number;
  riskLevel: string;
  maxLoanAmount: number;
}
```

#### 4. CAM Preview Component
**Purpose**: Display and export Credit Appraisal Memo

**Features**:
- Tabbed section navigation
- Export to Word/PDF
- Version tracking
- Print-friendly view

#### 5. Research Insights Component
**Purpose**: Display external research data

**Features**:
- Sentiment indicators
- Source attribution
- Categorized insights
- Timestamp tracking

### Backend Services

#### 1. Document Parser Service
**Location**: `ai_pipeline/document_processing/pdf_extractor.py`

**Responsibilities**:
- PDF text extraction
- OCR for scanned documents
- Document type detection
- Metadata extraction

**Key Methods**:
```python
def parse_pdf(file_path: str) -> Dict[str, Any]
def apply_ocr(image_data: bytes) -> str
def detect_document_type(text: str) -> str
```

#### 2. Data Extractor Service
**Location**: `ai_pipeline/document_processing/table_parser.py`

**Responsibilities**:
- Extract GST return data
- Extract ITR data
- Extract bank statement transactions
- Extract financial statements

**Key Methods**:
```python
def extract_gst_returns(gst_data: Dict) -> GSTData
def extract_itr(itr_data: Dict) -> Dict
def extract_bank_statements(statement_data: Dict) -> List[Transaction]
def extract_annual_report(report_data: Dict) -> FinancialData
```

#### 3. Credit Engine Service
**Location**: `ai_pipeline/credit_model/five_cs_analyzer.py`

**Responsibilities**:
- Five C's analysis (Character, Capacity, Capital, Collateral, Conditions)
- Risk scoring
- Loan recommendation
- Explainability

**Key Methods**:
```python
def analyze_character(company_data: Dict) -> float
def analyze_capacity(financial_data: Dict) -> float
def analyze_capital(financial_data: Dict) -> float
def analyze_collateral(asset_data: Dict) -> float
def analyze_conditions(market_data: Dict) -> float
def calculate_risk_score(five_cs: Dict) -> float
```

#### 4. Research Agent Service
**Location**: `ai_pipeline/research_agent/`

**Responsibilities**:
- Web scraping for company news
- Litigation search
- Compliance checking
- Sentiment analysis

**Key Methods**:
```python
def scrape_company_news(company_name: str) -> List[Dict]
def check_litigation(company_name: str) -> List[Dict]
def analyze_sentiment(text: str) -> str
def check_compliance(company_data: Dict) -> Dict
```

#### 5. CAM Generator Service
**Location**: `ai_pipeline/cam_generator/`

**Responsibilities**:
- Generate CAM from template
- Populate sections with data
- Export to Word/PDF
- Version management

**Key Methods**:
```python
def generate_cam(application_id: str) -> Dict
def export_to_word(cam_data: Dict) -> bytes
def export_to_pdf(cam_data: Dict) -> bytes
```

## Database Schema

### Applications Table
```sql
CREATE TABLE applications (
    id VARCHAR(36) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    risk_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Documents Table
```sql
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) REFERENCES applications(id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    document_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Financial Data Table
```sql
CREATE TABLE financial_data (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) REFERENCES applications(id),
    period VARCHAR(50),
    revenue DECIMAL(15, 2),
    expenses DECIMAL(15, 2),
    ebitda DECIMAL(15, 2),
    net_profit DECIMAL(15, 2),
    total_assets DECIMAL(15, 2),
    total_liabilities DECIMAL(15, 2),
    equity DECIMAL(15, 2),
    cash_flow DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Credit Assessments Table
```sql
CREATE TABLE credit_assessments (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) REFERENCES applications(id),
    risk_score DECIMAL(5, 2),
    risk_level VARCHAR(50),
    max_loan_amount DECIMAL(15, 2),
    five_cs_scores JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Research Data Table
```sql
CREATE TABLE research_data (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) REFERENCES applications(id),
    data_type VARCHAR(100),
    source_url VARCHAR(500),
    content JSON,
    sentiment VARCHAR(50),
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### CAM Table
```sql
CREATE TABLE cams (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) REFERENCES applications(id),
    version INTEGER DEFAULT 1,
    sections JSON,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(100)
);
```

## API Design

### Authentication Endpoints

#### POST /api/auth/login
**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "string",
    "username": "string",
    "role": "string"
  }
}
```

### Application Endpoints

#### GET /api/applications
**Description**: List all credit applications

**Response**:
```json
[
  {
    "id": "string",
    "company_name": "string",
    "status": "pending|approved|rejected",
    "risk_level": "low|medium|high",
    "created_at": "timestamp"
  }
]
```

#### POST /api/applications
**Description**: Create new credit application

**Request**:
```json
{
  "company_name": "string"
}
```

**Response**:
```json
{
  "id": "string",
  "company_name": "string",
  "status": "pending",
  "created_at": "timestamp"
}
```

#### GET /api/applications/{id}
**Description**: Get application details

**Response**:
```json
{
  "id": "string",
  "company_name": "string",
  "status": "string",
  "risk_level": "string",
  "created_at": "timestamp",
  "documents": [],
  "financial_data": {},
  "credit_assessment": {}
}
```

### Document Endpoints

#### POST /api/applications/{id}/documents
**Description**: Upload documents for application

**Request**: multipart/form-data with files

**Response**:
```json
{
  "uploaded_files": [
    {
      "id": "string",
      "file_name": "string",
      "document_type": "string"
    }
  ]
}
```

### Processing Endpoints

#### POST /api/applications/{id}/process
**Description**: Trigger document processing

**Response**:
```json
{
  "status": "processing",
  "message": "Document processing started"
}
```

### Credit Assessment Endpoints

#### GET /api/applications/{id}/credit-assessment
**Description**: Get credit assessment results

**Response**:
```json
{
  "risk_score": 75.5,
  "risk_level": "medium",
  "max_loan_amount": 5000000,
  "five_cs_scores": {
    "character_score": 80,
    "capacity_score": 75,
    "capital_score": 70,
    "collateral_score": 65,
    "conditions_score": 85
  }
}
```

### Research Endpoints

#### GET /api/applications/{id}/research
**Description**: Get research data

**Response**:
```json
[
  {
    "data_type": "news",
    "source_url": "string",
    "content": {},
    "sentiment": "positive|negative|neutral",
    "retrieved_at": "timestamp"
  }
]
```

### CAM Endpoints

#### GET /api/applications/{id}/cam
**Description**: Get CAM data

**Response**:
```json
{
  "id": "string",
  "version": 1,
  "sections": {
    "executive_summary": "string",
    "company_overview": "string",
    "financial_analysis": "string",
    "risk_assessment": "string",
    "recommendation": "string"
  },
  "generated_date": "timestamp"
}
```

#### POST /api/applications/{id}/cam/generate
**Description**: Generate new CAM

**Response**:
```json
{
  "status": "success",
  "cam_id": "string"
}
```

#### GET /api/applications/{id}/cam/export/word
**Description**: Export CAM to Word

**Response**: Binary file download

#### GET /api/applications/{id}/cam/export/pdf
**Description**: Export CAM to PDF

**Response**: Binary file download

## AI Pipeline Design

### Document Processing Pipeline

```
Input: PDF File
    ↓
PDF Parser (pdfplumber)
    ↓
Text Extraction
    ↓
Is Scanned? → Yes → OCR (Pytesseract)
    ↓ No
Document Type Detection
    ↓
Format-Specific Extraction
    ↓
Data Normalization
    ↓
Confidence Scoring
    ↓
Output: Structured Data
```

### Credit Scoring Pipeline

```
Input: Financial Data + Research Data
    ↓
Five C's Analysis
    ├── Character Analysis
    ├── Capacity Analysis
    ├── Capital Analysis
    ├── Collateral Analysis
    └── Conditions Analysis
    ↓
Risk Aggregation
    ↓
Loan Recommendation
    ↓
Explainability Generation
    ↓
Output: Credit Assessment
```

### Research Pipeline

```
Input: Company Name
    ↓
Web Scraping (Scrapy)
    ├── News Articles
    ├── Litigation Records
    └── Compliance Data
    ↓
Sentiment Analysis (OpenAI)
    ↓
Data Aggregation
    ↓
Output: Research Insights
```

### CAM Generation Pipeline

```
Input: Application Data
    ↓
Template Selection
    ↓
Section Generation (OpenAI)
    ├── Executive Summary
    ├── Company Overview
    ├── Financial Analysis
    ├── Risk Assessment
    └── Recommendation
    ↓
Document Assembly
    ↓
Export (python-docx / ReportLab)
    ↓
Output: CAM Document
```

## Integration Points

### 1. Frontend ↔ Backend
- **Protocol**: HTTP/REST
- **Format**: JSON
- **Authentication**: JWT Bearer Token

### 2. Backend ↔ AI Pipeline
- **Method**: Direct Python imports
- **Data Format**: Python dictionaries
- **Error Handling**: Try-catch with logging

### 3. Backend ↔ Database
- **ORM**: SQLAlchemy
- **Connection**: Connection pooling
- **Transactions**: ACID compliance

### 4. AI Pipeline ↔ External APIs
- **OpenAI API**: LLM for text generation
- **Web Scraping**: HTTP requests with Scrapy
- **Rate Limiting**: Implemented for all external calls

## Performance Considerations

1. **Caching**: Redis for frequently accessed data
2. **Async Processing**: Celery for long-running tasks
3. **Database Indexing**: Indexes on frequently queried fields
4. **File Storage**: S3 or local filesystem with CDN
5. **API Rate Limiting**: Prevent abuse

## Error Handling

1. **Frontend**: User-friendly error messages
2. **Backend**: Structured error responses with codes
3. **AI Pipeline**: Graceful degradation with fallbacks
4. **Logging**: Comprehensive logging at all levels

## Testing Strategy

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **E2E Tests**: Full workflow testing
4. **Property-Based Tests**: Hypothesis for edge cases
5. **Load Tests**: Performance under load
