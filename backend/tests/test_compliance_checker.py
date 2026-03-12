"""Unit tests for ComplianceChecker class."""

import pytest
from datetime import datetime, timedelta

from app.services.research_agent.compliance_checker import (
    ComplianceChecker,
    ComplianceStatus,
    DisqualificationRecord
)
from app.models.research import MCAData


class TestComplianceChecker:
    """Test suite for ComplianceChecker class."""
    
    @pytest.fixture
    def checker(self):
        """Create ComplianceChecker instance for testing."""
        return ComplianceChecker(
            filing_threshold_days=90,
            warning_threshold_days=60
        )
    
    @pytest.fixture
    def compliant_mca_data(self):
        """Create compliant MCA data for testing."""
        return MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="Active",
            directors=[
                {"name": "John Doe", "din": "12345678"},
                {"name": "Jane Smith", "din": "87654321"}
            ]
        )
    
    @pytest.fixture
    def non_compliant_mca_data(self):
        """Create non-compliant MCA data for testing."""
        return MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=120),
            compliance_status="Non-Compliant",
            directors=[]
        )
    
    def test_initialization(self, checker):
        """Test ComplianceChecker initialization."""
        assert checker.filing_threshold_days == 90
        assert checker.warning_threshold_days == 60
    
    def test_initialization_custom_thresholds(self):
        """Test initialization with custom thresholds."""
        checker = ComplianceChecker(
            filing_threshold_days=120,
            warning_threshold_days=90
        )
        assert checker.filing_threshold_days == 120
        assert checker.warning_threshold_days == 90
    
    def test_check_mca_compliance_compliant(self, checker, compliant_mca_data):
        """Test MCA compliance check with compliant data."""
        result = checker.check_mca_compliance(compliant_mca_data)
        
        assert isinstance(result, ComplianceStatus)
        assert result.is_compliant is True
        assert result.compliance_level == "compliant"
        assert result.last_filing_date is not None
        assert result.days_since_filing is not None
        assert result.days_since_filing < 90
        assert len(result.issues) == 0
    
    def test_check_mca_compliance_non_compliant(self, checker, non_compliant_mca_data):
        """Test MCA compliance check with non-compliant data."""
        result = checker.check_mca_compliance(non_compliant_mca_data)
        
        assert isinstance(result, ComplianceStatus)
        assert result.is_compliant is False
        assert result.compliance_level == "non-compliant"
        assert result.last_filing_date is not None
        assert result.days_since_filing > 90
        assert len(result.issues) > 0
        # Should have issues for both overdue filing and non-compliant status
        assert any("days ago" in issue for issue in result.issues)
        assert any("compliance status" in issue.lower() for issue in result.issues)
    
    def test_check_mca_compliance_warning_level(self, checker):
        """Test MCA compliance check with warning level."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=70),
            compliance_status="Active",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        assert result.is_compliant is True
        assert result.compliance_level == "warning"
        assert len(result.issues) > 0
        assert any("approaching deadline" in issue.lower() for issue in result.issues)
    
    def test_check_mca_compliance_no_filing_date(self, checker):
        """Test MCA compliance check with missing filing date."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=None,
            compliance_status="Active",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        assert result.is_compliant is False
        assert result.compliance_level == "non-compliant"
        assert result.last_filing_date is None
        assert result.days_since_filing is None
        assert any("no filing date" in issue.lower() for issue in result.issues)
    
    def test_check_mca_compliance_no_data(self, checker):
        """Test MCA compliance check with no data."""
        result = checker.check_mca_compliance(None)
        
        assert result.is_compliant is False
        assert result.compliance_level == "non-compliant"
        assert result.last_filing_date is None
        assert result.days_since_filing is None
        assert len(result.issues) == 1
        assert "no mca data" in result.issues[0].lower()
    
    def test_check_mca_compliance_inactive_company(self, checker):
        """Test MCA compliance check with inactive company."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="Inactive",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        assert result.is_compliant is False
        assert result.compliance_level == "non-compliant"
        assert any("inactive" in issue.lower() for issue in result.issues)
    
    def test_check_mca_compliance_strike_off(self, checker):
        """Test MCA compliance check with strike-off status."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="Strike-Off",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        assert result.is_compliant is False
        assert result.compliance_level == "non-compliant"
        assert any("compliance status" in issue.lower() for issue in result.issues)
    
    def test_check_mca_compliance_defaulter(self, checker):
        """Test MCA compliance check with defaulter status."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="Defaulter",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        assert result.is_compliant is False
        assert result.compliance_level == "non-compliant"
    
    def test_check_mca_compliance_pending_status(self, checker):
        """Test MCA compliance check with pending status."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=30),
            compliance_status="Pending",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        assert result.compliance_level == "warning"
        assert any("compliance status" in issue.lower() for issue in result.issues)
    
    def test_check_director_disqualification_empty_list(self, checker):
        """Test director disqualification check with empty list."""
        result = checker.check_director_disqualification([])
        
        assert result == []
    
    def test_check_director_disqualification_single_director(self, checker):
        """Test director disqualification check with single director."""
        directors = ["John Doe (DIN: 12345678)"]
        
        result = checker.check_director_disqualification(directors)
        
        assert len(result) == 1
        assert isinstance(result[0], DisqualificationRecord)
        assert result[0].director_name == "John Doe"
        assert result[0].din == "12345678"
        assert result[0].is_disqualified is False
        assert result[0].disqualification_reason is None
    
    def test_check_director_disqualification_multiple_directors(self, checker):
        """Test director disqualification check with multiple directors."""
        directors = [
            "John Doe (DIN: 12345678)",
            "Jane Smith (DIN: 87654321)",
            "Bob Johnson (DIN: 11223344)"
        ]
        
        result = checker.check_director_disqualification(directors)
        
        assert len(result) == 3
        assert all(isinstance(r, DisqualificationRecord) for r in result)
        assert result[0].director_name == "John Doe"
        assert result[1].director_name == "Jane Smith"
        assert result[2].director_name == "Bob Johnson"
    
    def test_check_director_disqualification_din_formats(self, checker):
        """Test director disqualification check with various DIN formats."""
        directors = [
            "John Doe (DIN: 12345678)",
            "Jane Smith (DIN:87654321)",
            "Bob Johnson DIN 11223344",
            "Alice Brown DIN:22334455"
        ]
        
        result = checker.check_director_disqualification(directors)
        
        assert len(result) == 4
        assert result[0].din == "12345678"
        assert result[1].din == "87654321"
        assert result[2].din == "11223344"
        assert result[3].din == "22334455"
    
    def test_check_director_disqualification_no_din(self, checker):
        """Test director disqualification check without DIN."""
        directors = ["John Doe"]
        
        result = checker.check_director_disqualification(directors)
        
        assert len(result) == 1
        assert result[0].director_name == "John Doe"
        assert result[0].din == "Unknown"
    
    def test_check_director_disqualification_din_only(self, checker):
        """Test director disqualification check with DIN only."""
        directors = ["12345678"]
        
        result = checker.check_director_disqualification(directors)
        
        assert len(result) == 1
        assert result[0].din == "12345678"
        assert result[0].director_name == "12345678"
    
    def test_extract_din_various_formats(self, checker):
        """Test DIN extraction from various formats."""
        assert checker._extract_din("John Doe (DIN: 12345678)") == "12345678"
        assert checker._extract_din("John Doe (DIN:12345678)") == "12345678"
        assert checker._extract_din("John Doe DIN 12345678") == "12345678"
        assert checker._extract_din("John Doe DIN:12345678") == "12345678"
        assert checker._extract_din("12345678") == "12345678"
        assert checker._extract_din("John Doe") is None
    
    def test_extract_name_removes_din(self, checker):
        """Test name extraction removes DIN information."""
        assert checker._extract_name("John Doe (DIN: 12345678)") == "John Doe"
        assert checker._extract_name("John Doe (DIN:12345678)") == "John Doe"
        assert checker._extract_name("John Doe DIN 12345678") == "John Doe"
        assert checker._extract_name("John Doe DIN:12345678") == "John Doe"
        assert checker._extract_name("John Doe") == "John Doe"
    
    def test_extract_name_preserves_spaces(self, checker):
        """Test name extraction preserves proper spacing."""
        assert checker._extract_name("  John Doe  ") == "John Doe"
        assert checker._extract_name("John Doe (DIN: 12345678)  ") == "John Doe"
    
    def test_check_disqualification_status_placeholder(self, checker):
        """Test disqualification status check (placeholder implementation)."""
        is_disqualified, reason, date, period = checker._check_disqualification_status(
            "John Doe", "12345678"
        )
        
        # Placeholder should return not disqualified
        assert is_disqualified is False
        assert reason is None
        assert date is None
        assert period is None
    
    def test_compliance_status_dataclass(self):
        """Test ComplianceStatus dataclass."""
        status = ComplianceStatus(
            is_compliant=True,
            last_filing_date=datetime(2024, 1, 15),
            days_since_filing=30,
            issues=[],
            compliance_level="compliant"
        )
        
        assert status.is_compliant is True
        assert status.last_filing_date == datetime(2024, 1, 15)
        assert status.days_since_filing == 30
        assert status.issues == []
        assert status.compliance_level == "compliant"
    
    def test_disqualification_record_dataclass(self):
        """Test DisqualificationRecord dataclass."""
        record = DisqualificationRecord(
            director_name="John Doe",
            din="12345678",
            is_disqualified=True,
            disqualification_reason="Section 164(2) violation",
            disqualification_date=datetime(2023, 1, 1),
            disqualification_period=5
        )
        
        assert record.director_name == "John Doe"
        assert record.din == "12345678"
        assert record.is_disqualified is True
        assert record.disqualification_reason == "Section 164(2) violation"
        assert record.disqualification_date == datetime(2023, 1, 1)
        assert record.disqualification_period == 5
    
    def test_check_mca_compliance_edge_case_exact_threshold(self, checker):
        """Test compliance check at exact threshold boundary."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=90),
            compliance_status="Active",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        # At exactly 90 days, should still be compliant (not > 90)
        assert result.is_compliant is True
    
    def test_check_mca_compliance_edge_case_one_day_over(self, checker):
        """Test compliance check one day over threshold."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=91),
            compliance_status="Active",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        # At 91 days, should be non-compliant
        assert result.is_compliant is False
        assert result.compliance_level == "non-compliant"
    
    def test_check_mca_compliance_multiple_issues(self, checker):
        """Test compliance check with multiple issues."""
        mca_data = MCAData(
            cin="L12345AB2020PLC123456",
            company_name="Test Company Ltd",
            registration_date=datetime(2020, 1, 1),
            authorized_capital=10000000.0,
            paid_up_capital=5000000.0,
            last_filing_date=datetime.now() - timedelta(days=120),
            compliance_status="Non-Compliant",
            directors=[]
        )
        
        result = checker.check_mca_compliance(mca_data)
        
        # Should have multiple issues
        assert len(result.issues) >= 2
        assert result.is_compliant is False
    
    def test_check_director_disqualification_mixed_formats(self, checker):
        """Test director disqualification with mixed name formats."""
        directors = [
            "John Doe (DIN: 12345678)",
            "Jane Smith",
            "87654321",
            "Bob Johnson DIN:11223344"
        ]
        
        result = checker.check_director_disqualification(directors)
        
        assert len(result) == 4
        assert result[0].director_name == "John Doe"
        assert result[0].din == "12345678"
        assert result[1].director_name == "Jane Smith"
        assert result[1].din == "Unknown"
        assert result[2].din == "87654321"
        assert result[3].director_name == "Bob Johnson"
        assert result[3].din == "11223344"
