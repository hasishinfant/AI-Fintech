"""Repository for research data CRUD operations."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import ResearchDataModel
from .base_repository import BaseRepository


class ResearchDataRepository(BaseRepository[ResearchDataModel]):
    """Repository for managing research data."""

    def __init__(self, db: Session):
        super().__init__(ResearchDataModel, db)

    def create_research_data(
        self,
        company_id: UUID,
        data_type: str,
        content: dict,
        retrieved_at: datetime,
        source_url: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> ResearchDataModel:
        """Create research data record."""
        return self.create(
            company_id=company_id,
            data_type=data_type,
            content=content,
            retrieved_at=retrieved_at,
            source_url=source_url,
            sentiment=sentiment
        )

    def get_by_company_id(self, company_id: UUID) -> List[ResearchDataModel]:
        """Get all research data for a company."""
        return self.db.query(ResearchDataModel).filter(
            ResearchDataModel.company_id == company_id
        ).order_by(ResearchDataModel.retrieved_at.desc()).all()

    def get_by_type(self, company_id: UUID, data_type: str) -> List[ResearchDataModel]:
        """Get research data by type (news, mca, legal, rbi)."""
        return self.db.query(ResearchDataModel).filter(
            ResearchDataModel.company_id == company_id,
            ResearchDataModel.data_type == data_type
        ).order_by(ResearchDataModel.retrieved_at.desc()).all()

    def get_by_sentiment(self, company_id: UUID, sentiment: str) -> List[ResearchDataModel]:
        """Get research data by sentiment (positive, neutral, negative)."""
        return self.db.query(ResearchDataModel).filter(
            ResearchDataModel.company_id == company_id,
            ResearchDataModel.sentiment == sentiment
        ).order_by(ResearchDataModel.retrieved_at.desc()).all()

    def get_recent(self, company_id: UUID, days: int = 90) -> List[ResearchDataModel]:
        """Get recent research data within specified days."""
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        return self.db.query(ResearchDataModel).filter(
            ResearchDataModel.company_id == company_id,
            ResearchDataModel.retrieved_at >= cutoff_date
        ).order_by(ResearchDataModel.retrieved_at.desc()).all()
