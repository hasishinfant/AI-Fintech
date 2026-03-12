"""Repository for financial data CRUD operations."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ..models import FinancialDataModel
from .base_repository import BaseRepository


class FinancialDataRepository(BaseRepository[FinancialDataModel]):
    """Repository for managing financial data."""

    def __init__(self, db: Session):
        super().__init__(FinancialDataModel, db)

    def create_financial_data(
        self,
        company_id: UUID,
        period: str,
        revenue: Optional[float] = None,
        expenses: Optional[float] = None,
        ebitda: Optional[float] = None,
        net_profit: Optional[float] = None,
        total_assets: Optional[float] = None,
        total_liabilities: Optional[float] = None,
        equity: Optional[float] = None,
        cash_flow: Optional[float] = None
    ) -> FinancialDataModel:
        """Create financial data record."""
        return self.create(
            company_id=company_id,
            period=period,
            revenue=revenue,
            expenses=expenses,
            ebitda=ebitda,
            net_profit=net_profit,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            equity=equity,
            cash_flow=cash_flow
        )

    def get_by_company_id(self, company_id: UUID) -> List[FinancialDataModel]:
        """Get all financial data for a company."""
        return self.db.query(FinancialDataModel).filter(
            FinancialDataModel.company_id == company_id
        ).order_by(FinancialDataModel.period.desc()).all()

    def get_by_period(self, company_id: UUID, period: str) -> Optional[FinancialDataModel]:
        """Get financial data for a specific period."""
        return self.db.query(FinancialDataModel).filter(
            FinancialDataModel.company_id == company_id,
            FinancialDataModel.period == period
        ).first()

    def get_latest(self, company_id: UUID) -> Optional[FinancialDataModel]:
        """Get the most recent financial data for a company."""
        return self.db.query(FinancialDataModel).filter(
            FinancialDataModel.company_id == company_id
        ).order_by(FinancialDataModel.period.desc()).first()

    def get_historical(self, company_id: UUID, num_periods: int = 3) -> List[FinancialDataModel]:
        """Get historical financial data for a company."""
        return self.db.query(FinancialDataModel).filter(
            FinancialDataModel.company_id == company_id
        ).order_by(FinancialDataModel.period.desc()).limit(num_periods).all()
