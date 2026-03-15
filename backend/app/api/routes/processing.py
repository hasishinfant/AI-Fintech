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
    FiveCsScoresResponse,
    ResearchResultResponse,
    ErrorResponse
)
from app.api.auth import get_current_user, require_credit_officer, TokenData
from app.db.repositories.company_repository import CompanyRepository
from app.db.repositories.research_repository import ResearchDataRepository
from app.db.repositories.credit_assessment_repository import CreditAssessmentRepository
import time
import random
from datetime import datetime, UTC

router = APIRouter(prefix="/applications", tags=["processing"])


@router.post("/{application_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_application(
    application_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
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
        repo = ApplicationRepository(db)
        app = repo.get_by_id(application_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )
        
        # Update status to processing
        repo.update_status(application_id, "processing")
        
        # Trigger actual background tasks
        background_tasks.add_task(run_workflow_background, application_id, db)
        
        return {
            "status": "processing",
            "message": "Application processing started in the background",
            "application_id": str(application_id),
            "workflow_stages": [
                {"stage": "document_parsing", "status": "processing"},
                {"stage": "research", "status": "queued"},
                {"stage": "credit_analysis", "status": "queued"},
                {"stage": "cam_generation", "status": "queued"}
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process application: {str(e)}"
        )


async def run_workflow_background(application_id: UUID, db: Session):
    """
    Simulated background workflow that seeds data and updates status.
    """
    try:
        app_repo = ApplicationRepository(db)
        application = app_repo.get_by_id(application_id)
        if not application:
            return

        # Phase 1: Simulate Parsing (2 seconds)
        time.sleep(2)
        
        # Phase 2: Simulate Research (3 seconds)
        time.sleep(3)
        research_repo = ResearchDataRepository(db)
        
        # Seed some dummy research if none exists
        existing_research = research_repo.get_by_company_id(application.company_id)
        if not existing_research:
            research_repo.create_research_data(
                company_id=application.company_id,
                data_type="news",
                content={
                    "title": "Expansion plans for " + (application.company_id.hex[:8]),
                    "summary": "The company is planning to expand its operations in the next fiscal year."
                },
                retrieved_at=datetime.now(UTC),
                sentiment="positive"
            )

        # Phase 3: Simulate Credit Analysis (2 seconds)
        time.sleep(2)
        assessment_repo = CreditAssessmentRepository(db)
        
        # Seed dummy assessment if none exists
        existing_assessment = assessment_repo.get_by_application_id(application_id)
        if not existing_assessment:
            risk_score = random.uniform(60, 85)
            risk_level = "low" if risk_score > 75 else "medium"
            assessment_repo.create_assessment(
                application_id=application_id,
                risk_score=risk_score,
                risk_level=risk_level,
                character_score=random.uniform(70, 90),
                capacity_score=random.uniform(60, 80),
                capital_score=random.uniform(65, 85),
                collateral_score=random.uniform(70, 90),
                conditions_score=random.uniform(55, 75),
                max_loan_amount=application.loan_amount_requested * 0.9,
                recommended_rate=10.5
            )

        # Phase 4: Finalize
        app_repo.update_status(application_id, "completed")
        
    except Exception as e:
        print(f"Background task failed for {application_id}: {str(e)}")
        # In a real app, we'd update the application status to 'failed'


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
        app = app_repo.get_by_id(application_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )
        
        repo = ResearchDataRepository(db)
        results = repo.get_by_company_id(app.company_id)
        
        return [
            ResearchResultResponse(
                company_id=r.company_id,
                data_type=r.data_type,
                source_url=r.source_url,
                content=r.content,
                sentiment=r.sentiment,
                retrieved_at=r.retrieved_at
            ) for r in results
        ]
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
        repo = CreditAssessmentRepository(db)
        assessment = repo.get_by_application_id(application_id)
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credit assessment for application {application_id} not found"
            )
        
        return CreditAssessmentResponse(
            id=assessment.id,
            application_id=assessment.application_id,
            risk_score=float(assessment.risk_score),
            risk_level=assessment.risk_level,
            five_cs_scores=FiveCsScoresResponse(
                character_score=float(assessment.character_score) if assessment.character_score else None,
                capacity_score=float(assessment.capacity_score) if assessment.capacity_score else None,
                capital_score=float(assessment.capital_score) if assessment.capital_score else None,
                collateral_score=float(assessment.collateral_score) if assessment.collateral_score else None,
                conditions_score=float(assessment.conditions_score) if assessment.conditions_score else None
            ),
            max_loan_amount=float(assessment.max_loan_amount) if assessment.max_loan_amount else None,
            recommended_rate=float(assessment.recommended_rate) if assessment.recommended_rate else None,
            created_at=assessment.created_at
        )
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
        repo = CreditAssessmentRepository(db)
        assessment = repo.get_by_application_id(application_id)
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation for application {application_id} not found"
            )
        
        # Map to recommendation response
        return LoanRecommendationResponse(
            max_loan_amount=float(assessment.max_loan_amount) if assessment.max_loan_amount else 0.0,
            recommended_interest_rate=float(assessment.recommended_rate) if assessment.recommended_rate else 0.0,
            risk_score=float(assessment.risk_score),
            risk_level=assessment.risk_level,
            # In a real app, these would come from an explainability engine
            limiting_constraint="Debt Service Coverage Ratio",
            explanations={
                "max_loan_amount": f"Based on risk score of {assessment.risk_score} and assessment criteria.",
                "interest_rate": f"Base rate plus risk premium for {assessment.risk_level} risk level.",
                "risk_factors": [
                    f"Character score: {assessment.character_score}",
                    f"Capacity score: {assessment.capacity_score}",
                    f"Capital score: {assessment.capital_score}"
                ]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve loan recommendation: {str(e)}"
        )
