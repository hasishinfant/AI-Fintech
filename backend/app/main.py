"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import applications, processing, cam

app = FastAPI(
    title="Intelli-Credit API",
    description="AI-powered corporate credit decisioning engine for Indian Banks and NBFCs",
    version="0.1.0",
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(applications.router)
app.include_router(processing.router)
app.include_router(cam.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Intelli-Credit API"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": "connected",  # TODO: Add actual DB health check
    }


@app.get("/api/applications")
async def get_applications_mock():
    """Mock endpoint for testing - returns sample applications"""
    return [
        {
            "application_id": "550e8400-e29b-41d4-a716-446655440000",
            "company_id": "660e8400-e29b-41d4-a716-446655440000",
            "company_name": "Tech Corp India",
            "loan_amount_requested": 5000000,
            "loan_purpose": "Working Capital",
            "status": "pending",
            "submitted_date": "2026-03-14T10:00:00Z"
        },
        {
            "application_id": "550e8400-e29b-41d4-a716-446655440001",
            "company_id": "660e8400-e29b-41d4-a716-446655440001",
            "company_name": "Manufacturing Ltd",
            "loan_amount_requested": 10000000,
            "loan_purpose": "Equipment Purchase",
            "status": "processing",
            "submitted_date": "2026-03-13T15:30:00Z"
        },
        {
            "application_id": "550e8400-e29b-41d4-a716-446655440002",
            "company_id": "660e8400-e29b-41d4-a716-446655440002",
            "company_name": "Retail Enterprises",
            "loan_amount_requested": 7500000,
            "loan_purpose": "Business Expansion",
            "status": "completed",
            "submitted_date": "2026-03-10T09:15:00Z"
        }
    ]
