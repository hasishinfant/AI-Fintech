# Intelli-Credit AI Corporate Credit Decisioning Engine

AI-powered credit decisioning system that automates the preparation of Credit Appraisal Memos (CAMs) for Indian Banks and NBFCs.

## Overview

Intelli-Credit processes multi-format financial documents, performs intelligent web research, and generates explainable lending recommendations based on the Five Cs of Credit framework (Character, Capacity, Capital, Collateral, Conditions).

## Architecture

The system consists of four main components:

1. **Data Ingestor**: Multi-format document parsing and data extraction
2. **Research Agent**: Automated web intelligence gathering
3. **Credit Recommendation Engine**: Risk scoring and lending recommendations
4. **CAM Generator**: Formatted report generation with audit trails

## Technology Stack

### Backend
- Python 3.10+
- FastAPI
- PostgreSQL
- AWS S3
- pandas, scikit-learn, shap, FAISS
- pdfplumber, pytesseract (OCR)

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- React Query

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- AWS account (for S3 document storage)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
psql -U postgres -c "CREATE DATABASE intellicredit;"
psql -U postgres -d intellicredit -f app/db/schema.sql
```

6. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Testing

### Backend Tests

Run all tests:
```bash
cd backend
pytest
```

Run property-based tests only:
```bash
pytest -m property
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Frontend Tests

Run all tests:
```bash
cd frontend
npm test
```

Run tests in watch mode:
```bash
npm run test:watch
```

## Project Structure

```
intelli-credit/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Core configuration
│   │   ├── db/               # Database models and schema
│   │   ├── models/           # Domain models
│   │   ├── services/         # Business logic
│   │   │   ├── data_ingestor/
│   │   │   ├── research_agent/
│   │   │   ├── credit_engine/
│   │   │   └── cam_generator/
│   │   └── utils/            # Utilities
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── property/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── types/            # TypeScript types
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## Features

- Multi-format document ingestion (PDF, Excel, CSV, images)
- OCR for scanned documents
- Circular trading detection
- Automated web research and sentiment analysis
- Five Cs credit assessment
- Risk scoring and loan recommendations
- Explainable AI with SHAP values
- CAM generation with Word/PDF export
- Complete audit trail

## License

Proprietary - All rights reserved

## Support

For support, please contact the development team.
