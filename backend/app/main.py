"""FastAPI application entry point"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.api.routes import applications, processing, cam, auth
from app.db.database import Base, engine, get_db

# Create tables on startup
Base.metadata.create_all(bind=engine)

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
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(applications.router, prefix="/api")
app.include_router(processing.router, prefix="/api")
app.include_router(cam.router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Intelli-Credit API"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check"""
    db_status = "connected"
    try:
        # Execute a simple query to check DB connection
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": "0.1.0",
        "database": db_status,
    }
