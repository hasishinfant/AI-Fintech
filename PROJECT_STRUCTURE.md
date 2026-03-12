# Intelli-Credit Project Structure

This document describes the complete project structure created for the Intelli-Credit system.

## Directory Tree

```
intelli-credit/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/                      # API routes (to be implemented)
│   │   │   └── __init__.py
│   │   ├── core/                     # Core configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py             # Settings and environment variables
│   │   ├── db/                       # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py           # SQLAlchemy setup
│   │   │   └── schema.sql            # PostgreSQL schema
│   │   ├── models/                   # Domain models (to be implemented)
│   │   │   └── __init__.py
│   │   ├── services/                 # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── data_ingestor/        # Document parsing component
│   │   │   │   └── __init__.py
│   │   │   ├── research_agent/       # Web research component
│   │   │   │   └── __init__.py
│   │   │   ├── credit_engine/        # Risk scoring component
│   │   │   │   └── __init__.py
│   │   │   └── cam_generator/        # CAM generation component
│   │   │       └── __init__.py
│   │   └── utils/                    # Utility functions
│   │       └── __init__.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest configuration
│   │   ├── test_main.py              # Basic API tests
│   │   ├── unit/                     # Unit tests
│   │   │   └── __init__.py
│   │   ├── integration/              # Integration tests
│   │   │   └── __init__.py
│   │   └── property/                 # Property-based tests
│   │       └── __init__.py
│   ├── requirements.txt              # Python dependencies
│   ├── pyproject.toml                # Python project configuration
│   ├── .env.example                  # Environment variables template
│   └── Dockerfile                    # Docker configuration
│
├── frontend/                         # React TypeScript frontend
│   ├── src/
│   │   ├── api/                      # API client
│   │   │   └── client.ts
│   │   ├── types/                    # TypeScript type definitions
│   │   │   └── index.ts
│   │   ├── App.tsx                   # Main application component
│   │   ├── App.test.tsx              # App tests
│   │   ├── main.tsx                  # Application entry point
│   │   ├── index.css                 # Global styles with Tailwind
│   │   ├── setupTests.ts             # Test configuration
│   │   └── vite-env.d.ts             # Vite environment types
│   ├── index.html                    # HTML entry point
│   ├── package.json                  # Node dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── tsconfig.node.json            # TypeScript config for Node
│   ├── vite.config.ts                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── postcss.config.js             # PostCSS configuration
│   ├── jest.config.js                # Jest test configuration
│   ├── .env.example                  # Environment variables template
│   └── Dockerfile                    # Docker configuration
│
├── .kiro/                            # Kiro spec files
│   └── specs/
│       └── intelli-credit/
│           ├── requirements.md       # Requirements document
│           ├── design.md             # Design document
│           └── tasks.md              # Implementation tasks
│
├── docker-compose.yml                # Docker Compose configuration
├── Makefile                          # Development commands
├── .gitignore                        # Git ignore rules
├── README.md                         # Project overview
├── SETUP.md                          # Setup instructions
└── PROJECT_STRUCTURE.md              # This file
```

## Key Components

### Backend (Python/FastAPI)

**Core Files:**
- `app/main.py`: FastAPI application with CORS, health check endpoints
- `app/core/config.py`: Centralized configuration using Pydantic Settings
- `app/db/database.py`: SQLAlchemy database connection and session management
- `app/db/schema.sql`: Complete PostgreSQL schema with all tables and indexes

**Service Components (Placeholders):**
- `data_ingestor/`: Document parsing, OCR, data extraction
- `research_agent/`: Web crawling, sentiment analysis, compliance checking
- `credit_engine/`: Five Cs analysis, risk scoring, loan calculations
- `cam_generator/`: CAM document generation and export

**Testing:**
- `tests/conftest.py`: Pytest fixtures for database and test client
- `tests/test_main.py`: Basic API endpoint tests
- Separate directories for unit, integration, and property-based tests

### Frontend (React/TypeScript)

**Core Files:**
- `src/main.tsx`: Application entry with React Query setup
- `src/App.tsx`: Main application with routing and basic UI
- `src/api/client.ts`: Axios client with authentication interceptors
- `src/types/index.ts`: TypeScript type definitions for domain models

**Configuration:**
- `vite.config.ts`: Vite bundler with proxy to backend
- `tailwind.config.js`: Tailwind CSS with custom color palette
- `tsconfig.json`: Strict TypeScript configuration
- `jest.config.js`: Jest testing framework setup

### Database Schema

The PostgreSQL schema includes:
- `applications`: Loan application records
- `companies`: Company information
- `promoters`: Company promoter details
- `documents`: Uploaded document metadata
- `financial_data`: Extracted financial information
- `research_data`: Web research results
- `credit_assessments`: Risk scores and recommendations
- `audit_trail`: Complete audit log

All tables include proper indexes for performance.

### Development Tools

**Docker:**
- `docker-compose.yml`: Orchestrates PostgreSQL, backend, and frontend
- Individual Dockerfiles for backend and frontend
- Health checks and proper service dependencies

**Makefile:**
- `make setup`: Complete project setup
- `make docker-up`: Start all services
- `make test`: Run all tests
- `make clean`: Clean build artifacts

**Environment Configuration:**
- `.env.example` files for both backend and frontend
- Separate configuration for development, testing, and production

## Dependencies

### Backend Python Packages

**Core Framework:**
- FastAPI, Uvicorn, Pydantic

**Database:**
- SQLAlchemy, psycopg2-binary, Alembic

**Data Processing:**
- pandas, numpy

**Document Parsing:**
- pdfplumber, PyPDF2, python-docx, openpyxl

**OCR:**
- pytesseract, pdf2image, Pillow

**Machine Learning:**
- scikit-learn, xgboost, shap

**Vector Search:**
- faiss-cpu

**Web Scraping:**
- beautifulsoup4, scrapy, requests

**Testing:**
- pytest, pytest-asyncio, hypothesis

### Frontend NPM Packages

**Core:**
- React 18, React Router, TypeScript

**State Management:**
- @tanstack/react-query

**HTTP Client:**
- axios

**UI:**
- Tailwind CSS

**Testing:**
- Jest, @testing-library/react, fast-check

**Build Tools:**
- Vite, TypeScript, ESLint

## Next Steps

1. **Install Dependencies:**
   - Backend: `cd backend && pip install -r requirements.txt`
   - Frontend: `cd frontend && npm install`

2. **Set Up Database:**
   - Create PostgreSQL database
   - Run schema.sql to initialize tables

3. **Configure Environment:**
   - Copy `.env.example` to `.env` in both directories
   - Update with your credentials and API keys

4. **Start Development:**
   - Backend: `uvicorn app.main:app --reload`
   - Frontend: `npm run dev`

5. **Begin Implementation:**
   - Follow tasks in `.kiro/specs/intelli-credit/tasks.md`
   - Start with Task 2: Core data models

## Testing Strategy

The project uses a dual testing approach:

1. **Unit Tests**: Specific examples and edge cases
2. **Property-Based Tests**: Universal properties with Hypothesis/fast-check
3. **Integration Tests**: End-to-end workflows

All property tests must run minimum 100 iterations and reference their design document property.

## Documentation

- `README.md`: Project overview and quick start
- `SETUP.md`: Detailed setup instructions
- `PROJECT_STRUCTURE.md`: This file - complete structure reference
- `.kiro/specs/`: Requirements, design, and task specifications
