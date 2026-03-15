"""Unit tests for API schemas and validation."""

import pytest
from datetime import datetime, UTC
from uuid import uuid4
from pydantic import ValidationError

from app.api.schemas import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStatusResponse,
    DocumentUploadRequest,
    DocumentResponse,
    FiveCsScoresResponse,
    CreditAssessmentResponse,
    LoanRecommendationResponse,
    CAMResponse,
    ErrorResponse
)


class TestApplicationSchemas:
    """Tests for application schemas."""

    def test_application_create_request_valid(self):
        """Test valid application creation request."""
        company_id = uuid4()
        request = ApplicationCreateRequest(
            company_id=company_id,
            loan_amount_requested=1000000.00,
            loan_purpose="Working Capital"
        )
        
        assert request.company_id == company_id
        assert request.loan_amount_requested == 1000000.00
        assert request.loan_purpose == "Working Capital"

    def test_application_create_request_flexible(self):
        """Test application creation request with flexible inputs."""
        # Only company_name
        request = ApplicationCreateRequest(company_name="Test Corp")
        assert request.company_name == "Test Corp"
        assert request.loan_amount_requested == 0.0
        assert request.loan_purpose == "Working Capital"
        
        # Only company_id
        company_id = uuid4()
        request = ApplicationCreateRequest(company_id=company_id)
        assert request.company_id == company_id
        assert request.loan_amount_requested == 0.0

    def test_application_response_valid(self):
        """Test valid application response."""
        app_id = uuid4()
        company_id = uuid4()
        now = datetime.now(UTC)
        
        response = ApplicationResponse(
            application_id=app_id,
            company_id=company_id,
            loan_amount_requested=1000000.00,
            loan_purpose="Working Capital",
            status="pending",
            submitted_date=now,
            created_at=now,
            updated_at=now
        )
        
        assert response.application_id == app_id
        assert response.status == "pending"

    def test_application_status_response_valid(self):
        """Test valid application status response."""
        app_id = uuid4()
        now = datetime.now(UTC)
        
        response = ApplicationStatusResponse(
            application_id=app_id,
            status="processing",
            updated_at=now
        )
        
        assert response.status == "processing"


class TestDocumentSchemas:
    """Tests for document schemas."""

    def test_document_upload_request_valid(self):
        """Test valid document upload request."""
        request = DocumentUploadRequest(
            document_type="GST",
            file_path="/uploads/gst_return.pdf"
        )
        
        assert request.document_type == "GST"
        assert request.file_path == "/uploads/gst_return.pdf"

    def test_document_response_valid(self):
        """Test valid document response."""
        doc_id = uuid4()
        app_id = uuid4()
        now = datetime.now(UTC)
        
        response = DocumentResponse(
            document_id=doc_id,
            application_id=app_id,
            document_type="GST",
            file_path="/uploads/gst_return.pdf",
            upload_date=now,
            processed=False,
            confidence_score=0.95
        )
        
        assert response.document_type == "GST"
        assert response.processed is False
        assert response.confidence_score == 0.95


class TestCreditAssessmentSchemas:
    """Tests for credit assessment schemas."""

    def test_five_cs_scores_valid(self):
        """Test valid Five Cs scores."""
        scores = FiveCsScoresResponse(
            character_score=70.0,
            capacity_score=60.0,
            capital_score=65.0,
            collateral_score=75.0,
            conditions_score=55.0
        )
        
        assert scores.character_score == 70.0
        assert scores.capacity_score == 60.0

    def test_five_cs_scores_out_of_range(self):
        """Test Five Cs scores with out-of-range values."""
        # Pydantic doesn't validate ranges by default, but we can add validators
        scores = FiveCsScoresResponse(
            character_score=150.0,  # Out of range
            capacity_score=60.0,
            capital_score=65.0,
            collateral_score=75.0,
            conditions_score=55.0
        )
        
        # Should still create but with invalid value
        assert scores.character_score == 150.0

    def test_credit_assessment_response_valid(self):
        """Test valid credit assessment response."""
        assessment_id = uuid4()
        app_id = uuid4()
        now = datetime.now(UTC)
        
        response = CreditAssessmentResponse(
            id=assessment_id,
            application_id=app_id,
            risk_score=65.5,
            risk_level="medium",
            five_cs_scores=FiveCsScoresResponse(
                character_score=70.0,
                capacity_score=60.0,
                capital_score=65.0,
                collateral_score=75.0,
                conditions_score=55.0
            ),
            max_loan_amount=500000.00,
            recommended_rate=10.5,
            created_at=now
        )
        
        assert response.risk_level == "medium"
        assert response.max_loan_amount == 500000.00


class TestLoanRecommendationSchemas:
    """Tests for loan recommendation schemas."""

    def test_loan_recommendation_response_valid(self):
        """Test valid loan recommendation response."""
        response = LoanRecommendationResponse(
            max_loan_amount=500000.00,
            recommended_interest_rate=10.5,
            risk_score=65.5,
            risk_level="medium",
            limiting_constraint="DSCR",
            explanations={"reason": "Low DSCR"}
        )
        
        assert response.max_loan_amount == 500000.00
        assert response.recommended_interest_rate == 10.5
        assert response.limiting_constraint == "DSCR"


class TestCAMSchemas:
    """Tests for CAM schemas."""

    def test_cam_response_valid(self):
        """Test valid CAM response."""
        app_id = uuid4()
        now = datetime.now(UTC)
        
        response = CAMResponse(
            application_id=app_id,
            company_name="Test Company Ltd",
            generated_date=now,
            version=1,
            sections={
                "executive_summary": "Summary text",
                "company_overview": "Overview text"
            }
        )
        
        assert response.company_name == "Test Company Ltd"
        assert response.version == 1
        assert len(response.sections) == 2


class TestErrorSchemas:
    """Tests for error schemas."""

    def test_error_response_valid(self):
        """Test valid error response."""
        now = datetime.now(UTC)
        
        response = ErrorResponse(
            detail="Application not found",
            error_code="NOT_FOUND",
            timestamp=now
        )
        
        assert response.detail == "Application not found"
        assert response.error_code == "NOT_FOUND"

    def test_error_response_default_timestamp(self):
        """Test error response with default timestamp."""
        response = ErrorResponse(
            detail="Internal server error"
        )
        
        assert response.detail == "Internal server error"
        assert response.timestamp is not None
