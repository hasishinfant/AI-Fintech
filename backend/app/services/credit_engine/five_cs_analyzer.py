"""Five Cs credit analysis framework implementation."""

from typing import Dict, List
from datetime import datetime
from app.models.credit_assessment import (
    CharacterScore,
    CapacityScore,
    CapitalScore,
    CollateralScore,
    ConditionsScore,
    FiveCsScores,
)
from app.models.research import LegalCase, MCAData, SentimentScore, RBINotification
from app.models.financial import FinancialData, Debt, Asset


class FiveCsAnalyzer:
    """Analyzes credit risk using the Five Cs framework."""

    def analyze_character(
        self,
        promoter_data: Dict,
        legal_cases: List[LegalCase],
        mca_data: MCAData,
        credit_bureau_score: float,
    ) -> CharacterScore:
        """
        Assess promoter credibility based on litigation history, governance, and credit bureau data.
        
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
        
        Args:
            promoter_data: Dictionary containing promoter information
            legal_cases: List of legal cases involving the company or promoters
            mca_data: MCA compliance and governance data
            credit_bureau_score: CIBIL commercial credit score (300-900 range)
            
        Returns:
            CharacterScore with score (0-100) and supporting details
        """
        negative_factors = []
        
        # Requirement 5.1: Check litigation history
        litigation_count = len(legal_cases)
        litigation_score = self._calculate_litigation_score(legal_cases, negative_factors)
        
        # Requirement 5.2: Analyze governance records
        governance_rating, governance_score = self._calculate_governance_score(
            mca_data, negative_factors
        )
        
        # Requirement 5.3: Analyze credit bureau data
        bureau_score = self._normalize_credit_bureau_score(credit_bureau_score)
        if credit_bureau_score < 650:
            negative_factors.append(f"Low credit bureau score: {credit_bureau_score}")
        
        # Requirement 5.4: Calculate Character score (0-100)
        # Weighted average: 40% litigation, 30% governance, 30% credit bureau
        character_score = (
            litigation_score * 0.4 +
            governance_score * 0.3 +
            bureau_score * 0.3
        )
        
        # Ensure score is within 0-100 range
        character_score = max(0.0, min(100.0, character_score))
        
        return CharacterScore(
            score=character_score,
            litigation_count=litigation_count,
            governance_rating=governance_rating,
            credit_bureau_score=credit_bureau_score,
            negative_factors=negative_factors,
        )

    def _calculate_litigation_score(
        self, legal_cases: List[LegalCase], negative_factors: List[str]
    ) -> float:
        """
        Calculate litigation score based on number and severity of legal cases.
        
        Returns score from 0-100 (higher is better).
        """
        if not legal_cases:
            return 100.0
        
        # Categorize cases by severity
        high_severity_cases = []
        medium_severity_cases = []
        low_severity_cases = []
        
        for case in legal_cases:
            case_type_lower = case.case_type.lower()
            
            # High severity: fraud, criminal, insolvency
            if any(keyword in case_type_lower for keyword in ['fraud', 'criminal', 'insolvency', 'bankruptcy']):
                high_severity_cases.append(case)
            # Medium severity: civil disputes, contract breaches
            elif any(keyword in case_type_lower for keyword in ['civil', 'contract', 'breach', 'dispute']):
                medium_severity_cases.append(case)
            # Low severity: minor regulatory, procedural
            else:
                low_severity_cases.append(case)
        
        # Document negative factors (Requirement 5.5)
        if high_severity_cases:
            negative_factors.append(
                f"{len(high_severity_cases)} high-severity legal case(s): "
                f"{', '.join(c.case_type for c in high_severity_cases[:3])}"
            )
        if medium_severity_cases:
            negative_factors.append(
                f"{len(medium_severity_cases)} medium-severity legal case(s)"
            )
        
        # Calculate weighted penalty
        penalty = (
            len(high_severity_cases) * 20 +
            len(medium_severity_cases) * 10 +
            len(low_severity_cases) * 5
        )
        
        # Start from 100 and subtract penalties
        score = 100.0 - penalty
        return max(0.0, score)

    def _calculate_governance_score(
        self, mca_data: MCAData, negative_factors: List[str]
    ) -> tuple[str, float]:
        """
        Calculate governance score based on MCA compliance and filing status.
        
        Returns tuple of (rating_string, score_0_to_100).
        """
        score = 100.0
        
        # Check compliance status
        compliance_status = mca_data.compliance_status.lower()
        
        if compliance_status == "non-compliant":
            score -= 40
            negative_factors.append("MCA non-compliance detected")
            rating = "Poor"
        elif compliance_status == "partially_compliant":
            score -= 20
            negative_factors.append("Partial MCA compliance issues")
            rating = "Fair"
        elif compliance_status == "compliant":
            rating = "Good"
        else:
            # Unknown status - treat cautiously
            score -= 10
            rating = "Unknown"
        
        # Check filing recency (last filing should be within 1 year)
        from datetime import datetime, timedelta
        days_since_filing = (datetime.now() - mca_data.last_filing_date).days
        
        if days_since_filing > 365:
            score -= 15
            negative_factors.append(
                f"MCA filing overdue by {days_since_filing - 365} days"
            )
            rating = "Poor" if rating == "Good" else rating
        elif days_since_filing > 180:
            score -= 5
            negative_factors.append("MCA filing approaching due date")
        
        # Check director information completeness
        if not mca_data.directors or len(mca_data.directors) == 0:
            score -= 10
            negative_factors.append("No director information available")
        
        score = max(0.0, score)
        return rating, score

    def _normalize_credit_bureau_score(self, cibil_score: float) -> float:
        """
        Normalize CIBIL score (300-900 range) to 0-100 scale.
        
        CIBIL scoring:
        - 750-900: Excellent (80-100)
        - 650-749: Good (60-79)
        - 550-649: Fair (40-59)
        - 300-549: Poor (0-39)
        """
        if cibil_score >= 750:
            # Map 750-900 to 80-100
            return 80 + ((cibil_score - 750) / 150) * 20
        elif cibil_score >= 650:
            # Map 650-749 to 60-79
            return 60 + ((cibil_score - 650) / 100) * 20
        elif cibil_score >= 550:
            # Map 550-649 to 40-59
            return 40 + ((cibil_score - 550) / 100) * 20
        else:
            # Map 300-549 to 0-39
            return ((cibil_score - 300) / 250) * 40

    def analyze_capacity(
        self, financial_data: FinancialData, debt_obligations: List[Debt]
    ) -> CapacityScore:
        """
        Calculate DSCR and assess repayment ability.
        
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
        
        Args:
            financial_data: Company financial data including cash flow
            debt_obligations: List of existing debt obligations
            
        Returns:
            CapacityScore with DSCR and capacity assessment
        """
        # Requirement 6.3: Use operating cash flow from financial data
        # If cash_flow is not available, derive from EBITDA
        cash_flow = financial_data.cash_flow
        if cash_flow <= 0:
            # Derive from EBITDA as fallback
            cash_flow = financial_data.ebitda
        
        # Calculate total debt service (annual EMI + interest)
        # Requirement 6.1: DSCR = Cash Flow / Debt Service
        total_debt_service = sum(debt.emi for debt in debt_obligations)
        
        # Calculate DSCR
        if total_debt_service > 0:
            dscr = cash_flow / total_debt_service
        else:
            # No debt obligations - perfect capacity
            dscr = float('inf')
        
        # Requirement 6.2: Flag if DSCR < 1.25
        # Calculate Capacity score based on DSCR
        # Requirement 6.4: Assign Capacity score (0-100)
        capacity_score = self._calculate_capacity_score(dscr)
        
        # Determine trend (improving, stable, declining)
        # For now, mark as stable (would need historical data for trend analysis)
        trend = "stable"
        
        return CapacityScore(
            score=capacity_score,
            dscr=dscr if dscr != float('inf') else 0.0,
            cash_flow=cash_flow,
            debt_service=total_debt_service,
            trend=trend,
        )

    def _calculate_capacity_score(self, dscr: float) -> float:
        """
        Calculate Capacity score (0-100) based on DSCR.
        
        DSCR Scoring:
        - DSCR >= 2.0: Excellent (90-100)
        - DSCR 1.5-1.99: Very Good (75-89)
        - DSCR 1.25-1.49: Good (60-74)
        - DSCR 1.0-1.24: Fair (40-59)
        - DSCR < 1.0: Poor (0-39)
        - No debt: Perfect (100)
        
        Requirement 6.2: Flag if DSCR < 1.25 (score < 60)
        """
        if dscr == float('inf'):
            # No debt obligations
            return 100.0
        
        if dscr >= 2.0:
            # Map 2.0+ to 90-100
            return min(100.0, 90 + (dscr - 2.0) * 5)
        elif dscr >= 1.5:
            # Map 1.5-1.99 to 75-89
            return 75 + ((dscr - 1.5) / 0.5) * 14
        elif dscr >= 1.25:
            # Map 1.25-1.49 to 60-74
            return 60 + ((dscr - 1.25) / 0.25) * 14
        elif dscr >= 1.0:
            # Map 1.0-1.24 to 40-59
            return 40 + ((dscr - 1.0) / 0.25) * 19
        else:
            # Map 0-0.99 to 0-39
            return (dscr / 1.0) * 40

    def analyze_capital(self, financial_data: FinancialData) -> CapitalScore:
        """
        Evaluate equity strength and Debt-to-Equity ratio.
        
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
        
        Args:
            financial_data: Company financial data including balance sheet
            
        Returns:
            CapitalScore with debt/equity ratio and net worth analysis
        """
        # Requirement 7.1: Calculate Debt-to-Equity ratio
        total_debt = financial_data.total_liabilities
        total_equity = financial_data.equity
        
        # Calculate Debt-to-Equity ratio
        if total_equity > 0:
            debt_equity_ratio = total_debt / total_equity
        else:
            # If equity is zero or negative, ratio is undefined - treat as very high risk
            debt_equity_ratio = float('inf')
        
        # Requirement 7.3: Analyze net worth trends over three years
        # For now, we use the current net worth (would need historical data for trend analysis)
        net_worth = total_equity
        net_worth_trend = "stable"  # Default to stable (would need historical data)
        
        # Requirement 7.4: Calculate Capital score (0-100)
        capital_score = self._calculate_capital_score(debt_equity_ratio, net_worth)
        
        return CapitalScore(
            score=capital_score,
            debt_equity_ratio=debt_equity_ratio if debt_equity_ratio != float('inf') else 0.0,
            net_worth=net_worth,
            net_worth_trend=net_worth_trend,
        )

    def _calculate_capital_score(self, debt_equity_ratio: float, net_worth: float) -> float:
        """
        Calculate Capital score (0-100) based on Debt-to-Equity ratio and net worth.
        
        Debt-to-Equity Scoring:
        - D/E <= 0.5: Excellent (90-100)
        - D/E 0.5-1.0: Very Good (75-89)
        - D/E 1.0-2.0: Good (60-74)
        - D/E 2.0-3.0: Fair (40-59)
        - D/E > 3.0: Poor (0-39)
        - D/E = infinity (zero equity): Critical (0)
        
        Requirement 7.2: Flag if D/E > 2.0 (score < 60)
        Requirement 7.5: Include breakdown of equity components
        """
        # Handle infinite ratio (zero equity)
        if debt_equity_ratio == float('inf'):
            return 0.0
        
        # Handle negative net worth
        if net_worth <= 0:
            return 0.0
        
        # Calculate score based on D/E ratio
        if debt_equity_ratio <= 0.5:
            # Map 0-0.5 to 90-100
            return 90 + (0.5 - debt_equity_ratio) / 0.5 * 10
        elif debt_equity_ratio <= 1.0:
            # Map 0.5-1.0 to 75-89
            return 75 + (1.0 - debt_equity_ratio) / 0.5 * 14
        elif debt_equity_ratio <= 2.0:
            # Map 1.0-2.0 to 60-74
            return 60 + (2.0 - debt_equity_ratio) / 1.0 * 14
        elif debt_equity_ratio <= 3.0:
            # Map 2.0-3.0 to 40-59
            return 40 + (3.0 - debt_equity_ratio) / 1.0 * 19
        else:
            # Map 3.0+ to 0-39
            # Higher ratios get lower scores, capped at 0
            return max(0.0, 39 - (debt_equity_ratio - 3.0) * 5)

    def analyze_collateral(
        self, collateral_assets: List[Asset], loan_amount: float
    ) -> CollateralScore:
        """
        Calculate LTV and assess collateral adequacy.
        
        Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
        
        Args:
            collateral_assets: List of assets offered as collateral
            loan_amount: Requested loan amount
            
        Returns:
            CollateralScore with LTV and collateral assessment
        """
        # Requirement 8.3: Calculate aggregate LTV for multiple collateral assets
        total_collateral_value = sum(asset.value for asset in collateral_assets)
        
        # Requirement 8.1: Calculate LTV (Loan-to-Value) ratio
        # LTV = Loan Amount / Collateral Value
        if total_collateral_value > 0:
            ltv = loan_amount / total_collateral_value
        else:
            # No collateral - infinite LTV (worst case)
            ltv = float('inf')
        
        # Determine primary collateral type for reporting
        # Requirement 8.5: Include breakdown of collateral composition
        collateral_type = self._determine_primary_collateral_type(collateral_assets)
        
        # Get the most recent valuation date
        valuation_date = max(
            (asset.valuation_date for asset in collateral_assets),
            default=datetime.now()
        )
        
        # Requirement 8.4: Calculate Collateral score (0-100)
        collateral_score = self._calculate_collateral_score(ltv)
        
        return CollateralScore(
            score=collateral_score,
            ltv=ltv if ltv != float('inf') else 0.0,
            collateral_type=collateral_type,
            valuation_date=valuation_date,
        )

    def _determine_primary_collateral_type(self, collateral_assets: List[Asset]) -> str:
        """
        Determine the primary collateral type from the list of assets.
        
        Returns the most valuable asset type or "mixed" if multiple types.
        """
        if not collateral_assets:
            return "none"
        
        if len(collateral_assets) == 1:
            return collateral_assets[0].asset_type
        
        # Group by asset type and sum values
        type_values = {}
        for asset in collateral_assets:
            asset_type = asset.asset_type
            type_values[asset_type] = type_values.get(asset_type, 0) + asset.value
        
        # If only one type, return it
        if len(type_values) == 1:
            return list(type_values.keys())[0]
        
        # Multiple types - return the most valuable one
        primary_type = max(type_values.items(), key=lambda x: x[1])[0]
        return primary_type

    def _calculate_collateral_score(self, ltv: float) -> float:
        """
        Calculate Collateral score (0-100) based on LTV ratio.
        
        LTV Scoring:
        - LTV <= 0.5: Excellent (90-100)
        - LTV 0.5-0.75: Good (70-89)
        - LTV 0.75-1.0: Fair (50-69)
        - LTV 1.0-1.5: Poor (20-49)
        - LTV > 1.5: Critical (0-19)
        - No collateral (infinity): Critical (0)
        
        Requirement 8.2: Flag if LTV > 0.75 (score < 70)
        """
        # Handle no collateral case
        if ltv == float('inf'):
            return 0.0
        
        # Handle negative LTV (shouldn't happen but be safe)
        if ltv < 0:
            return 0.0
        
        # Calculate score based on LTV
        if ltv <= 0.5:
            # Map 0-0.5 to 90-100
            return 90 + (0.5 - ltv) / 0.5 * 10
        elif ltv <= 0.75:
            # Map 0.5-0.75 to 70-89
            return 70 + (0.75 - ltv) / 0.25 * 19
        elif ltv <= 1.0:
            # Map 0.75-1.0 to 50-69
            return 50 + (1.0 - ltv) / 0.25 * 19
        elif ltv <= 1.5:
            # Map 1.0-1.5 to 20-49
            return 20 + (1.5 - ltv) / 0.5 * 29
        else:
            # Map 1.5+ to 0-19
            # Higher LTV gets lower scores, capped at 0
            return max(0.0, 19 - (ltv - 1.5) * 5)

    def analyze_conditions(
        self,
        industry_data: Dict,
        rbi_notifications: List[RBINotification],
        sentiment: SentimentScore,
    ) -> ConditionsScore:
        """
        Assess external risk factors including sector, regulatory, and market conditions.
        
        Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
        
        Args:
            industry_data: Industry-specific data and benchmarks
                Expected keys: 'sector', 'growth_rate', 'volatility', 'commodity_exposure'
            rbi_notifications: Relevant RBI regulatory notifications
            sentiment: News sentiment analysis results
            
        Returns:
            ConditionsScore with external risk assessment (0-100)
        """
        risk_factors = []
        
        # Requirement 9.1: Analyze sector-specific risks from industry reports
        sector_risk, sector_score = self._assess_sector_risk(industry_data, risk_factors)
        
        # Requirement 9.2: Check RBI notifications and policy changes
        regulatory_risk, regulatory_score = self._assess_regulatory_risk(
            rbi_notifications, risk_factors
        )
        
        # Requirement 9.3: Assess commodity price volatility risks
        commodity_risk, commodity_score = self._assess_commodity_risk(
            industry_data, risk_factors
        )
        
        # Requirement 9.4: Calculate Conditions score (0-100)
        # Weighted average: 35% sector, 40% regulatory, 25% commodity
        conditions_score = (
            sector_score * 0.35 +
            regulatory_score * 0.40 +
            commodity_score * 0.25
        )
        
        # Factor in sentiment (positive sentiment improves score, negative worsens it)
        # Sentiment ranges from -1 to 1, so multiply by 15 for -15 to +15 adjustment
        sentiment_adjustment = sentiment.overall * 15
        conditions_score += sentiment_adjustment
        
        # Ensure score is within 0-100 range
        conditions_score = max(0.0, min(100.0, conditions_score))
        
        return ConditionsScore(
            score=conditions_score,
            sector_risk=sector_risk,
            regulatory_risk=regulatory_risk,
            commodity_risk=commodity_risk,
            risk_factors=risk_factors,
        )

    def _assess_sector_risk(
        self, industry_data: Dict, risk_factors: List[str]
    ) -> tuple[str, float]:
        """
        Assess sector-specific risks from industry data.
        
        Requirement 9.1: Analyze sector-specific risks from industry reports
        
        Returns tuple of (risk_level_string, score_0_to_100).
        """
        sector = industry_data.get("sector", "Unknown")
        growth_rate = industry_data.get("growth_rate", 0.0)
        volatility = industry_data.get("volatility", 0.5)
        
        score = 100.0
        
        # Assess growth rate
        if growth_rate < -5.0:
            # Negative growth - high risk
            score -= 30
            risk_factors.append(f"Sector declining at {growth_rate:.1f}% annually")
            risk_level = "High"
        elif growth_rate < 0.0:
            # Slight negative growth
            score -= 15
            risk_factors.append(f"Sector showing slight decline at {growth_rate:.1f}%")
            risk_level = "Medium"
        elif growth_rate < 3.0:
            # Low growth
            score -= 10
            risk_factors.append(f"Sector growth below 3% at {growth_rate:.1f}%")
            risk_level = "Medium"
        elif growth_rate < 7.0:
            # Moderate growth
            risk_level = "Low"
        else:
            # Strong growth
            score += 5
            risk_level = "Low"
        
        # Assess volatility (0.0 = stable, 1.0 = highly volatile)
        if volatility > 0.7:
            # High volatility
            score -= 20
            risk_factors.append(f"High sector volatility ({volatility:.2f})")
            risk_level = "High"
        elif volatility > 0.5:
            # Moderate volatility
            score -= 10
            risk_factors.append(f"Moderate sector volatility ({volatility:.2f})")
            if risk_level != "High":
                risk_level = "Medium"
        elif volatility > 0.3:
            # Low volatility
            if risk_level == "Low":
                score += 5
        
        # Ensure score is within 0-100
        score = max(0.0, min(100.0, score))
        
        return risk_level, score

    def _assess_regulatory_risk(
        self, rbi_notifications: List[RBINotification], risk_factors: List[str]
    ) -> tuple[str, float]:
        """
        Assess regulatory risk from RBI notifications and policy changes.
        
        Requirement 9.2: Check RBI notifications and policy changes
        
        Returns tuple of (risk_level_string, score_0_to_100).
        """
        score = 100.0
        risk_level = "Low"
        
        if not rbi_notifications:
            # No recent notifications - assume stable regulatory environment
            return risk_level, score
        
        # Categorize notifications by severity
        high_severity_notifications = []
        medium_severity_notifications = []
        low_severity_notifications = []
        
        for notification in rbi_notifications:
            title_lower = notification.title.lower()
            content_lower = notification.content.lower()
            
            # High severity: restrictions, bans, tightening, increased requirements
            if any(keyword in title_lower or keyword in content_lower 
                   for keyword in ['ban', 'restrict', 'tighten', 'increase', 'mandatory', 'compliance']):
                high_severity_notifications.append(notification)
            # Medium severity: guidelines, advisory, monitoring
            elif any(keyword in title_lower or keyword in content_lower 
                     for keyword in ['guideline', 'advisory', 'monitor', 'review', 'caution']):
                medium_severity_notifications.append(notification)
            # Low severity: informational, clarification
            else:
                low_severity_notifications.append(notification)
        
        # Document risk factors (Requirement 9.5)
        if high_severity_notifications:
            score -= 25
            risk_level = "High"
            risk_factors.append(
                f"{len(high_severity_notifications)} high-severity RBI notification(s): "
                f"{', '.join(n.title for n in high_severity_notifications[:2])}"
            )
        
        if medium_severity_notifications:
            score -= 10
            if risk_level == "Low":
                risk_level = "Medium"
            risk_factors.append(
                f"{len(medium_severity_notifications)} medium-severity RBI notification(s)"
            )
        
        if low_severity_notifications:
            score -= 3
            risk_factors.append(
                f"{len(low_severity_notifications)} informational RBI notification(s)"
            )
        
        # Ensure score is within 0-100
        score = max(0.0, min(100.0, score))
        
        return risk_level, score

    def _assess_commodity_risk(
        self, industry_data: Dict, risk_factors: List[str]
    ) -> tuple[str, float]:
        """
        Assess commodity price volatility risks.
        
        Requirement 9.3: Assess commodity price volatility risks
        
        Returns tuple of (risk_level_string, score_0_to_100).
        """
        score = 100.0
        risk_level = "Low"
        
        # Check if company has commodity exposure
        commodity_exposure = industry_data.get("commodity_exposure", False)
        
        if not commodity_exposure:
            # No commodity exposure - no risk
            return risk_level, score
        
        # Get commodity volatility data
        commodity_volatility = industry_data.get("commodity_volatility", 0.0)
        commodity_types = industry_data.get("commodity_types", [])
        
        # Assess volatility level
        if commodity_volatility > 0.6:
            # High volatility
            score -= 25
            risk_level = "High"
            risk_factors.append(
                f"High commodity price volatility ({commodity_volatility:.2f}) for: "
                f"{', '.join(commodity_types[:3])}"
            )
        elif commodity_volatility > 0.4:
            # Moderate volatility
            score -= 15
            risk_level = "Medium"
            risk_factors.append(
                f"Moderate commodity price volatility ({commodity_volatility:.2f})"
            )
        elif commodity_volatility > 0.2:
            # Low volatility
            score -= 5
            risk_factors.append(
                f"Low commodity price volatility ({commodity_volatility:.2f})"
            )
        
        # Ensure score is within 0-100
        score = max(0.0, min(100.0, score))
        
        return risk_level, score
