"""CAM Generator service for creating Credit Appraisal Memos."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from app.models.cam import CAMDocument, AuditTrail, AuditEvent
from app.models.credit_assessment import (
    FiveCsScores,
    RiskScore,
    LoanRecommendation,
    Explanation,
)
from app.models.financial import FinancialData
from app.models.research import MCAData, SentimentScore
from app.models.company import Company


class CAMGenerator:
    """Generates comprehensive Credit Appraisal Memo documents."""

    def __init__(self):
        """Initialize CAM Generator."""
        self.audit_trail = AuditTrail()

    def generate_cam(
        self,
        application_id: str,
        company_data: Company,
        financial_data: FinancialData,
        research_data: Dict[str, Any],
        loan_recommendation: LoanRecommendation,
        audit_trail: AuditTrail,
    ) -> CAMDocument:
        """Generate complete CAM document with all sections.
        
        Args:
            application_id: Unique application identifier
            company_data: Company information
            financial_data: Financial statements and data
            research_data: Research findings (news, MCA, legal, etc.)
            loan_recommendation: Credit engine recommendation
            audit_trail: Complete audit trail of operations
            
        Returns:
            CAMDocument with all sections populated
        """
        cam_document = CAMDocument(
            application_id=application_id,
            company_name=company_data.name,
            generated_date=datetime.now(),
            audit_trail=audit_trail,
        )

        # Generate all sections
        cam_document.sections["executive_summary"] = self.generate_executive_summary(
            loan_recommendation
        )
        cam_document.sections["company_overview"] = self.generate_company_overview(
            company_data, research_data.get("mca_data")
        )
        cam_document.sections["industry_analysis"] = self.generate_industry_analysis(
            research_data, loan_recommendation.risk_score
        )
        cam_document.sections["financial_analysis"] = self.generate_financial_analysis(
            financial_data, research_data.get("ratios", {})
        )
        cam_document.sections["risk_assessment"] = self.generate_risk_assessment(
            loan_recommendation.risk_score, loan_recommendation
        )
        cam_document.sections["five_cs_summary"] = self.generate_five_cs_summary(
            loan_recommendation
        )
        cam_document.sections["final_recommendation"] = (
            self.generate_final_recommendation(loan_recommendation)
        )
        cam_document.sections["explainability_notes"] = self.add_explainability_notes(
            loan_recommendation.explanations
        )
        cam_document.sections["audit_trail"] = self.add_audit_trail(audit_trail)

        return cam_document

    def generate_executive_summary(
        self, loan_recommendation: LoanRecommendation
    ) -> str:
        """Generate executive summary section.
        
        Args:
            loan_recommendation: Loan recommendation with risk score
            
        Returns:
            Formatted executive summary text
        """
        risk_level = loan_recommendation.risk_score.risk_level.upper()
        max_amount = loan_recommendation.max_loan_amount
        interest_rate = loan_recommendation.recommended_interest_rate

        summary = f"""EXECUTIVE SUMMARY

Risk Assessment: {risk_level}
Overall Risk Score: {loan_recommendation.risk_score.overall_score:.2f}/100

Loan Recommendation:
- Maximum Loan Amount: ₹{max_amount:,.2f}
- Recommended Interest Rate: {interest_rate:.2f}%
- Limiting Constraint: {loan_recommendation.limiting_constraint}

Key Risk Factors:
"""
        for factor in loan_recommendation.risk_score.top_risk_factors[:3]:
            summary += f"- {factor}\n"

        summary += "\nKey Positive Factors:\n"
        for factor in loan_recommendation.risk_score.top_positive_factors[:3]:
            summary += f"- {factor}\n"

        return summary

    def generate_company_overview(
        self, company_data: Company, mca_data: Optional[MCAData] = None
    ) -> str:
        """Generate company overview section.
        
        Args:
            company_data: Company information
            mca_data: MCA filing data if available
            
        Returns:
            Formatted company overview text
        """
        overview = f"""COMPANY OVERVIEW

Company Name: {company_data.name}
CIN: {company_data.cin}
GSTIN: {company_data.gstin}
Industry: {company_data.industry}
Incorporation Date: {company_data.incorporation_date.strftime('%d-%m-%Y')}

