"""Unit tests for API endpoints."""

import pytest
from datetime import datetime, UTC
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.models import ApplicationModel, CompanyModel, DocumentModel, CreditAssessmentModel, ResearchDataModel
from app.db.database import get_db
from app.api.auth import create_access_token


@pytest.fixture
def auth_token():
    """Create a test JWT token for Credit Officer."""
    user_id = uuid4()
    token = create_access_token(user_id, "credit_officer")
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers with token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_company(test_db: Session):
    """Create a sample company for testing."""
    # Use a unique CIN for each company to avoid IntegrityError
    unique_cin = f"U{uuid4().hex[:6].upper()}AB1234C123456"[:21]
    company = CompanyModel(
        company_id=uuid4(),
        cin=unique_cin,
        gstin="27AABCT1234H1Z0",
        name="Test Company Ltd",
        industry="Manufacturing",
        incorporation_date=datetime(2015, 1, 1).date()
    )
    test_db.add(company)
    test_db.commit()
    test_db.refresh(company)
    return company


@pytest.fixture
def sample_application(test_db: Session, sample_company):
    """Create a sample application for testing."""
    application = ApplicationModel(
        application_id=uuid4(),
        company_id=sample_company.company_id,
        loan_amount_requested=1000000.00,
        loan_purpose="Working Capital",
        submitted_date=datetime.now(UTC),
        status="pending"
    )
    test_db.add(application)
    test_db.commit()
    test_db.refresh(application)
    return application


