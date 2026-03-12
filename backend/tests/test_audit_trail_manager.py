"""Tests for AuditTrailManager."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, MagicMock, call

from app.services.credit_engine.audit_trail_manager import AuditTrailManager
from app.models.cam import AuditEvent, AuditTrail


@pytest.fixture
def mock_audit_repository():
    """Create a mock audit repository."""
    return Mock()


@pytest.fixture
def audit_manager(mock_audit_repository):
    """Create an AuditTrailManager instance with mock repository."""
    return AuditTrailManager(mock_audit_repository)


class TestRecordDataIngestion:
    """Tests for record_data_ingestion method."""

    def test_record_data_ingestion_basic(self, audit_manager):
        """Test recording a basic data ingestion event."""
        source = "GST_RETURN"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        method = "STRUCTURED_PARSER"
        
        event = audit_manager.record_data_ingestion(
            source=source,
            timestamp=timestamp,
            method=method
        )
        
        assert event.event_type == "DATA_INGESTION"
        assert event.timestamp == timestamp
        assert event.data["source"] == source
        assert event.data["method"] == method
        assert f"{source}" in event.description
        assert f"{method}" in event.description

    def test_record_data_ingestion_with_application_id(self, audit_manager, mock_audit_repository):
        """Test recording data ingestion with application ID persists to database."""
        source = "BANK_STATEMENT"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        method = "OCR"
        application_id = uuid4()
        user_id = uuid4()
        
        event = audit_manager.record_data_ingestion(
            source=source,
            timestamp=timestamp,
            method=method,
            application_id=application_id,
            user_id=user_id
        )
        
        # Verify database persistence was called
        mock_audit_repository.create_audit_event.assert_called_once()
        call_kwargs = mock_audit_repository.create_audit_event.call_args[1]
        assert call_kwargs["event_type"] == "DATA_INGESTION"
        assert call_kwargs["application_id"] == application_id
        assert call_kwargs["user_id"] == user_id
        assert call_kwargs["timestamp"] == timestamp

    def test_record_data_ingestion_with_additional_data(self, audit_manager):
        """Test recording data ingestion with additional metadata."""
        source = "ANNUAL_REPORT"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        method = "PDF_PARSER"
        additional_data = {"file_name": "report_2023.pdf", "pages": 45}
        
        event = audit_manager.record_data_ingestion(
            source=source,
            timestamp=timestamp,
            method=method,
            additional_data=additional_data
        )
        
        assert event.data["file_name"] == "report_2023.pdf"
        assert event.data["pages"] == 45

    def test_record_data_ingestion_multiple_events(self, audit_manager):
        """Test recording multiple data ingestion events."""
        timestamp1 = datetime(2024, 1, 15, 10, 0, 0)
        timestamp2 = datetime(2024, 1, 15, 11, 0, 0)
        
        event1 = audit_manager.record_data_ingestion(
            source="GST_RETURN",
            timestamp=timestamp1,
            method="STRUCTURED_PARSER"
        )
        
        event2 = audit_manager.record_data_ingestion(
            source="BANK_STATEMENT",
            timestamp=timestamp2,
            method="OCR"
        )
        
        trail = audit_manager.get_audit_trail()
        assert len(trail.events) == 2
        assert trail.events[0] == event1
        assert trail.events[1] == event2


class TestRecordResearchActivity:
    """Tests for record_research_activity method."""

    def test_record_research_activity_basic(self, audit_manager):
        """Test recording a basic research activity event."""
        url = "https://www.mca.gov.in/company/ABC123"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        data_retrieved = "MCA filing data"
        
        event = audit_manager.record_research_activity(
            url=url,
            timestamp=timestamp,
            data_retrieved=data_retrieved
        )
        
        assert event.event_type == "RESEARCH_ACTIVITY"
        assert event.timestamp == timestamp
        assert event.data["url"] == url
        assert event.data["data_retrieved"] == data_retrieved
        assert url in event.description
        assert data_retrieved in event.description

    def test_record_research_activity_with_application_id(self, audit_manager, mock_audit_repository):
        """Test recording research activity with application ID persists to database."""
        url = "https://news.example.com/company-news"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        data_retrieved = "News articles"
        application_id = uuid4()
        user_id = uuid4()
        
        event = audit_manager.record_research_activity(
            url=url,
            timestamp=timestamp,
            data_retrieved=data_retrieved,
            application_id=application_id,
            user_id=user_id
        )
        
        # Verify database persistence was called
        mock_audit_repository.create_audit_event.assert_called_once()
        call_kwargs = mock_audit_repository.create_audit_event.call_args[1]
        assert call_kwargs["event_type"] == "RESEARCH_ACTIVITY"
        assert call_kwargs["application_id"] == application_id
        assert call_kwargs["user_id"] == user_id

    def test_record_research_activity_with_additional_data(self, audit_manager):
        """Test recording research activity with additional metadata."""
        url = "https://ecourts.gov.in/case/123"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        data_retrieved = "Litigation records"
        additional_data = {"case_count": 2, "status": "active"}
        
        event = audit_manager.record_research_activity(
            url=url,
            timestamp=timestamp,
            data_retrieved=data_retrieved,
            additional_data=additional_data
        )
        
        assert event.data["case_count"] == 2
        assert event.data["status"] == "active"

    def test_record_research_activity_multiple_urls(self, audit_manager):
        """Test recording research activities from multiple URLs."""
        timestamp1 = datetime(2024, 1, 15, 10, 0, 0)
        timestamp2 = datetime(2024, 1, 15, 11, 0, 0)
        
        event1 = audit_manager.record_research_activity(
            url="https://mca.gov.in/company/ABC",
            timestamp=timestamp1,
            data_retrieved="MCA data"
        )
        
        event2 = audit_manager.record_research_activity(
            url="https://news.example.com/abc",
            timestamp=timestamp2,
            data_retrieved="News articles"
        )
        
        trail = audit_manager.get_audit_trail()
        assert len(trail.events) == 2
        assert trail.events[0].data["url"] == "https://mca.gov.in/company/ABC"
        assert trail.events[1].data["url"] == "https://news.example.com/abc"


class TestRecordCalculation:
    """Tests for record_calculation method."""

    def test_record_calculation_basic(self, audit_manager):
        """Test recording a basic calculation event."""
        calculation_type = "DSCR"
        formula = "cash_flow / debt_service"
        inputs = {"cash_flow": 1000000, "debt_service": 800000}
        output = 1.25
        
        event = audit_manager.record_calculation(
            calculation_type=calculation_type,
            formula=formula,
            inputs=inputs,
            output=output
        )
        
        assert event.event_type == "CALCULATION"
        assert event.data["calculation_type"] == calculation_type
        assert event.data["formula"] == formula
        assert event.data["inputs"] == inputs
        assert event.data["output"] == output
        assert calculation_type in event.description
        assert str(output) in event.description

    def test_record_calculation_with_application_id(self, audit_manager, mock_audit_repository):
        """Test recording calculation with application ID persists to database."""
        calculation_type = "DEBT_EQUITY_RATIO"
        formula = "total_debt / total_equity"
        inputs = {"total_debt": 5000000, "total_equity": 3000000}
        output = 1.67
        application_id = uuid4()
        user_id = uuid4()
        
        event = audit_manager.record_calculation(
            calculation_type=calculation_type,
            formula=formula,
            inputs=inputs,
            output=output,
            application_id=application_id,
            user_id=user_id
        )
        
        # Verify database persistence was called
        mock_audit_repository.create_audit_event.assert_called_once()
        call_kwargs = mock_audit_repository.create_audit_event.call_args[1]
        assert call_kwargs["event_type"] == "CALCULATION"
        assert call_kwargs["application_id"] == application_id

    def test_record_calculation_with_additional_data(self, audit_manager):
        """Test recording calculation with additional metadata."""
        calculation_type = "LTV"
        formula = "loan_amount / collateral_value"
        inputs = {"loan_amount": 1000000, "collateral_value": 1500000}
        output = 0.67
        additional_data = {"collateral_type": "property", "valuation_date": "2024-01-15"}
        
        event = audit_manager.record_calculation(
            calculation_type=calculation_type,
            formula=formula,
            inputs=inputs,
            output=output,
            additional_data=additional_data
        )
        
        assert event.data["collateral_type"] == "property"
        assert event.data["valuation_date"] == "2024-01-15"

    def test_record_calculation_multiple_calculations(self, audit_manager):
        """Test recording multiple calculation events."""
        event1 = audit_manager.record_calculation(
            calculation_type="DSCR",
            formula="cash_flow / debt_service",
            inputs={"cash_flow": 1000000, "debt_service": 800000},
            output=1.25
        )
        
        event2 = audit_manager.record_calculation(
            calculation_type="DEBT_EQUITY_RATIO",
            formula="total_debt / total_equity",
            inputs={"total_debt": 5000000, "total_equity": 3000000},
            output=1.67
        )
        
        trail = audit_manager.get_audit_trail()
        assert len(trail.events) == 2
        assert trail.events[0].data["calculation_type"] == "DSCR"
        assert trail.events[1].data["calculation_type"] == "DEBT_EQUITY_RATIO"


class TestRecordModification:
    """Tests for record_modification method."""

    def test_record_modification_basic(self, audit_manager):
        """Test recording a basic modification event."""
        user = "credit_officer_001"
        field = "loan_amount"
        old_value = 1000000
        new_value = 1200000
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        event = audit_manager.record_modification(
            user=user,
            field=field,
            old_value=old_value,
            new_value=new_value,
            timestamp=timestamp
        )
        
        assert event.event_type == "MODIFICATION"
        assert event.timestamp == timestamp
        assert event.user == user
        assert event.data["field"] == field
        assert event.data["old_value"] == old_value
        assert event.data["new_value"] == new_value
        assert field in event.description
        assert user in event.description

    def test_record_modification_with_application_id(self, audit_manager, mock_audit_repository):
        """Test recording modification with application ID persists to database."""
        user = "credit_officer_001"
        field = "interest_rate"
        old_value = 8.5
        new_value = 9.0
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        application_id = uuid4()
        user_id = uuid4()
        
        event = audit_manager.record_modification(
            user=user,
            field=field,
            old_value=old_value,
            new_value=new_value,
            timestamp=timestamp,
            application_id=application_id,
            user_id=user_id
        )
        
        # Verify database persistence was called
        mock_audit_repository.create_audit_event.assert_called_once()
        call_kwargs = mock_audit_repository.create_audit_event.call_args[1]
        assert call_kwargs["event_type"] == "MODIFICATION"
        assert call_kwargs["application_id"] == application_id
        assert call_kwargs["user_id"] == user_id

    def test_record_modification_with_additional_data(self, audit_manager):
        """Test recording modification with additional metadata."""
        user = "credit_officer_001"
        field = "risk_score"
        old_value = 45
        new_value = 50
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        additional_data = {"reason": "Updated based on new financial data", "approved_by": "manager_001"}
        
        event = audit_manager.record_modification(
            user=user,
            field=field,
            old_value=old_value,
            new_value=new_value,
            timestamp=timestamp,
            additional_data=additional_data
        )
        
        assert event.data["reason"] == "Updated based on new financial data"
        assert event.data["approved_by"] == "manager_001"

    def test_record_modification_multiple_modifications(self, audit_manager):
        """Test recording multiple modification events."""
        timestamp1 = datetime(2024, 1, 15, 10, 0, 0)
        timestamp2 = datetime(2024, 1, 15, 11, 0, 0)
        
        event1 = audit_manager.record_modification(
            user="officer_1",
            field="loan_amount",
            old_value=1000000,
            new_value=1200000,
            timestamp=timestamp1
        )
        
        event2 = audit_manager.record_modification(
            user="officer_2",
            field="interest_rate",
            old_value=8.5,
            new_value=9.0,
            timestamp=timestamp2
        )
        
        trail = audit_manager.get_audit_trail()
        assert len(trail.events) == 2
        assert trail.events[0].data["field"] == "loan_amount"
        assert trail.events[1].data["field"] == "interest_rate"

    def test_record_modification_string_values(self, audit_manager):
        """Test recording modification with string values."""
        user = "credit_officer_001"
        field = "status"
        old_value = "PENDING"
        new_value = "APPROVED"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        event = audit_manager.record_modification(
            user=user,
            field=field,
            old_value=old_value,
            new_value=new_value,
            timestamp=timestamp
        )
        
        assert event.data["old_value"] == "PENDING"
        assert event.data["new_value"] == "APPROVED"


class TestAuditTrailIntegration:
    """Integration tests for AuditTrailManager."""

    def test_mixed_event_types(self, audit_manager):
        """Test recording different types of events together."""
        # Record data ingestion
        audit_manager.record_data_ingestion(
            source="GST_RETURN",
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            method="STRUCTURED_PARSER"
        )
        
        # Record research activity
        audit_manager.record_research_activity(
            url="https://mca.gov.in/company/ABC",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            data_retrieved="MCA data"
        )
        
        # Record calculation
        audit_manager.record_calculation(
            calculation_type="DSCR",
            formula="cash_flow / debt_service",
            inputs={"cash_flow": 1000000, "debt_service": 800000},
            output=1.25
        )
        
        # Record modification
        audit_manager.record_modification(
            user="officer_1",
            field="loan_amount",
            old_value=1000000,
            new_value=1200000,
            timestamp=datetime(2024, 1, 15, 11, 0, 0)
        )
        
        trail = audit_manager.get_audit_trail()
        assert len(trail.events) == 4
        assert trail.events[0].event_type == "DATA_INGESTION"
        assert trail.events[1].event_type == "RESEARCH_ACTIVITY"
        assert trail.events[2].event_type == "CALCULATION"
        assert trail.events[3].event_type == "MODIFICATION"

    def test_get_audit_trail_returns_copy(self, audit_manager):
        """Test that get_audit_trail returns a copy of events."""
        audit_manager.record_data_ingestion(
            source="GST_RETURN",
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            method="STRUCTURED_PARSER"
        )
        
        trail1 = audit_manager.get_audit_trail()
        trail2 = audit_manager.get_audit_trail()
        
        # Trails should have same content but be different objects
        assert len(trail1.events) == len(trail2.events)
        assert trail1.events[0].event_type == trail2.events[0].event_type
        # Modifying one trail shouldn't affect the other
        trail1.events.clear()
        assert len(trail2.events) == 1

    def test_clear_events(self, audit_manager):
        """Test clearing in-memory events."""
        audit_manager.record_data_ingestion(
            source="GST_RETURN",
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            method="STRUCTURED_PARSER"
        )
        
        audit_manager.record_research_activity(
            url="https://mca.gov.in/company/ABC",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            data_retrieved="MCA data"
        )
        
        trail = audit_manager.get_audit_trail()
        assert len(trail.events) == 2
        
        audit_manager.clear_events()
        trail = audit_manager.get_audit_trail()
        assert len(trail.events) == 0

    def test_user_field_tracking(self, audit_manager):
        """Test that user information is properly tracked."""
        user_id = uuid4()
        
        audit_manager.record_data_ingestion(
            source="GST_RETURN",
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            method="STRUCTURED_PARSER",
            user_id=user_id
        )
        
        trail = audit_manager.get_audit_trail()
        assert trail.events[0].user == str(user_id)

    def test_timestamp_preservation(self, audit_manager):
        """Test that timestamps are preserved correctly."""
        timestamp = datetime(2024, 1, 15, 14, 30, 45)
        
        event = audit_manager.record_data_ingestion(
            source="GST_RETURN",
            timestamp=timestamp,
            method="STRUCTURED_PARSER"
        )
        
        assert event.timestamp == timestamp
        trail = audit_manager.get_audit_trail()
        assert trail.events[0].timestamp == timestamp

    def test_database_persistence_called_correctly(self, audit_manager, mock_audit_repository):
        """Test that database persistence is called with correct parameters."""
        application_id = uuid4()
        user_id = uuid4()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        audit_manager.record_data_ingestion(
            source="GST_RETURN",
            timestamp=timestamp,
            method="STRUCTURED_PARSER",
            application_id=application_id,
            user_id=user_id,
            additional_data={"file_name": "gst_return.pdf"}
        )
        
        # Verify the call
        mock_audit_repository.create_audit_event.assert_called_once()
        call_kwargs = mock_audit_repository.create_audit_event.call_args[1]
        
        assert call_kwargs["event_type"] == "DATA_INGESTION"
        assert call_kwargs["description"] == "Data ingested from GST_RETURN using STRUCTURED_PARSER"
        assert call_kwargs["application_id"] == application_id
        assert call_kwargs["user_id"] == user_id
        assert call_kwargs["timestamp"] == timestamp
        assert call_kwargs["event_data"]["source"] == "GST_RETURN"
        assert call_kwargs["event_data"]["method"] == "STRUCTURED_PARSER"
        assert call_kwargs["event_data"]["file_name"] == "gst_return.pdf"



class TestAuditTrailPropertyBased:
    """Property-based tests for audit trail completeness.
    
    Feature: intelli-credit, Property 37: Audit Trail Completeness
    Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5
    """

    def test_audit_trail_completeness_data_ingestion(self, audit_manager):
        """For any data ingestion event, the audit trail should record source, timestamp, and method.
        
        Property: For any system operation (data ingestion), the audit trail should record 
        the event with source, timestamp, and operation details.
        """
        from hypothesis import given, strategies as st
        
        @given(
            source=st.sampled_from(["GST_RETURN", "BANK_STATEMENT", "ANNUAL_REPORT", "ITR", "BOARD_MINUTES"]),
            method=st.sampled_from(["OCR", "STRUCTURED_PARSER", "PDF_PARSER", "API"]),
            timestamp=st.datetimes(timezones=st.none())
        )
        def check_data_ingestion_completeness(source, method, timestamp):
            manager = AuditTrailManager(Mock())
            
            event = manager.record_data_ingestion(
                source=source,
                timestamp=timestamp,
                method=method
            )
            
            # Verify all required fields are present
            assert event.event_type == "DATA_INGESTION"
            assert event.timestamp == timestamp
            assert event.data["source"] == source
            assert event.data["method"] == method
            assert event.description is not None
            assert len(event.description) > 0
        
        check_data_ingestion_completeness()

    def test_audit_trail_completeness_research_activity(self, audit_manager):
        """For any research activity event, the audit trail should record URL, timestamp, and data retrieved.
        
        Property: For any system operation (research activity), the audit trail should record 
        the event with URL, timestamp, and data retrieved details.
        """
        from hypothesis import given, strategies as st
        
        @given(
            url=st.text(min_size=10, max_size=200),
            data_retrieved=st.text(min_size=5, max_size=100),
            timestamp=st.datetimes(timezones=st.none())
        )
        def check_research_activity_completeness(url, data_retrieved, timestamp):
            manager = AuditTrailManager(Mock())
            
            event = manager.record_research_activity(
                url=url,
                timestamp=timestamp,
                data_retrieved=data_retrieved
            )
            
            # Verify all required fields are present
            assert event.event_type == "RESEARCH_ACTIVITY"
            assert event.timestamp == timestamp
            assert event.data["url"] == url
            assert event.data["data_retrieved"] == data_retrieved
            assert event.description is not None
            assert len(event.description) > 0
        
        check_research_activity_completeness()

    def test_audit_trail_completeness_calculation(self, audit_manager):
        """For any calculation event, the audit trail should record formula, inputs, and output.
        
        Property: For any system operation (calculation), the audit trail should record 
        the event with formula, inputs, and output details.
        """
        from hypothesis import given, strategies as st
        
        @given(
            calculation_type=st.sampled_from(["DSCR", "DEBT_EQUITY_RATIO", "LTV", "RISK_SCORE"]),
            formula=st.text(min_size=5, max_size=100),
            output=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
        )
        def check_calculation_completeness(calculation_type, formula, output):
            manager = AuditTrailManager(Mock())
            
            inputs = {"input1": 100, "input2": 50}
            event = manager.record_calculation(
                calculation_type=calculation_type,
                formula=formula,
                inputs=inputs,
                output=output
            )
            
            # Verify all required fields are present
            assert event.event_type == "CALCULATION"
            assert event.data["calculation_type"] == calculation_type
            assert event.data["formula"] == formula
            assert event.data["inputs"] == inputs
            assert event.data["output"] == output
            assert event.description is not None
            assert len(event.description) > 0
        
        check_calculation_completeness()

    def test_audit_trail_completeness_modification(self, audit_manager):
        """For any modification event, the audit trail should record user, field, old/new values, and timestamp.
        
        Property: For any system operation (modification), the audit trail should record 
        the event with user, field, before/after values, and timestamp.
        """
        from hypothesis import given, strategies as st
        
        @given(
            user=st.text(min_size=3, max_size=50),
            field=st.text(min_size=3, max_size=50),
            old_value=st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.text()),
            new_value=st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.text()),
            timestamp=st.datetimes(timezones=st.none())
        )
        def check_modification_completeness(user, field, old_value, new_value, timestamp):
            manager = AuditTrailManager(Mock())
            
            event = manager.record_modification(
                user=user,
                field=field,
                old_value=old_value,
                new_value=new_value,
                timestamp=timestamp
            )
            
            # Verify all required fields are present
            assert event.event_type == "MODIFICATION"
            assert event.user == user
            assert event.timestamp == timestamp
            assert event.data["field"] == field
            assert event.data["old_value"] == old_value
            assert event.data["new_value"] == new_value
            assert event.description is not None
            assert len(event.description) > 0
        
        check_modification_completeness()

    def test_audit_trail_all_events_recorded(self, audit_manager):
        """For any sequence of operations, all events should be recorded in the audit trail.
        
        Property: For any sequence of system operations, the audit trail should contain 
        all events in the order they were recorded.
        """
        from hypothesis import given, strategies as st
        
        @given(
            num_events=st.integers(min_value=1, max_value=10)
        )
        def check_all_events_recorded(num_events):
            manager = AuditTrailManager(Mock())
            
            # Record multiple events
            for i in range(num_events):
                manager.record_data_ingestion(
                    source=f"SOURCE_{i}",
                    timestamp=datetime(2024, 1, 15, 10, i, 0),
                    method="PARSER"
                )
            
            trail = manager.get_audit_trail()
            
            # Verify all events are recorded
            assert len(trail.events) == num_events
            for i, event in enumerate(trail.events):
                assert event.data["source"] == f"SOURCE_{i}"
        
        check_all_events_recorded()

    def test_audit_trail_event_order_preserved(self, audit_manager):
        """For any sequence of operations, events should be recorded in chronological order.
        
        Property: For any sequence of system operations, the audit trail should preserve 
        the order in which events were recorded.
        """
        from hypothesis import given, strategies as st
        
        @given(
            timestamps=st.lists(
                st.datetimes(timezones=st.none()),
                min_size=2,
                max_size=10,
                unique=True
            )
        )
        def check_event_order_preserved(timestamps):
            manager = AuditTrailManager(Mock())
            
            # Sort timestamps to ensure they're in order
            sorted_timestamps = sorted(timestamps)
            
            # Record events in order
            for i, ts in enumerate(sorted_timestamps):
                manager.record_data_ingestion(
                    source=f"SOURCE_{i}",
                    timestamp=ts,
                    method="PARSER"
                )
            
            trail = manager.get_audit_trail()
            
            # Verify events are in the same order
            for i, event in enumerate(trail.events):
                assert event.timestamp == sorted_timestamps[i]
        
        check_event_order_preserved()

    def test_audit_trail_database_persistence_completeness(self, audit_manager):
        """For any event with application_id, all event details should be persisted to database.
        
        Property: For any system operation with application_id, the audit trail should 
        persist all event details to the database.
        """
        from hypothesis import given, strategies as st
        
        @given(
            source=st.text(min_size=3, max_size=50),
            method=st.text(min_size=3, max_size=50)
        )
        def check_database_persistence(source, method):
            mock_repo = Mock()
            manager = AuditTrailManager(mock_repo)
            
            application_id = uuid4()
            user_id = uuid4()
            timestamp = datetime(2024, 1, 15, 10, 30, 0)
            
            manager.record_data_ingestion(
                source=source,
                timestamp=timestamp,
                method=method,
                application_id=application_id,
                user_id=user_id
            )
            
            # Verify database was called
            mock_repo.create_audit_event.assert_called_once()
            call_kwargs = mock_repo.create_audit_event.call_args[1]
            
            # Verify all required fields were persisted
            assert call_kwargs["event_type"] == "DATA_INGESTION"
            assert call_kwargs["application_id"] == application_id
            assert call_kwargs["user_id"] == user_id
            assert call_kwargs["timestamp"] == timestamp
            assert call_kwargs["event_data"]["source"] == source
            assert call_kwargs["event_data"]["method"] == method
        
        check_database_persistence()
