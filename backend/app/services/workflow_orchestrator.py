"""End-to-end workflow orchestration for Intelli-Credit system."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
import logging

from app.db.database import SessionLocal
from app.db.unit_of_work import UnitOfWork

from app.services.data_ingestor.document_parser import DocumentParser
from app.services.data_ingestor.data_extractor import DataExtractor
from app.services.data_ingestor.data_normalizer import DataNormalizer
from app.services.data_ingestor.circular_trading_detector import CircularTradingDetector

from app.services.research_agent.web_crawler import WebCrawler
from app.services.research_agent.sentiment_analyzer import SentimentAnalyzer
from app.services.research_agent.compliance_checker import ComplianceChecker

from app.services.credit_engine.five_cs_analyzer import FiveCsAnalyzer
from app.services.credit_engine.ratio_calculator import RatioCalculator
from app.services.credit_engine.risk_aggregator import RiskAggregator
from app.services.credit_engine.loan_calculator import LoanCalculator
from app.services.credit_engine.explainability_engine import ExplainabilityEngine

from app.services.credit_engine.audit_trail_manager import AuditTrailManager
from app.services.cam_generator.cam_generator import CAMGenerator
from app.services.cam_generator.document_exporter import DocumentExporter

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates the complete credit decisioning workflow."""

    def __init__(self):
        """Initialize workflow orchestrator with all service components."""
        self.document_parser = DocumentParser()
        self.data_extractor = DataExtractor()
        self.data_normalizer = DataNormalizer()
        self.circular_trading_detector = CircularTradingDetector()

        self.web_crawler = WebCrawler()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.compliance_checker = ComplianceChecker()

        self.five_cs_analyzer = FiveCsAnalyzer()
        self.ratio_calculator = RatioCalculator()
        self.risk_aggregator = RiskAggregator()
        self.loan_calculator = LoanCalculator()
        self.explainability_engine = ExplainabilityEngine()

        self.audit_trail_manager = AuditTrailManager()
        self.cam_generator = CAMGenerator()
        self.document_exporter = DocumentExporter()

    async def orchestrate_full_workflow(
        self,
        application_id: UUID,
        company_id: UUID,
        company_name: str,
        documents: Dict[str, Any],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Execute complete credit decisioning workflow."""
        workflow_start = datetime.utcnow()
        db = SessionLocal()
        uow = UnitOfWork(db)

        try:
            # Phase 1: Data Ingestion
            logger.info(f"Starting data ingestion for application {application_id}")
            if progress_callback:
                await progress_callback("data_ingestion", 0)

            financial_data = await self._run_data_ingestor(
                application_id, company_id, documents, uow
            )

            if progress_callback:
                await progress_callback("data_ingestion", 100)

            # Phase 2: Research & Intelligence
            logger.info(f"Starting research phase for application {application_id}")
            if progress_callback:
                await progress_callback("research", 0)

            research_data = await self._run_research_agent(
                company_id, company_name, uow
            )

            if progress_callback:
                await progress_callback("research", 100)

            # Phase 3: Credit Analysis
            logger.info(f"Starting credit analysis for application {application_id}")
            if progress_callback:
                await progress_callback("credit_analysis", 0)

            credit_assessment = await self._run_credit_engine(
                application_id, financial_data, research_data, uow
            )

            if progress_callback:
                await progress_callback("credit_analysis", 100)

            # Phase 4: CAM Generation
            logger.info(f"Starting CAM generation for application {application_id}")
            if progress_callback:
                await progress_callback("cam_generation", 0)

            cam_document = await self._generate_cam(
                application_id, company_id, company_name,
                financial_data, research_data, credit_assessment, uow
            )

            if progress_callback:
                await progress_callback("cam_generation", 100)

            workflow_end = datetime.utcnow()
            workflow_duration = (workflow_end - workflow_start).total_seconds()

            logger.info(
                f"Workflow completed for application {application_id} "
                f"in {workflow_duration:.2f} seconds"
            )

            return {
                "application_id": str(application_id),
                "status": "completed",
                "financial_data": financial_data,
                "research_data": research_data,
                "credit_assessment": credit_assessment,
                "cam_document": cam_document,
                "workflow_duration_seconds": workflow_duration,
                "completed_at": workflow_end.isoformat()
            }

        except Exception as e:
            logger.error(f"Workflow failed for application {application_id}: {str(e)}")
            uow.rollback()
            raise

        finally:
            db.close()

    async def _run_data_ingestor(
        self,
        application_id: UUID,
        company_id: UUID,
        documents: Dict[str, Any],
        uow: UnitOfWork
    ) -> Dict[str, Any]:
        """Run data ingestion pipeline."""
        extracted_data = {}

        for doc_type, doc_content in documents.items():
            try:
                if doc_type == "pdf":
                    parsed = self.document_parser.parse_pdf(doc_content)
                else:
                    parsed = doc_content

                if "gst" in doc_type.lower():
                    extracted_data["gst"] = self.data_extractor.extract_gst_returns(parsed)
                elif "itr" in doc_type.lower():
                    extracted_data["itr"] = self.data_extractor.extract_itr(parsed)
                elif "bank" in doc_type.lower():
                    extracted_data["bank_statements"] = self.data_extractor.extract_bank_statements(parsed)
                elif "annual" in doc_type.lower():
                    extracted_data["financial_statements"] = self.data_extractor.extract_annual_report(parsed)

                self.audit_trail_manager.record_data_ingestion(
                    source=doc_type,
                    timestamp=datetime.utcnow(),
                    method="document_parsing"
                )

            except Exception as e:
                logger.warning(f"Failed to extract {doc_type}: {str(e)}")
                continue

        normalized_data = self.data_normalizer.normalize_financial_data(
            extracted_data, "multi_source"
        )

        if "gst" in extracted_data and "bank_statements" in extracted_data:
            circular_trading_alert = self.circular_trading_detector.detect_circular_trading(
                extracted_data["gst"],
                extracted_data["bank_statements"]
            )
            normalized_data["circular_trading_alert"] = circular_trading_alert

        return normalized_data

    async def _run_research_agent(
        self,
        company_id: UUID,
        company_name: str,
        uow: UnitOfWork
    ) -> Dict[str, Any]:
        """Run research and intelligence gathering."""
        research_data = {}

        try:
            news_articles = self.web_crawler.search_company_news(company_name)
            research_data["news"] = news_articles

            if news_articles:
                sentiment = self.sentiment_analyzer.analyze_news_sentiment(news_articles)
                research_data["sentiment"] = sentiment

            self.audit_trail_manager.record_research_activity(
                url="news_api",
                timestamp=datetime.utcnow(),
                data_retrieved=f"{len(news_articles)} articles"
            )

        except Exception as e:
            logger.warning(f"Failed to fetch news: {str(e)}")

        try:
            mca_data = self.web_crawler.fetch_mca_filings(str(company_id))
            research_data["mca"] = mca_data

            compliance_status = self.compliance_checker.check_mca_compliance(mca_data)
            research_data["compliance_status"] = compliance_status

            self.audit_trail_manager.record_research_activity(
                url="mca_portal",
                timestamp=datetime.utcnow(),
                data_retrieved="MCA filings"
            )

        except Exception as e:
            logger.warning(f"Failed to fetch MCA data: {str(e)}")

        try:
            legal_cases = self.web_crawler.search_ecourts(company_name, [])
            research_data["legal_cases"] = legal_cases

            self.audit_trail_manager.record_research_activity(
                url="ecourts_portal",
                timestamp=datetime.utcnow(),
                data_retrieved=f"{len(legal_cases)} cases"
            )

        except Exception as e:
            logger.warning(f"Failed to fetch legal data: {str(e)}")

        return research_data

    async def _run_credit_engine(
        self,
        application_id: UUID,
        financial_data: Dict[str, Any],
        research_data: Dict[str, Any],
        uow: UnitOfWork
    ) -> Dict[str, Any]:
        """Run credit analysis and scoring."""
        assessment = {}

        try:
            character_score = self.five_cs_analyzer.analyze_character(
                {}, research_data.get("legal_cases", []), {}
            )
            assessment["character"] = character_score

            capacity_score = self.five_cs_analyzer.analyze_capacity(
                financial_data, []
            )
            assessment["capacity"] = capacity_score

            capital_score = self.five_cs_analyzer.analyze_capital(financial_data)
            assessment["capital"] = capital_score

            collateral_score = self.five_cs_analyzer.analyze_collateral([], 0)
            assessment["collateral"] = collateral_score

            conditions_score = self.five_cs_analyzer.analyze_conditions(
                {}, [], research_data.get("sentiment")
            )
            assessment["conditions"] = conditions_score

            dscr = self.ratio_calculator.calculate_dscr(
                financial_data.get("cash_flow", 0),
                financial_data.get("debt_service", 0)
            )
            assessment["dscr"] = dscr

            debt_equity = self.ratio_calculator.calculate_debt_equity_ratio(
                financial_data.get("total_liabilities", 0),
                financial_data.get("equity", 0)
            )
            assessment["debt_equity_ratio"] = debt_equity

            five_cs = {
                "character": character_score,
                "capacity": capacity_score,
                "capital": capital_score,
                "collateral": collateral_score,
                "conditions": conditions_score
            }

            risk_score = self.risk_aggregator.calculate_composite_risk_score(
                five_cs, {}
            )
            assessment["risk_score"] = risk_score

            max_loan = self.loan_calculator.calculate_max_loan_amount(
                financial_data.get("ebitda", 0),
                financial_data.get("collateral_value", 0),
                dscr
            )
            assessment["max_loan_amount"] = max_loan

            interest_rate = self.loan_calculator.determine_interest_rate(
                base_rate=7.0,
                risk_score=risk_score.get("overall_score", 50)
            )
            assessment["recommended_rate"] = interest_rate

            explanations = self.explainability_engine.explain_risk_score(
                risk_score, five_cs
            )
            assessment["explanations"] = explanations

            self.audit_trail_manager.record_calculation(
                calculation_type="risk_aggregation",
                formula="weighted_five_cs",
                inputs=five_cs,
                output=risk_score.get("overall_score", 0)
            )

        except Exception as e:
            logger.error(f"Credit analysis failed: {str(e)}")
            raise

        return assessment

    async def _generate_cam(
        self,
        application_id: UUID,
        company_id: UUID,
        company_name: str,
        financial_data: Dict[str, Any],
        research_data: Dict[str, Any],
        credit_assessment: Dict[str, Any],
        uow: UnitOfWork
    ) -> Dict[str, Any]:
        """Generate Credit Appraisal Memo."""
        try:
            cam_document = self.cam_generator.generate_cam(
                company_data={"name": company_name, "id": str(company_id)},
                financial_data=financial_data,
                research_data=research_data,
                loan_recommendation=credit_assessment,
                audit_trail=self.audit_trail_manager.get_audit_trail()
            )

            return {
                "application_id": str(application_id),
                "company_name": company_name,
                "generated_date": datetime.utcnow().isoformat(),
                "version": 1,
                "sections": cam_document.get("sections", {})
            }

        except Exception as e:
            logger.error(f"CAM generation failed: {str(e)}")
            raise