class TestApplicationManagementEndpoints:
    """Tests for application management endpoints."""

    def test_create_application_success(self, client: TestClient, auth_headers, sample_company):
        """Test successful application creation."""
        payload = {
            "company_id": str(sample_company.company_id),
            "loan_amount_requested": 1000000.00,
            "loan_purpose": "Working Capital"
        }
        response = client.post("/api/applications", json=payload, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["company_id"] == str(sample_company.company_id)
        assert data["loan_amount_requested"] == 1000000.00
        assert data["loan_purpose"] == "Working Capital"
        assert data["status"] == "pending"

    def test_create_application_invalid_company(self, client: TestClient, auth_headers):
        """Test application creation with invalid company."""
        payload = {
            "company_id": str(uuid4()),
            "loan_amount_requested": 1000000.00,
            "loan_purpose": "Working Capital"
        }
        response = client.post("/api/applications", json=payload, headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_application_unauthorized(self, client: TestClient, sample_company):
        """Test application creation without authorization."""
        payload = {
            "company_id": str(sample_company.company_id),
            "loan_amount_requested": 1000000.00,
            "loan_purpose": "Working Capital"
        }
        response = client.post("/api/applications", json=payload)
        
        assert response.status_code == 401

    def test_get_application_success(self, client: TestClient, auth_headers, sample_application):
        """Test successful application retrieval."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["application_id"] == str(sample_application.application_id)
        assert data["status"] == "pending"

    def test_get_application_not_found(self, client: TestClient, auth_headers):
        """Test retrieval of non-existent application."""
        response = client.get(
            f"/api/applications/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_get_application_status_success(self, client: TestClient, auth_headers, sample_application):
        """Test successful status retrieval."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}/status",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["application_id"] == str(sample_application.application_id)

    def test_upload_document_success(self, client: TestClient, auth_headers, sample_application):
        """Test successful document upload."""
        payload = {
            "document_type": "GST",
            "file_path": "/uploads/gst_return.pdf"
        }
        response = client.post(
            f"/api/applications/{sample_application.application_id}/documents",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["document_type"] == "GST"
        assert data["file_path"] == "/uploads/gst_return.pdf"
        assert data["processed"] is False

    def test_upload_document_invalid_application(self, client: TestClient, auth_headers):
        """Test document upload to non-existent application."""
        payload = {
            "document_type": "GST",
            "file_path": "/uploads/gst_return.pdf"
        }
        response = client.post(
            f"/api/applications/{uuid4()}/documents",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_upload_document_unauthorized(self, client: TestClient, sample_application):
        """Test document upload without authorization."""
        payload = {
            "document_type": "GST",
            "file_path": "/uploads/gst_return.pdf"
        }
        response = client.post(
            f"/api/applications/{sample_application.application_id}/documents",
            json=payload
        )
        
        assert response.status_code == 401


class TestProcessingEndpoints:
    """Tests for processing endpoints."""

    def test_process_application_success(self, client: TestClient, auth_headers, sample_application):
        """Test successful application processing trigger."""
        response = client.post(
            f"/api/applications/{sample_application.application_id}/process",
            headers=auth_headers
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "processing"
        assert data["application_id"] == str(sample_application.application_id)

    def test_process_application_not_found(self, client: TestClient, auth_headers):
        """Test processing of non-existent application."""
        response = client.post(
            f"/api/applications/{uuid4()}/process",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_get_research_results_success(self, client: TestClient, auth_headers, test_db, sample_application):
        """Test successful research results retrieval."""
        # Add sample research data
        research = ResearchDataModel(
            company_id=sample_application.company_id,
            data_type="news",
            content={"title": "Test News", "content": "Test content"},
            retrieved_at=datetime.now(UTC),
            source_url="https://example.com",
            sentiment="positive"
        )
        test_db.add(research)
        test_db.commit()

        response = client.get(
            f"/api/applications/{sample_application.application_id}/research",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["data_type"] == "news"

    def test_get_research_results_empty(self, client: TestClient, auth_headers, sample_application):
        """Test research results retrieval with no data."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}/research",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_credit_assessment_success(self, client: TestClient, auth_headers, test_db, sample_application):
        """Test successful credit assessment retrieval."""
        # Add sample credit assessment
        assessment = CreditAssessmentModel(
            application_id=sample_application.application_id,
            risk_score=65.5,
            risk_level="medium",
            character_score=70.0,
            capacity_score=60.0,
            capital_score=65.0,
            collateral_score=75.0,
            conditions_score=55.0,
            max_loan_amount=500000.00,
            recommended_rate=10.5
        )
        test_db.add(assessment)
        test_db.commit()

        response = client.get(
            f"/api/applications/{sample_application.application_id}/credit-assessment",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["risk_score"] == 65.5
        assert data["risk_level"] == "medium"

    def test_get_credit_assessment_not_found(self, client: TestClient, auth_headers, sample_application):
        """Test credit assessment retrieval when not found."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}/credit-assessment",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_get_loan_recommendation_success(self, client: TestClient, auth_headers, test_db, sample_application):
        """Test successful loan recommendation retrieval."""
        # Add sample credit assessment
        assessment = CreditAssessmentModel(
            application_id=sample_application.application_id,
            risk_score=65.5,
            risk_level="medium",
            max_loan_amount=500000.00,
            recommended_rate=10.5
        )
        test_db.add(assessment)
        test_db.commit()

        response = client.get(
            f"/api/applications/{sample_application.application_id}/recommendation",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["max_loan_amount"] == 500000.00
        assert data["recommended_interest_rate"] == 10.5
        assert data["risk_level"] == "medium"

    def test_get_loan_recommendation_not_found(self, client: TestClient, auth_headers, sample_application):
        """Test loan recommendation retrieval when not found."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}/recommendation",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestCAMEndpoints:
    """Tests for CAM generation and export endpoints."""

    def test_generate_cam_success(self, client: TestClient, auth_headers, sample_application):
        """Test successful CAM generation."""
        response = client.post(
            f"/api/applications/{sample_application.application_id}/cam/generate",
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["application_id"] == str(sample_application.application_id)

    def test_generate_cam_not_found(self, client: TestClient, auth_headers):
        """Test CAM generation for non-existent application."""
        response = client.post(
            f"/api/applications/{uuid4()}/cam/generate",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_get_cam_not_found(self, client: TestClient, auth_headers, sample_application):
        """Test CAM retrieval when not generated."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}/cam",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_export_cam_to_word_not_found(self, client: TestClient, auth_headers, sample_application):
        """Test Word export when CAM not found."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}/cam/export/word",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_export_cam_to_pdf_not_found(self, client: TestClient, auth_headers, sample_application):
        """Test PDF export when CAM not found."""
        response = client.get(
            f"/api/applications/{sample_application.application_id}/cam/export/pdf",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestAuthenticationAndAuthorization:
    """Tests for authentication and authorization."""

    def test_missing_authorization_header(self, client: TestClient):
        """Test endpoint access without authorization header."""
        response = client.get("/api/applications/123")
        
        assert response.status_code == 401

    def test_invalid_token(self, client: TestClient):
        """Test endpoint access with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/applications/123", headers=headers)
        
        assert response.status_code == 401

    def test_credit_officer_role_required(self, client: TestClient, test_db, sample_company):
        """Test that Credit Officer role is required for creation."""
        # Create token with different role
        user_id = uuid4()
        token = create_access_token(user_id, "viewer")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "company_id": str(sample_company.company_id),
            "loan_amount_requested": 1000000.00,
            "loan_purpose": "Working Capital"
        }
        response = client.post("/api/applications", json=payload, headers=headers)
        
        assert response.status_code == 403
        assert "Credit Officer" in response.json()["detail"]
