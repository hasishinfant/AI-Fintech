"""CAM generation and export endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import io

from datetime import datetime, UTC
from app.db.database import get_db
from app.db.repositories.application_repository import ApplicationRepository
from app.db.repositories.company_repository import CompanyRepository
from app.db.repositories.credit_assessment_repository import CreditAssessmentRepository
from app.api.schemas import (
    CAMGenerateRequest,
    CAMResponse,
    CAMExportRequest,
    ErrorResponse
)
from app.api.auth import get_current_user, require_credit_officer, TokenData
from app.services.cam_generator.document_exporter import DocumentExporter
from app.models.cam import CAMDocument, AuditTrail
import tempfile
import os

router = APIRouter(prefix="/applications", tags=["cam"])


@router.post("/{application_id}/cam/generate", response_model=CAMResponse, status_code=status.HTTP_201_CREATED)
async def generate_cam(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_credit_officer)
) -> CAMResponse:
    """
    Generate a Credit Appraisal Memo (CAM) for an application.
    """
    try:
        app_repo = ApplicationRepository(db)
        application = app_repo.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )
        
        company_repo = CompanyRepository(db)
        company = company_repo.get_by_id(application.company_id)
        
        assessment_repo = CreditAssessmentRepository(db)
        assessment = assessment_repo.get_by_application_id(application_id)
        
        from datetime import UTC
        
        # Aggregate data into CAM sections
        sections = {
            "executive_summary": f"{company.name if company else 'The applicant'} has requested a loan of ₹{application.loan_amount_requested}. Current status is {application.status}.",
            "company_overview": f"Company: {company.name if company else 'Unknown'}. Industry: {company.industry if company else 'Unknown'}.",
            "financial_analysis": "Detailed financial analysis based on submitted documents.",
            "risk_assessment": f"Risk Level: {assessment.risk_level if assessment else 'Not Assessed'}. Risk Score: {assessment.risk_score if assessment else 'N/A'}.",
            "recommendation": f"Recommended Loan: ₹{assessment.max_loan_amount if assessment else 'N/A'} at {assessment.recommended_rate if assessment else 'N/A'}%."
        }
        
        return CAMResponse(
            application_id=application_id,
            company_name=company.name if company else "Unknown",
            generated_date=datetime.now(UTC),
            version=1,
            sections=sections
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
    """
    app_repo = ApplicationRepository(db)
    application = app_repo.get_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    
    # Check if a credit assessment exists - if not, the CAM hasn't been "generated" yet
    assessment_repo = CreditAssessmentRepository(db)
    assessment = assessment_repo.get_by_application_id(application_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAM document not found for this application. Please generate it first."
        )
    
    # For now, we regenerate it on the fly as we don't have a CAM table yet
    return await generate_cam(application_id, db, current_user)


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

        # Get CAM data
        cam_data = await get_cam(application_id, db, current_user)
        
        # Create CAMDocument object
        cam_doc = CAMDocument(
            application_id=str(application_id),
            company_name=cam_data.company_name,
            generated_date=cam_data.generated_date,
            sections=cam_data.sections,
            version=cam_data.version,
            audit_trail=AuditTrail(events=[]) # Empty for now
        )

        # Export to Word
        exporter = DocumentExporter()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp_path = tmp.name
        
        try:
            exporter.export_to_word(cam_doc, tmp_path)
            return FileResponse(
                path=tmp_path,
                filename=f"CAM_{cam_doc.company_name.replace(' ', '_')}.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e

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

        # Get CAM data
        cam_data = await get_cam(application_id, db, current_user)
        
        # Create CAMDocument object
        cam_doc = CAMDocument(
            application_id=str(application_id),
            company_name=cam_data.company_name,
            generated_date=cam_data.generated_date,
            sections=cam_data.sections,
            version=cam_data.version,
            audit_trail=AuditTrail(events=[]) # Empty for now
        )

        # Export to PDF
        exporter = DocumentExporter()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name
        
        try:
            exporter.export_to_pdf(cam_doc, tmp_path)
            return FileResponse(
                path=tmp_path,
                filename=f"CAM_{cam_doc.company_name.replace(' ', '_')}.pdf",
                media_type="application/pdf"
            )
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export CAM to PDF: {str(e)}"
        )
