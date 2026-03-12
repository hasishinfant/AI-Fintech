"""Repository for credit assessment CRUD operations."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ..models import CreditAssessmentModel
from .base_repository import BaseRepository


class CreditAssessmentRepository(BaseRepository[CreditAssessmentModel]):
    """Repository for managing credit assessments."""

    def __init__(self, db: Session):
        super().__init__(CreditAssessmentModel, db)

    def create_assessment(
        self,
        application_id: UUID,
        risk_score: float,
        risk_level: str,
        character_score: Optional[float] = None,
        capacity_score: Optional[float] = None,
        capital_score: Optional[float] = None,
        collateral_score: Optional[float] = None,
        conditions_score: Optional[float] = None,
        max_loan_amount: Optional[float] = None,
        recommended_rate: Optional[float] = None
    ) -> CreditAssessmentModel:
        """Create a credit assessment."""
        return self.create(
            application_id=application_id,
            risk_score=risk_score,
            risk_level=risk_level,
            character_score=character_score,
            capacity_score=capacity_score,
            capital_score=capital_score,
            collateral_score=collateral_score,
            conditions_score=conditions_score,
            max_loan_amount=max_loan_amount,
            recommended_rate=recommended_rate
        )

    def get_by_application_id(self, application_id: UUID) -> Optional[CreditAssessmentModel]:
        """Get the latest credit assessment for an application."""
        return self.db.query(CreditAssessmentModel).filter(
            CreditAssessmentModel.application_id == application_id
        ).order_by(CreditAssessmentModel.created_at.desc()).first()

    def get_all_by_application_id(self, application_id: UUID) -> List[CreditAssessmentModel]:
        """Get all credit assessments for an application (historical)."""
        return self.db.query(CreditAssessmentModel).filter(
            CreditAssessmentModel.application_id == application_id
        ).order_by(CreditAssessmentModel.created_at.desc()).all()

    def get_by_risk_level(self, risk_level: str, skip: int = 0, limit: int = 100) -> List[CreditAssessmentModel]:
        """Get assessments by risk level (high, medium, low)."""
        return self.db.query(CreditAssessmentModel).filter(
            CreditAssessmentModel.risk_level == risk_level
        ).order_by(CreditAssessmentModel.created_at.desc()).offset(skip).limit(limit).all()
