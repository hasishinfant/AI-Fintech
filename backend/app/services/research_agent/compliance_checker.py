"""Compliance checking for MCA filings and director disqualification."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.research import MCAData

logger = logging.getLogger(__name__)


@dataclass
class ComplianceStatus:
    """MCA compliance status result."""
    is_compliant: bool
    last_filing_date: Optional[datetime]
    days_since_filing: Optional[int]
    issues: List[str] = field(default_factory=list)
    compliance_level: str = "compliant"  # "compliant", "warning", "non-compliant"


@dataclass
class DisqualificationRecord:
    """Director disqualification record."""
    director_name: str
    din: str
    is_disqualified: bool
    disqualification_reason: Optional[str] = None
    disqualification_date: Optional[datetime] = None
    disqualification_period: Optional[int] = None  # in years


class ComplianceChecker:
    """
    Compliance checker for MCA filings and director disqualification.
    
    Implements check_mca_compliance() for filing status verification and
    check_director_disqualification() for director checks.
    
    Requirements: 4.3
    """
    
    def __init__(
        self,
        filing_threshold_days: int = 90,
        warning_threshold_days: int = 60
    ):
        """
        Initialize ComplianceChecker with threshold configuration.
        
        Args:
            filing_threshold_days: Days after which non-filing is considered non-compliant
            warning_threshold_days: Days after which to issue a warning
        """
        self.filing_threshold_days = filing_threshold_days
        self.warning_threshold_days = warning_threshold_days
    
    def check_mca_compliance(self, mca_data: MCAData) -> ComplianceStatus:
        """
        Verify MCA filing compliance status.
        
        Checks if the company is compliant with MCA filing requirements by
        examining the last filing date and compliance status from MCA data.
        Flags non-compliance if filings are overdue.
        
        Args:
            mca_data: MCAData object containing company filing information
            
        Returns:
            ComplianceStatus with compliance determination, issues, and level
            
        Requirements: 4.3
        """
        if not mca_data:
            logger.warning("No MCA data provided for compliance check")
            return ComplianceStatus(
                is_compliant=False,
                last_filing_date=None,
                days_since_filing=None,
                issues=["No MCA data available"],
                compliance_level="non-compliant"
            )
        
        issues = []
        is_compliant = True
        compliance_level = "compliant"
        
        # Check last filing date
        last_filing_date = mca_data.last_filing_date
        days_since_filing = None
        
        if last_filing_date:
            days_since_filing = (datetime.now() - last_filing_date).days
            
            # Check if filing is overdue
            if days_since_filing > self.filing_threshold_days:
                is_compliant = False
                compliance_level = "non-compliant"
                issues.append(
                    f"Last MCA filing was {days_since_filing} days ago "
                    f"(threshold: {self.filing_threshold_days} days)"
                )
            elif days_since_filing > self.warning_threshold_days:
                compliance_level = "warning"
                issues.append(
                    f"MCA filing approaching deadline: {days_since_filing} days since last filing"
                )
        else:
            is_compliant = False
            compliance_level = "non-compliant"
            issues.append("No filing date available in MCA records")
        
        # Check compliance status from MCA data
        if mca_data.compliance_status:
            status_lower = mca_data.compliance_status.lower()
            
            if status_lower in ["non-compliant", "defaulter", "strike-off"]:
                is_compliant = False
                compliance_level = "non-compliant"
                issues.append(f"MCA compliance status: {mca_data.compliance_status}")
            elif status_lower in ["warning", "pending"]:
                if compliance_level == "compliant":
                    compliance_level = "warning"
                issues.append(f"MCA compliance status: {mca_data.compliance_status}")
        
        # Check if company is active
        if mca_data.compliance_status and "inactive" in mca_data.compliance_status.lower():
            is_compliant = False
            compliance_level = "non-compliant"
            issues.append("Company status is inactive")
        
        compliance_status = ComplianceStatus(
            is_compliant=is_compliant,
            last_filing_date=last_filing_date,
            days_since_filing=days_since_filing,
            issues=issues,
            compliance_level=compliance_level
        )
        
        logger.info(
            f"MCA compliance check for {mca_data.company_name} (CIN: {mca_data.cin}): "
            f"{compliance_level} - {len(issues)} issues found"
        )
        
        return compliance_status
    
    def check_director_disqualification(
        self,
        directors: List[str]
    ) -> List[DisqualificationRecord]:
        """
        Check if directors are disqualified.
        
        Verifies whether any of the provided directors are disqualified under
        Section 164(2) of the Companies Act, 2013. Checks against MCA's
        disqualified directors database.
        
        Args:
            directors: List of director names or DINs to check
            
        Returns:
            List of DisqualificationRecord objects, one per director
            
        Requirements: 4.3
        """
        if not directors:
            logger.warning("No directors provided for disqualification check")
            return []
        
        disqualification_records = []
        
        for director in directors:
            # Extract DIN if provided in format "Name (DIN: 12345678)"
            din = self._extract_din(director)
            director_name = self._extract_name(director)
            
            # Check disqualification status
            # In production, this would query MCA's disqualified directors database
            # For now, we'll implement a placeholder that returns not disqualified
            is_disqualified, reason, date, period = self._check_disqualification_status(
                director_name, din
            )
            
            record = DisqualificationRecord(
                director_name=director_name,
                din=din or "Unknown",
                is_disqualified=is_disqualified,
                disqualification_reason=reason,
                disqualification_date=date,
                disqualification_period=period
            )
            
            disqualification_records.append(record)
            
            if is_disqualified:
                logger.warning(
                    f"Director {director_name} (DIN: {din}) is disqualified: {reason}"
                )
        
        disqualified_count = sum(1 for r in disqualification_records if r.is_disqualified)
        logger.info(
            f"Checked {len(directors)} directors: "
            f"{disqualified_count} disqualified, "
            f"{len(directors) - disqualified_count} clear"
        )
        
        return disqualification_records
    
    def _extract_din(self, director_info: str) -> Optional[str]:
        """
        Extract DIN from director information string.
        
        Args:
            director_info: Director information (may contain DIN)
            
        Returns:
            DIN string if found, None otherwise
        """
        import re
        
        # Try to extract DIN from formats like "Name (DIN: 12345678)" or "DIN12345678"
        din_match = re.search(r"DIN[:\s]*(\d{8})", director_info, re.IGNORECASE)
        if din_match:
            return din_match.group(1)
        
        # Check if the string itself is a DIN (8 digits)
        if re.match(r"^\d{8}$", director_info.strip()):
            return director_info.strip()
        
        return None
    
    def _extract_name(self, director_info: str) -> str:
        """
        Extract director name from director information string.
        
        Args:
            director_info: Director information
            
        Returns:
            Director name
        """
        import re
        
        # Remove DIN information if present
        name = re.sub(r"\(DIN[:\s]*\d{8}\)", "", director_info, flags=re.IGNORECASE)
        name = re.sub(r"DIN[:\s]*\d{8}", "", name, flags=re.IGNORECASE)
        
        return name.strip()
    
    def _check_disqualification_status(
        self,
        director_name: str,
        din: Optional[str]
    ) -> tuple[bool, Optional[str], Optional[datetime], Optional[int]]:
        """
        Check director disqualification status against MCA database.
        
        In production, this would query the MCA API or disqualified directors
        database. For now, returns a placeholder implementation.
        
        Args:
            director_name: Name of the director
            din: Director Identification Number
            
        Returns:
            Tuple of (is_disqualified, reason, date, period_in_years)
        """
        # Placeholder implementation
        # In production, would make API call to MCA disqualified directors database
        # Example: https://www.mca.gov.in/content/mca/global/en/data-and-reports/
        #          disqualified-directors.html
        
        # For now, return not disqualified
        # This would be replaced with actual API integration
        
        logger.debug(
            f"Checking disqualification status for {director_name} "
            f"(DIN: {din or 'N/A'})"
        )
        
        # Placeholder: No disqualification found
        return False, None, None, None

