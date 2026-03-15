"""Repository for audit trail CRUD operations."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from ..models import AuditTrailModel
from .base_repository import BaseRepository


class AuditTrailRepository(BaseRepository[AuditTrailModel]):
    """Repository for managing audit trail."""

    def __init__(self, db: Session):
        super().__init__(AuditTrailModel, db)

    def create_audit_event(
        self,
        event_type: str,
        description: str,
        application_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        event_data: Optional[dict] = None,
        timestamp: Optional[datetime] = None
    ) -> AuditTrailModel:
        """Create an audit trail event."""
        return self.create(
            event_type=event_type,
            description=description,
            application_id=application_id,
            user_id=user_id,
            event_data=event_data,
            timestamp=timestamp or datetime.now(UTC)
        )

    def get_by_application_id(self, application_id: UUID) -> List[AuditTrailModel]:
        """Get all audit events for an application."""
        return self.db.query(AuditTrailModel).filter(
            AuditTrailModel.application_id == application_id
        ).order_by(AuditTrailModel.timestamp.desc()).all()

    def get_by_event_type(self, event_type: str, skip: int = 0, limit: int = 100) -> List[AuditTrailModel]:
        """Get audit events by type."""
        return self.db.query(AuditTrailModel).filter(
            AuditTrailModel.event_type == event_type
        ).order_by(AuditTrailModel.timestamp.desc()).offset(skip).limit(limit).all()

    def get_by_user_id(self, user_id: UUID) -> List[AuditTrailModel]:
        """Get all audit events for a user."""
        return self.db.query(AuditTrailModel).filter(
            AuditTrailModel.user_id == user_id
        ).order_by(AuditTrailModel.timestamp.desc()).all()

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        application_id: Optional[UUID] = None
    ) -> List[AuditTrailModel]:
        """Get audit events within a date range."""
        query = self.db.query(AuditTrailModel).filter(
            AuditTrailModel.timestamp >= start_date,
            AuditTrailModel.timestamp <= end_date
        )
        if application_id:
            query = query.filter(AuditTrailModel.application_id == application_id)
        return query.order_by(AuditTrailModel.timestamp.desc()).all()
