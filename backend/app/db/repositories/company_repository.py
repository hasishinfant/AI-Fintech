"""Repository for company CRUD operations."""

from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session

from ..models import CompanyModel, PromoterModel
from .base_repository import BaseRepository


class CompanyRepository(BaseRepository[CompanyModel]):
    """Repository for managing companies."""

    def __init__(self, db: Session):
        super().__init__(CompanyModel, db)

    def create_company(
        self,
        name: str,
        cin: Optional[str] = None,
        gstin: Optional[str] = None,
        industry: Optional[str] = None,
        incorporation_date: Optional[date] = None
    ) -> CompanyModel:
        """Create a new company."""
        return self.create(
            name=name,
            cin=cin,
            gstin=gstin,
            industry=industry,
            incorporation_date=incorporation_date
        )

    def get_by_cin(self, cin: str) -> Optional[CompanyModel]:
        """Get company by CIN."""
        return self.db.query(CompanyModel).filter(
            CompanyModel.cin == cin
        ).first()

    def get_by_gstin(self, gstin: str) -> Optional[CompanyModel]:
        """Get company by GSTIN."""
        return self.db.query(CompanyModel).filter(
            CompanyModel.gstin == gstin
        ).first()

    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[CompanyModel]:
        """Search companies by name (case-insensitive partial match)."""
        return self.db.query(CompanyModel).filter(
            CompanyModel.name.ilike(f"%{name}%")
        ).offset(skip).limit(limit).all()

    def add_promoter(
        self,
        company_id: UUID,
        name: str,
        din: Optional[str] = None,
        shareholding: Optional[float] = None,
        role: Optional[str] = None
    ) -> Optional[PromoterModel]:
        """Add a promoter to a company."""
        company = self.get_by_id(company_id)
        if not company:
            return None

        promoter = PromoterModel(
            company_id=company_id,
            name=name,
            din=din,
            shareholding=shareholding,
            role=role
        )
        self.db.add(promoter)
        self.db.commit()
        self.db.refresh(promoter)
        return promoter

    def get_promoters(self, company_id: UUID) -> List[PromoterModel]:
        """Get all promoters for a company."""
        return self.db.query(PromoterModel).filter(
            PromoterModel.company_id == company_id
        ).all()

    def _get_id_field(self) -> str:
        return "company_id"
