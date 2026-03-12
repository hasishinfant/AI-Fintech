# Intelli-Credit Startup Guide

## Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- npm or yarn

## Backend Setup & Startup

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
DATABASE_URL=postgresql://user:password@localhost:5432/intelli_credit
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

### 3. Initialize Database
```bash
# Create database
createdb intelli_credit

# Run migrations (if using Alembic)
alembic upgrade head
```

### 4. Start Backend Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## Frontend Setup & Startup

### 1. Install Node Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
Create a `.env` file in the frontend directory:
```bash
REACT_APP_API_URL=http://localhost:8000/api
```

### 3. Start Frontend Development Server
```bash
npm start
```

Frontend will be available at: **http://localhost:3000**

## Running Tests

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Docker Setup (Optional)

### Build and Run with Docker Compose
```bash
docker-compose up --build
```

This will start:
- Backend API on port 8000
- Frontend on port 3000
- PostgreSQL on port 5432

## Accessing the Application

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:8000
3. **API Docs**: http://localhost:8000/docs
4. **ReDoc**: http://localhost:8000/redoc

## Default Credentials

For testing, you can use:
- Username: `credit_officer`
- Password: `test_password`

## Troubleshooting

### Backend Issues
- **Port 8000 already in use**: `lsof -i :8000` and kill the process
- **Database connection error**: Check PostgreSQL is running and credentials are correct
- **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Frontend Issues
- **Port 3000 already in use**: `lsof -i :3000` and kill the process
- **npm install fails**: Clear cache: `npm cache clean --force` and retry
- **API connection errors**: Ensure backend is running on port 8000

## API Endpoints

### Applications
- `POST /api/applications` - Create new application
- `GET /api/applications/{id}` - Get application details
- `POST /api/applications/{id}/documents` - Upload documents
- `GET /api/applications/{id}/status` - Get application status

### Processing
- `POST /api/applications/{id}/process` - Start workflow
- `GET /api/applications/{id}/research` - Get research results
- `GET /api/applications/{id}/credit-assessment` - Get credit assessment
- `GET /api/applications/{id}/recommendation` - Get loan recommendation

### CAM
- `POST /api/applications/{id}/cam/generate` - Generate CAM
- `GET /api/applications/{id}/cam` - Get CAM document
- `GET /api/applications/{id}/cam/export/word` - Export to Word
- `GET /api/applications/{id}/cam/export/pdf` - Export to PDF

## Next Steps

1. Start the backend server
2. Start the frontend server
3. Open http://localhost:3000 in your browser
4. Create a new loan application
5. Upload financial documents
6. Start the processing workflow
7. View analysis results and CAM

## Support

For issues or questions, refer to:
- Requirements: `.kiro/specs/intelli-credit/requirements.md`
- Design: `.kiro/specs/intelli-credit/design.md`
- Implementation: `IMPLEMENTATION_COMPLETE.md`
