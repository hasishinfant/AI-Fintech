"""CAM generation and export endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import io

from app.db.database import get_db
from app.db.repositories.application_repository import ApplicationRepository
from app.api.schemas import (
    CAMGenerateRequest,
    CAMResponse,
    CAMExportRequest,
    ErrorResponse
)
from app.api.auth import get_current_user, require_credit_officer, TokenData

router = APIRouter(prefix="/api/applications", tags=["cam"])


@router.post("/{application_id}/cam/generate", response_model=CAMResponse, status_code=status.HTTP_201_CREATED)
async def generate_cam(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_credit_officer)
) -> CAMResponse:
    """
    Generate a Credit Appraisal Memo (CAM) for an application.
    
    This endpoint generates a complete CAM document with:
    - Executive Summary
    - Company Overview
    - Industry Analysis
    - Financial Analysis
    - Risk Assessment
    - Five Cs Summary
    - Final Recommendation
    - Explainability Notes
    - Audit Trail
    
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

        # TODO: Call CAMGenerator service to generate CAM
        # cam_document = cam_generator.generate_cam(application)

        return CAMResponse(
            application_id=application_id,
            company_name="",  # TODO: Get from company data
            generated_date=None,  # TODO: Get from CAM
            version=1,
            sections={}  # TODO: Get from CAM
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CAM: {str(e)}"
        )


@router.get("/{application_id}/cam", response_model=CAMResponse)
async def get_cam(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
) -> CAMResponse:
    """
    Get a previously generated CAM document.
    
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

        # TODO: Retrieve CAM from storage
        # cam_document = cam_repository.get_by_application_id(application_id)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAM document not found for this application"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CAM: {str(e)}"
        )


@router.get("/{application_id}/cam/export/word")
async def export_cam_to_word(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Export CAM to Word format (.docx).
    
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

        # TODO: Call DocumentExporter to export to Word
        # word_bytes = document_exporter.export_to_word(cam_document)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAM document not found for this application"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export CAM to Word: {str(e)}"
        )


@router.get("/{application_id}/cam/export/pdf")
async def export_cam_to_pdf(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Export CAM to PDF format.
    
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

        # TODO: Call DocumentExporter to export to PDF
        # pdf_bytes = document_exporter.export_to_pdf(cam_document)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAM document not found for this application"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export CAM to PDF: {str(e)}"
        )
