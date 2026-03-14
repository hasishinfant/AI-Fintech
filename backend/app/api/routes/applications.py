"""Application management endpoints."""

from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories.application_repository import ApplicationRepository
from app.db.repositories.company_repository import CompanyRepository
from app.api.schemas import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStatusResponse,
    DocumentUploadRequest,
    DocumentResponse,
    ErrorResponse
)
from app.api.auth import get_current_user, require_credit_officer, TokenData

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
) -> list[ApplicationResponse]:
    """
    Get all loan applications.
    
    Returns a list of all applications in the system.
    """
    try:
        # Return mock data for development
        from datetime import datetime
        from uuid import UUID
        
        mock_applications = [
            ApplicationResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                company_id=UUID("660e8400-e29b-41d4-a716-446655440000"),
                company_name="Tech Corp India",
                loan_amount_requested=5000000.0,
                loan_purpose="Working Capital",
                status="pending",
                submitted_date=datetime.fromisoformat("2026-03-14T10:00:00"),
                created_at=datetime.fromisoformat("2026-03-14T10:00:00"),
                updated_at=datetime.fromisoformat("2026-03-14T10:00:00")
            ),
            ApplicationResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                company_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
                company_name="Manufacturing Ltd",
                loan_amount_requested=10000000.0,
                loan_purpose="Equipment Purchase",
                status="processing",
                submitted_date=datetime.fromisoformat("2026-03-13T15:30:00"),
                created_at=datetime.fromisoformat("2026-03-13T15:30:00"),
                updated_at=datetime.fromisoformat("2026-03-13T15:30:00")
            ),
            ApplicationResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                company_id=UUID("660e8400-e29b-41d4-a716-446655440002"),
                company_name="Retail Enterprises",
                loan_amount_requested=7500000.0,
                loan_purpose="Business Expansion",
                status="completed",
                submitted_date=datetime.fromisoformat("2026-03-10T09:15:00"),
                created_at=datetime.fromisoformat("2026-03-10T09:15:00"),
                updated_at=datetime.fromisoformat("2026-03-10T09:15:00")
            )
        ]
        
        return mock_applications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve applications: {str(e)}"
        )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    request: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_credit_officer)
) -> ApplicationResponse:
    """
    Create a new loan application.
    
    - **company_id**: UUID of the company
    - **loan_amount_requested**: Requested loan amount
    - **loan_purpose**: Purpose of the loan
    """
    try:
        # Verify company exists
        company_repo = CompanyRepository(db)
        company = company_repo.get_by_id(request.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {request.company_id} not found"
            )

        # Create application
        app_repo = ApplicationRepository(db)
        application = app_repo.create_application(
            company_id=request.company_id,
            loan_amount_requested=request.loan_amount_requested,
            loan_purpose=request.loan_purpose,
            submitted_date=datetime.utcnow(),
            status="pending"
        )

        return ApplicationResponse.from_orm(application)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
) -> ApplicationResponse:
    """
    Get application details by ID.
    
    - **application_id**: UUID of the application
    """
    try:
        # Return mock data for development
        from datetime import datetime
        
        # Mock data mapping
        mock_data = {
            UUID("550e8400-e29b-41d4-a716-446655440000"): ApplicationResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                company_id=UUID("660e8400-e29b-41d4-a716-446655440000"),
                company_name="Tech Corp India",
                loan_amount_requested=5000000.0,
                loan_purpose="Working Capital",
                status="pending",
                submitted_date=datetime.fromisoformat("2026-03-14T10:00:00"),
                created_at=datetime.fromisoformat("2026-03-14T10:00:00"),
                updated_at=datetime.fromisoformat("2026-03-14T10:00:00")
            ),
            UUID("550e8400-e29b-41d4-a716-446655440001"): ApplicationResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                company_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
                company_name="Manufacturing Ltd",
                loan_amount_requested=10000000.0,
                loan_purpose="Equipment Purchase",
                status="processing",
                submitted_date=datetime.fromisoformat("2026-03-13T15:30:00"),
                created_at=datetime.fromisoformat("2026-03-13T15:30:00"),
                updated_at=datetime.fromisoformat("2026-03-13T15:30:00")
            ),
            UUID("550e8400-e29b-41d4-a716-446655440002"): ApplicationResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                company_id=UUID("660e8400-e29b-41d4-a716-446655440002"),
                company_name="Retail Enterprises",
                loan_amount_requested=7500000.0,
                loan_purpose="Business Expansion",
                status="completed",
                submitted_date=datetime.fromisoformat("2026-03-10T09:15:00"),
                created_at=datetime.fromisoformat("2026-03-10T09:15:00"),
                updated_at=datetime.fromisoformat("2026-03-10T09:15:00")
            )
        }
        
        if application_id in mock_data:
            return mock_data[application_id]
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve application: {str(e)}"
        )


@router.post("/{application_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    application_id: UUID,
    request: DocumentUploadRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_credit_officer)
) -> DocumentResponse:
    """
    Upload a document to an application.
    
    - **application_id**: UUID of the application
    - **document_type**: Type of document (e.g., 'GST', 'ITR', 'BankStatement')
    - **file_path**: Path to the uploaded file
    """
    try:
        app_repo = ApplicationRepository(db)
        
        # Verify application exists
        application = app_repo.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )

        # Add document
        document = app_repo.add_document(
            application_id=application_id,
            document_type=request.document_type,
            file_path=request.file_path,
            upload_date=datetime.utcnow(),
            processed=False
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add document"
            )

        return DocumentResponse.from_orm(document)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/{application_id}/status", response_model=ApplicationStatusResponse)
async def get_application_status(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
) -> ApplicationStatusResponse:
    """
    Get application processing status.
    
    - **application_id**: UUID of the application
    """
    try:
        from datetime import datetime
        
        # Mock status data
        mock_statuses = {
            UUID("550e8400-e29b-41d4-a716-446655440000"): ApplicationStatusResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                status="pending",
                updated_at=datetime.fromisoformat("2026-03-14T10:00:00")
            ),
            UUID("550e8400-e29b-41d4-a716-446655440001"): ApplicationStatusResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                status="processing",
                updated_at=datetime.fromisoformat("2026-03-13T15:30:00")
            ),
            UUID("550e8400-e29b-41d4-a716-446655440002"): ApplicationStatusResponse(
                application_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                status="completed",
                updated_at=datetime.fromisoformat("2026-03-10T09:15:00")
            )
        }
        
        if application_id in mock_statuses:
            return mock_statuses[application_id]
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve application status: {str(e)}"
        )
