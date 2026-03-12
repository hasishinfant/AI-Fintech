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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
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
