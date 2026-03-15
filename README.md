# Intelli-Credit AI: Corporate Credit Decisioning Engine

![CI Pipeline](https://github.com/hasishinfant/AI-Fintech/actions/workflows/ci.yml/badge.svg)
![Docker Build & Push](https://github.com/hasishinfant/AI-Fintech/actions/workflows/docker.yml/badge.svg)

Intelli-Credit AI is a production-ready, automated credit appraisal system designed for Indian Banks and NBFCs. It streamlines the credit decisioning process by transforming raw financial documents and web intelligence into comprehensive, explainable Credit Appraisal Memos (CAMs).

## 🚀 Key Features

- **Multi-Format Ingestion**: Automated parsing of GSTR-2A/3B, ITR, Bank Statements, and Annual Reports.
- **Intelligent Research**: AI-driven web intelligence gathering with sentiment analysis and legal check automation.
- **Five Cs Framework**: Robust risk assessment based on Character, Capacity, Capital, Collateral, and Conditions.
- **Explainable AI**: Transparent risk scoring powered by analytical models with SHAP-based explanations.
- **Background Orchestration**: Asynchronous workflow processing from document upload to final decision.
- **CAM Export**: One-click professional report generation in both **Word (.docx)** and **PDF** formats.
- **Audit & Security**: Comprehensive audit trails and hardened JWT-based authentication.

## 🛠 Technology Stack

### Backend (Python)

- **Framework**: FastAPI (Asynchronous)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Logic**: SQLAlchemy 2.0, Pydantic V2
- **Document Processing**: `python-docx`, `ReportLab`, `pdfplumber`, `pytesseract` (OCR)
- **Time Handling**: Timezone-aware UTC-based operations

### Frontend (TypeScript)

- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **State/Data**: React Query (TanStack Query), Axios
- **Quality**: 100% Clean ESLint pass with strict typing

## 🚦 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Tesseract OCR (for scanned document processing)

### Backend Setup

1. **Navigate & Environment**:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**:

   ```bash
   cp .env.example .env
   # The system comes with a secure default SECRET_KEY
   ```

3. **Database Setup**:

   The system uses SQLite by default for development. No manual setup required.

4. **Run Server**:

   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Navigate & Install**:

   ```bash
   cd frontend
   npm install
   ```

2. **Run Dev Server**:

   ```bash
   npm run dev
   ```

## 🧪 Verification & Quality

### Backend Tests

The backend features a comprehensive suite of **641 tests** covering unit, integration, and property-based scenarios.

```bash
cd backend
pytest tests
```

### Frontend Quality

The frontend is strictly typed and linted to ensure zero runtime errors.

```bash
cd frontend
npm run lint
```

## 🏥 Health Monitoring

The system includes a dedicated health check endpoint to monitor API and Database status:
`GET /api/health`

## 📂 Project Structure

```text
AI-Fintech/
├── backend/          # FastAPI application & Test suite
├── frontend/         # React + Vite application
├── data/             # Sample documents & artifacts
└── scripts/          # Automation and utility scripts
```

## 📜 License

Proprietary - All rights reserved.
