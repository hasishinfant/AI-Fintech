"""Processing endpoints for credit analysis workflow."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories.application_repository import ApplicationRepository
from app.db.repositories.credit_assessment_repository import CreditAssessmentRepository
from app.db.repositories.research_repository import ResearchDataRepository
from app.api.schemas import (
    LoanRecommendationResponse,
    CreditAssessmentResponse,
    ResearchResultResponse,
    ErrorResponse
)
from app.api.auth import get_current_user, require_credit_officer, TokenData

router = APIRouter(prefix="/api/applications", tags=["processing"])


@router.post("/{application_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_application(
    application_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_credit_officer)
):
    """
    Trigger full workflow processing for an application.
    
    This endpoint starts the complete workflow:
    1. Document parsing and data extraction
    2. Web research and intelligence gathering
    3. Five Cs analysis and risk scoring
    4. Loan calculation and interest rate determination
    
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

        # Update status to processing
        app_repo.update_status(application_id, "processing")

        # TODO: Add background task to orchestrate full workflow
        # background_tasks.add_task(orchestrate_workflow, application_id)

        return {
            "status": "processing",
            "message": "Application processing started",
            "application_id": str(application_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process application: {str(e)}"
        )


@router.get("/{application_id}/research", response_model=list[ResearchResultResponse])
async def get_research_results(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
) -> list[ResearchResultResponse]:
    """
    Get research results for an application.
    
    Returns news articles, MCA filings, legal cases, and other research data.
    
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

        # Get research data for the company
        research_repo = ResearchDataRepository(db)
        research_data = research_repo.get_by_company_id(application.company_id)

        return [ResearchResultResponse.from_orm(r) for r in research_data]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve research results: {str(e)}"
        )


@router.get("/{application_id}/credit-assessment", response_model=CreditAssessmentResponse)
async def get_credit_assessment(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
) -> CreditAssessmentResponse:
    """
    Get credit assessment results for an application.
    
    Returns Five Cs scores, risk score, and financial ratios.
    
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

        # Get credit assessment
        assessment_repo = CreditAssessmentRepository(db)
        assessment = assessment_repo.get_by_application_id(application_id)

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit assessment not found for this application"
            )

        return CreditAssessmentResponse.from_orm(assessment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve credit assessment: {str(e)}"
        )


@router.get("/{application_id}/recommendation", response_model=LoanRecommendationResponse)
async def get_loan_recommendation(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
) -> LoanRecommendationResponse:
    """
    Get loan recommendation for an application.
    
    Returns maximum loan amount, interest rate, and explanations.
    
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

        # Get credit assessment which contains recommendation
        assessment_repo = CreditAssessmentRepository(db)
        assessment = assessment_repo.get_by_application_id(application_id)

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan recommendation not found for this application"
            )

        return LoanRecommendationResponse(
            max_loan_amount=float(assessment.max_loan_amount) if assessment.max_loan_amount else 0,
            recommended_interest_rate=float(assessment.recommended_rate) if assessment.recommended_rate else 0,
            risk_score=float(assessment.risk_score),
            risk_level=assessment.risk_level,
            limiting_constraint="",  # TODO: Get from assessment data
            explanations={}  # TODO: Get from assessment data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve loan recommendation: {str(e)}"
        )
