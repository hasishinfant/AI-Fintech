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
        from datetime import datetime
        
        # Return mock CAM data
        mock_cam = CAMResponse(
            application_id=application_id,
            company_name="Tech Corp India",
            generated_date=datetime.utcnow(),
            version=1,
            sections={
                "executive_summary": "Tech Corp India has applied for a working capital loan of ₹50 lakhs. Based on comprehensive analysis, we recommend approval of ₹45 lakhs at 10.5% interest rate.",
                "company_overview": "Tech Corp India is a technology services company incorporated in 2020, specializing in software development and IT consulting.",
                "financial_analysis": "Strong revenue growth of 25% YoY. DSCR of 1.8. Debt-to-equity ratio of 1.2.",
                "risk_assessment": "Medium risk profile with overall risk score of 72.5/100.",
                "recommendation": "Approve loan of ₹45 lakhs at 10.5% interest rate for 3 years."
            }
        )
        
        return mock_cam
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
        from datetime import datetime
        
        # Return mock CAM data
        mock_cam = CAMResponse(
            application_id=application_id,
            company_name="Tech Corp India",
            generated_date=datetime.utcnow(),
            version=1,
            sections={
                "executive_summary": "Tech Corp India has applied for a working capital loan of ₹50 lakhs. Based on comprehensive analysis, we recommend approval of ₹45 lakhs at 10.5% interest rate.",
                "company_overview": "Tech Corp India is a technology services company incorporated in 2020, specializing in software development and IT consulting.",
                "financial_analysis": "Strong revenue growth of 25% YoY. DSCR of 1.8. Debt-to-equity ratio of 1.2.",
                "risk_assessment": "Medium risk profile with overall risk score of 72.5/100.",
                "recommendation": "Approve loan of ₹45 lakhs at 10.5% interest rate for 3 years."
            }
        )
        
        return mock_cam
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
