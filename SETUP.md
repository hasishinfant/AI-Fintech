# Intelli-Credit Setup Guide

This guide will help you set up the Intelli-Credit development environment.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **PostgreSQL 14+**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Tesseract OCR**: Required for document OCR
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
- **Poppler**: Required for PDF processing
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`
  - Windows: [Download binaries](https://github.com/oschwartz10612/poppler-windows/releases/)

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# Start all services
make docker-up

# Or manually:
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000

Access the application at http://localhost:3000

## Manual Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd intelli-credit
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 3. Database Setup

```bash
# Create database
psql -U postgres -c "CREATE DATABASE intellicredit;"

# Initialize schema
psql -U postgres -d intellicredit -f app/db/schema.sql

# For testing, also create test database
psql -U postgres -c "CREATE DATABASE intellicredit_test;"
psql -U postgres -d intellicredit_test -f app/db/schema.sql
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env if needed
nano .env
```

### 5. AWS S3 Setup (Optional for Development)

For document storage, you'll need an AWS S3 bucket:

1. Create an S3 bucket in AWS Console
2. Create an IAM user with S3 access
3. Add credentials to `backend/.env`:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   S3_BUCKET_NAME=your_bucket_name
   ```

For local development, you can skip this and use local file storage.

## Running the Application

### Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only property-based tests
pytest -m property

# Run only unit tests
pytest -m unit
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm run test:watch
```

## Configuration

### Backend Environment Variables

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/intellicredit

# AWS (optional for development)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=your_bucket

# API Keys (required for full functionality)
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_news_api_key
CIBIL_API_KEY=your_cibil_key

# Security
SECRET_KEY=your_secret_key_for_jwt
```

### Frontend Environment Variables

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## Development Workflow

1. **Start the database**: `docker-compose up -d postgres` (or run PostgreSQL locally)
2. **Start the backend**: `cd backend && uvicorn app.main:app --reload`
3. **Start the frontend**: `cd frontend && npm run dev`
4. **Make changes** and see them hot-reload automatically
5. **Run tests** before committing

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running: `pg_isready`
- Check connection string in `.env`
- Verify database exists: `psql -U postgres -l`

### OCR Not Working

- Verify Tesseract is installed: `tesseract --version`
- Check Tesseract path in system PATH
- On Windows, you may need to set `TESSERACT_CMD` environment variable

### Port Already in Use

- Backend (8000): Change port in uvicorn command
- Frontend (3000): Change port in `vite.config.ts`
- Database (5432): Change port in `docker-compose.yml` or `.env`

### Module Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- For frontend: `rm -rf node_modules && npm install`

## Next Steps

After setup is complete:

1. Review the [README.md](README.md) for project overview
2. Check the [design document](.kiro/specs/intelli-credit/design.md) for architecture details
3. Review the [requirements](.kiro/specs/intelli-credit/requirements.md) for feature specifications
4. Start implementing tasks from [tasks.md](.kiro/specs/intelli-credit/tasks.md)

## Support

For issues or questions, please contact the development team.
