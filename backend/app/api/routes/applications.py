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
        app_repo = ApplicationRepository(db)
        application = app_repo.get_by_id(application_id)
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )

        return ApplicationResponse.from_orm(application)
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
        app_repo = ApplicationRepository(db)
        application = app_repo.get_by_id(application_id)
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )

        return ApplicationStatusResponse(
            application_id=application.application_id,
            status=application.status,
            updated_at=application.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve application status: {str(e)}"
        )
