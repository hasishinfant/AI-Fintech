"""Application management endpoints."""

from typing import List, Optional, Any
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

router = APIRouter(prefix="/applications", tags=["applications"])


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
        repo = ApplicationRepository(db)
        applications = repo.get_all()
        
        # We need to add company_name to the response
        company_repo = CompanyRepository(db)
        results = []
        for app in applications:
            company = company_repo.get_by_id(app.company_id)
            results.append(ApplicationResponse(
                application_id=app.application_id,
                company_id=app.company_id,
                company_name=company.name if company else "Unknown",
                loan_amount_requested=app.loan_amount_requested,
                loan_purpose=app.loan_purpose,
                status=app.status,
                submitted_date=app.submitted_date,
                created_at=app.created_at,
                updated_at=app.updated_at
            ))
        return results
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
) -> Any:
    """Create a new loan application."""
    try:
        # 1. Handle Company (find or create)
        company_id = request.company_id
        if not company_id and request.company_name:
            company_repo = CompanyRepository(db)
            companies = company_repo.search_by_name(request.company_name)
            if companies:
                company = companies[0]
                company_id = company.company_id
            else:
                company = company_repo.create_company(name=request.company_name)
                company_id = company.company_id
        elif company_id:
            company_repo = CompanyRepository(db)
            company = company_repo.get_by_id(company_id)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with ID {company_id} not found"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either company_id or company_name must be provided"
            )

        # 2. Create Application
        repo = ApplicationRepository(db)
        from datetime import UTC
        application = repo.create_application(
            company_id=company_id,
            loan_amount_requested=request.loan_amount_requested,
            loan_purpose=request.loan_purpose,
            submitted_date=datetime.now(UTC)
        )
        
        return ApplicationResponse(
            application_id=application.application_id,
            company_id=application.company_id,
            company_name=company.name,
            loan_amount_requested=float(application.loan_amount_requested),
            loan_purpose=application.loan_purpose,
            status=application.status,
            submitted_date=application.submitted_date,
            created_at=application.created_at,
            updated_at=application.updated_at
        )
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
        repo = ApplicationRepository(db)
        app = repo.get_by_id(application_id)
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )
        
        company_repo = CompanyRepository(db)
        company = company_repo.get_by_id(app.company_id)
        
        return ApplicationResponse(
            application_id=app.application_id,
            company_id=app.company_id,
            company_name=company.name if company else "Unknown",
            loan_amount_requested=app.loan_amount_requested,
            loan_purpose=app.loan_purpose,
            status=app.status,
            submitted_date=app.submitted_date,
            created_at=app.created_at,
            updated_at=app.updated_at
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
        repo = ApplicationRepository(db)
        app = repo.get_by_id(application_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )
        
        from datetime import UTC
        doc = repo.add_document(
            application_id=application_id,
            document_type=request.document_type,
            file_path=request.file_path,
            upload_date=datetime.now(UTC)
        )
        
        return DocumentResponse(
            document_id=doc.document_id,
            application_id=doc.application_id,
            document_type=doc.document_type,
            file_path=doc.file_path,
            upload_date=doc.upload_date,
            processed=doc.processed
        )
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
        repo = ApplicationRepository(db)
        app = repo.get_by_id(application_id)
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )
        
        return ApplicationStatusResponse(
            application_id=app.application_id,
            status=app.status,
            updated_at=app.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve application status: {str(e)}"
        )
