"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# Application Schemas
class ApplicationCreateRequest(BaseModel):
    """Request schema for creating a new application."""
    company_id: UUID
    loan_amount_requested: float
    loan_purpose: str


class ApplicationResponse(BaseModel):
    """Response schema for application details."""
    application_id: UUID
    company_id: UUID
    company_name: Optional[str] = None
    loan_amount_requested: float
    loan_purpose: str
    status: str
    submitted_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationStatusResponse(BaseModel):
    """Response schema for application status."""
    application_id: UUID
    status: str
    updated_at: datetime


# Document Schemas
class DocumentUploadRequest(BaseModel):
    """Request schema for uploading a document."""
    document_type: str
    file_path: str


class DocumentResponse(BaseModel):
    """Response schema for document details."""
    document_id: UUID
    application_id: UUID
    document_type: str
    file_path: str
    upload_date: datetime
    processed: bool
    confidence_score: Optional[float] = None
    extracted_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Research Schemas
class ResearchResultResponse(BaseModel):
    """Response schema for research results."""
    company_id: UUID
    data_type: str
    source_url: Optional[str] = None
    content: Dict[str, Any]
    sentiment: Optional[str] = None
    retrieved_at: datetime


# Credit Assessment Schemas
class FiveCsScoresResponse(BaseModel):
    """Response schema for Five Cs scores."""
    character_score: float
    capacity_score: float
    capital_score: float
    collateral_score: float
    conditions_score: float


class CreditAssessmentResponse(BaseModel):
    """Response schema for credit assessment."""
    id: UUID
    application_id: UUID
    risk_score: float
    risk_level: str
    five_cs_scores: FiveCsScoresResponse
    max_loan_amount: float
    recommended_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


# Loan Recommendation Schemas
class LoanRecommendationResponse(BaseModel):
    """Response schema for loan recommendation."""
    max_loan_amount: float
    recommended_interest_rate: float
    risk_score: float
    risk_level: str
    limiting_constraint: str
    explanations: Dict[str, Any]


# CAM Schemas
class CAMGenerateRequest(BaseModel):
    """Request schema for generating CAM."""
    application_id: UUID


class CAMResponse(BaseModel):
    """Response schema for CAM document."""
    application_id: UUID
    company_name: str
    generated_date: datetime
    version: int
    sections: Dict[str, str]


class CAMExportRequest(BaseModel):
    """Request schema for exporting CAM."""
    format: str = Field(..., description="Export format: 'word' or 'pdf'")


# Error Response Schema
class ErrorResponse(BaseModel):
    """Response schema for errors."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
