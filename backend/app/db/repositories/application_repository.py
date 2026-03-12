"""Repository for application CRUD operations."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import ApplicationModel, DocumentModel
from .base_repository import BaseRepository


class ApplicationRepository(BaseRepository[ApplicationModel]):
    """Repository for managing loan applications."""

    def __init__(self, db: Session):
        super().__init__(ApplicationModel, db)

    def create_application(
        self,
        company_id: UUID,
        loan_amount_requested: float,
        loan_purpose: str,
        submitted_date: datetime,
        status: str = "pending"
    ) -> ApplicationModel:
        """Create a new loan application."""
        return self.create(
            company_id=company_id,
            loan_amount_requested=loan_amount_requested,
            loan_purpose=loan_purpose,
            submitted_date=submitted_date,
            status=status
        )

    def get_by_company_id(self, company_id: UUID) -> List[ApplicationModel]:
        """Get all applications for a company."""
        return self.db.query(ApplicationModel).filter(
            ApplicationModel.company_id == company_id
        ).all()

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[ApplicationModel]:
        """Get applications by status."""
        return self.db.query(ApplicationModel).filter(
            ApplicationModel.status == status
        ).offset(skip).limit(limit).all()

    def update_status(self, application_id: UUID, status: str) -> Optional[ApplicationModel]:
        """Update application status."""
        return self.update(application_id, status=status)

    def add_document(
        self,
        application_id: UUID,
        document_type: str,
        file_path: str,
        upload_date: datetime,
        processed: bool = False,
        confidence_score: Optional[float] = None,
        extracted_data: Optional[dict] = None
    ) -> Optional[DocumentModel]:
        """Add a document to an application."""
        application = self.get_by_id(application_id)
        if not application:
            return None

        document = DocumentModel(
            application_id=application_id,
            document_type=document_type,
            file_path=file_path,
            upload_date=upload_date,
            processed=processed,
            confidence_score=confidence_score,
            extracted_data=extracted_data
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_documents(self, application_id: UUID) -> List[DocumentModel]:
        """Get all documents for an application."""
        return self.db.query(DocumentModel).filter(
            DocumentModel.application_id == application_id
        ).all()

    def _get_id_field(self) -> str:
        return "application_id"