Promoters:
"""
        for promoter in company_data.promoters:
            overview += f"- {promoter.name} ({promoter.role}): {promoter.shareholding:.2f}% shareholding\n"

        if mca_data:
            overview += f"""
MCA Filing Status:
- Authorized Capital: ₹{mca_data.authorized_capital:,.2f}
- Paid-up Capital: ₹{mca_data.paid_up_capital:,.2f}
- Last Filing Date: {mca_data.last_filing_date.strftime('%d-%m-%Y')}
- Compliance Status: {mca_data.compliance_status}
"""

        return overview

    def generate_industry_analysis(
        self, research_data: Dict[str, Any], risk_score: RiskScore
    ) -> str:
        """Generate industry analysis section.
        
        Args:
            research_data: Research findings including industry data
            risk_score: Risk score with conditions assessment
            
        Returns:
            Formatted industry analysis text
        """
        analysis = "INDUSTRY ANALYSIS\n\n"

        # Add industry information if available
        if "industry_data" in research_data:
            industry_data = research_data["industry_data"]
            analysis += f"Industry: {industry_data.get('name', 'N/A')}\n"
            analysis += f"Market Size: {industry_data.get('market_size', 'N/A')}\n"
            analysis += f"Growth Rate: {industry_data.get('growth_rate', 'N/A')}\n\n"

        # Add sentiment analysis if available
        if "sentiment" in research_data:
            sentiment = research_data["sentiment"]
            analysis += f"Market Sentiment: {sentiment.get('overall', 'Neutral')}\n"
            analysis += f"Positive News: {sentiment.get('positive_count', 0)}\n"
            analysis += f"Negative News: {sentiment.get('negative_count', 0)}\n\n"

        # Add risk factors
        analysis += "Key Risk Factors:\n"
        if "conditions_score" in research_data:
            conditions = research_data["conditions_score"]
            analysis += f"- Sector Risk: {conditions.get('sector_risk', 'N/A')}\n"
            analysis += f"- Regulatory Risk: {conditions.get('regulatory_risk', 'N/A')}\n"
            analysis += f"- Commodity Risk: {conditions.get('commodity_risk', 'N/A')}\n"

        return analysis

    def generate_financial_analysis(
        self, financial_data: FinancialData, ratios: Dict[str, float]
    ) -> str:
        """Generate financial analysis section.
        
        Args:
            financial_data: Financial statements
            ratios: Calculated financial ratios
            
        Returns:
            Formatted financial analysis text
        """
        analysis = f"""FINANCIAL ANALYSIS

Period: {financial_data.period}

Income Statement:
- Revenue: ₹{financial_data.revenue:,.2f}
- Expenses: ₹{financial_data.expenses:,.2f}
- EBITDA: ₹{financial_data.ebitda:,.2f}
- Net Profit: ₹{financial_data.net_profit:,.2f}

Balance Sheet:
- Total Assets: ₹{financial_data.total_assets:,.2f}
- Total Liabilities: ₹{financial_data.total_liabilities:,.2f}
- Equity: ₹{financial_data.equity:,.2f}

Cash Flow:
- Operating Cash Flow: ₹{financial_data.cash_flow:,.2f}

Key Financial Ratios:
"""
        for ratio_name, ratio_value in ratios.items():
            analysis += f"- {ratio_name}: {ratio_value:.4f}\n"

        return analysis

    def generate_risk_assessment(
        self, risk_score: RiskScore, loan_recommendation: LoanRecommendation
    ) -> str:
        """Generate risk assessment section.
        
        Args:
            risk_score: Overall risk score
            loan_recommendation: Loan recommendation with Five Cs
            
        Returns:
            Formatted risk assessment text
        """
        assessment = f"""RISK ASSESSMENT

Overall Risk Score: {risk_score.overall_score:.2f}/100
Risk Classification: {risk_score.risk_level.upper()}

Five Cs Assessment:
- Character Score: {loan_recommendation.explanations.get('character', Explanation('', [], [], '')).summary}
- Capacity Score: {loan_recommendation.explanations.get('capacity', Explanation('', [], [], '')).summary}
- Capital Score: {loan_recommendation.explanations.get('capital', Explanation('', [], [], '')).summary}
- Collateral Score: {loan_recommendation.explanations.get('collateral', Explanation('', [], [], '')).summary}
- Conditions Score: {loan_recommendation.explanations.get('conditions', Explanation('', [], [], '')).summary}

