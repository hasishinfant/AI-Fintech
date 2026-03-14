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

router = APIRouter(prefix="/api/applications", tags=["processing"])


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
        # Return mock response for development
        return {
            "status": "processing",
            "message": "Application processing started",
            "application_id": str(application_id),
            "workflow_stages": [
                {"stage": "document_parsing", "status": "queued"},
                {"stage": "research", "status": "queued"},
                {"stage": "credit_analysis", "status": "queued"},
                {"stage": "cam_generation", "status": "queued"}
            ]
        }
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
        from datetime import datetime
        
        # Return mock research data
        mock_research = [
            ResearchResultResponse(
                company_id=UUID("660e8400-e29b-41d4-a716-446655440000"),
                data_type="news",
                source_url="https://example.com/news/tech-corp-expansion",
                content={
                    "title": "Tech Corp India Announces Major Expansion",
                    "summary": "Tech Corp India plans to expand operations with new facility in Bangalore",
                    "date": "2026-03-01"
                },
                sentiment="positive",
                retrieved_at=datetime.utcnow()
            ),
            ResearchResultResponse(
                company_id=UUID("660e8400-e29b-41d4-a716-446655440000"),
                data_type="mca_filing",
                source_url="https://mca.gov.in/filing/12345",
                content={
                    "filing_type": "Annual Return",
                    "filing_date": "2026-02-15",
                    "status": "Filed"
                },
                sentiment=None,
                retrieved_at=datetime.utcnow()
            ),
            ResearchResultResponse(
                company_id=UUID("660e8400-e29b-41d4-a716-446655440000"),
                data_type="legal_case",
                source_url=None,
                content={
                    "case_count": 0,
                    "status": "No pending legal cases found"
                },
                sentiment="positive",
                retrieved_at=datetime.utcnow()
            )
        ]
        
        return mock_research
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
        from datetime import datetime
        from uuid import uuid4
        
        # Return mock credit assessment data
        mock_assessment = CreditAssessmentResponse(
            id=uuid4(),
            application_id=application_id,
            risk_score=72.5,
            risk_level="medium",
            five_cs_scores=FiveCsScoresResponse(
                character_score=75.0,
                capacity_score=68.0,
                capital_score=80.0,
                collateral_score=65.0,
                conditions_score=74.0
            ),
            max_loan_amount=4500000.0,
            recommended_rate=10.5,
            created_at=datetime.utcnow()
        )
        
        return mock_assessment
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
        # Return mock recommendation data
        mock_recommendation = LoanRecommendationResponse(
            max_loan_amount=4500000.0,
            recommended_interest_rate=10.5,
            risk_score=72.5,
            risk_level="medium",
            limiting_constraint="Debt Service Coverage Ratio",
            explanations={
                "max_loan_amount": "Based on DSCR of 1.8 and annual revenue of ₹50M",
                "interest_rate": "Base rate 9% + risk premium 1.5% based on medium risk profile",
                "risk_factors": [
                    "Strong revenue growth of 25% YoY",
                    "Moderate debt-to-equity ratio of 1.2",
                    "Good payment history with existing lenders"
                ]
            }
        )
        
        return mock_recommendation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve loan recommendation: {str(e)}"
        )