Top Risk Factors:
"""
        for i, factor in enumerate(risk_score.top_risk_factors[:5], 1):
            assessment += f"{i}. {factor}\n"

        return assessment

    def generate_five_cs_summary(
        self, loan_recommendation: LoanRecommendation
    ) -> str:
        """Generate Five Cs summary section.
        
        Args:
            loan_recommendation: Loan recommendation with Five Cs scores
            
        Returns:
            Formatted Five Cs summary text
        """
        summary = "FIVE CS SUMMARY\n\n"

        # Extract Five Cs information from explanations
        five_cs_keys = ["character", "capacity", "capital", "collateral", "conditions"]

        for cs_key in five_cs_keys:
            explanation = loan_recommendation.explanations.get(
                cs_key, Explanation("Not assessed", [], [], "")
            )
            summary += f"{cs_key.upper()}:\n"
            summary += f"Summary: {explanation.summary}\n"

            if explanation.key_factors:
                summary += "Key Factors:\n"
                for factor_name, contribution in explanation.key_factors[:3]:
                    summary += f"  - {factor_name}: {contribution:.2f}\n"

            summary += "\n"

        return summary

    def generate_final_recommendation(
        self, loan_recommendation: LoanRecommendation
    ) -> str:
        """Generate final recommendation section.
        
        Args:
            loan_recommendation: Loan recommendation
            
        Returns:
            Formatted final recommendation text
        """
        recommendation = f"""FINAL RECOMMENDATION

Risk Level: {loan_recommendation.risk_score.risk_level.upper()}
Overall Risk Score: {loan_recommendation.risk_score.overall_score:.2f}/100

Loan Recommendation:
- Maximum Loan Amount: ₹{loan_recommendation.max_loan_amount:,.2f}
- Recommended Interest Rate: {loan_recommendation.recommended_interest_rate:.2f}%
- Limiting Constraint: {loan_recommendation.limiting_constraint}

Recommendation Rationale:
The loan recommendation is based on comprehensive analysis of the Five Cs of Credit:
1. Character - Promoter credibility and track record
2. Capacity - Ability to repay based on cash flow and DSCR
3. Capital - Equity strength and financial structure
4. Collateral - Security adequacy and LTV ratio
5. Conditions - External market and regulatory factors

Based on this analysis, the recommended loan amount and interest rate reflect the 
assessed risk level and provide appropriate risk-adjusted returns.
"""
        return recommendation

    def add_explainability_notes(
        self, explanations: Dict[str, Explanation]
    ) -> str:
        """Add explainability notes section.
        
        Args:
            explanations: Dictionary of explanations for each decision component
            
        Returns:
            Formatted explainability notes text
        """
        notes = "EXPLAINABILITY NOTES\n\n"

        for component, explanation in explanations.items():
            notes += f"{component.upper()} EXPLANATION:\n"
            notes += f"Summary: {explanation.summary}\n\n"

            if explanation.key_factors:
                notes += "Contributing Factors:\n"
                for factor_name, contribution in explanation.key_factors:
                    notes += f"- {factor_name}: {contribution:.4f}\n"
                notes += "\n"

            if explanation.data_sources:
                notes += "Data Sources:\n"
                for source in explanation.data_sources:
                    notes += f"- {source}\n"
                notes += "\n"

            if explanation.reasoning:
                notes += f"Reasoning: {explanation.reasoning}\n\n"

        return notes

    def add_audit_trail(self, audit_trail: AuditTrail) -> str:
        """Add audit trail section.
        
        Args:
            audit_trail: Complete audit trail of operations
            
        Returns:
            Formatted audit trail text
        """
        trail_text = "AUDIT TRAIL\n\n"
        trail_text += f"Total Events: {len(audit_trail.events)}\n\n"

        # Group events by type
        events_by_type: Dict[str, List[AuditEvent]] = {}
        for event in audit_trail.events:
            if event.event_type not in events_by_type:
                events_by_type[event.event_type] = []
            events_by_type[event.event_type].append(event)

        # Format events by type
        for event_type, events in sorted(events_by_type.items()):
            trail_text += f"{event_type.upper()} ({len(events)} events):\n"
            for event in events[-5:]:  # Show last 5 events of each type
                trail_text += f"- {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {event.description}\n"
            trail_text += "\n"

        return trail_text
