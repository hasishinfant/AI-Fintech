"""Audit Trail Manager for tracking all system operations and decisions."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from app.db.repositories.audit_repository import AuditTrailRepository
from app.models.cam import AuditEvent, AuditTrail


class AuditTrailManager:
    """Manages audit trail recording for all system operations.
    
    Tracks:
    - Data ingestion events (source, timestamp, extraction method)
    - Research activities (URLs, data retrieved, timestamps)
    - Calculations (formulas, inputs, outputs)
    - Modifications (user, field, before/after values)
    """

    def __init__(self, audit_repository: AuditTrailRepository):
        """Initialize AuditTrailManager with repository.
        
        Args:
            audit_repository: Repository for persisting audit events
        """
        self.audit_repository = audit_repository
        self.events: list[AuditEvent] = []

    def record_data_ingestion(
        self,
        source: str,
        timestamp: datetime,
        method: str,
        application_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Record a data ingestion event.
        
        Tracks the source of ingested data, when it was ingested, and the extraction method used.
        
        Args:
            source: The data source (e.g., "GST_RETURN", "BANK_STATEMENT", "ANNUAL_REPORT")
            timestamp: When the data was ingested
            method: The extraction method used (e.g., "OCR", "STRUCTURED_PARSER", "API")
            application_id: Optional application ID for database persistence
            user_id: Optional user ID who triggered the ingestion
            additional_data: Optional additional metadata about the ingestion
            
        Returns:
            AuditEvent: The created audit event
        """
        event_data = {
            "source": source,
            "method": method,
            **(additional_data or {})
        }
        
        event = AuditEvent(
            timestamp=timestamp,
            event_type="DATA_INGESTION",
            description=f"Data ingested from {source} using {method}",
            user=str(user_id) if user_id else None,
            data=event_data
        )
        
        self.events.append(event)
        
        # Persist to database if application_id provided
        if application_id:
            self.audit_repository.create_audit_event(
                event_type="DATA_INGESTION",
                description=event.description,
                application_id=application_id,
                user_id=user_id,
                event_data=event_data,
                timestamp=timestamp
            )
        
        return event

    def record_research_activity(
        self,
        url: str,
        timestamp: datetime,
        data_retrieved: str,
        application_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Record a research activity event.
        
        Tracks URLs accessed, data retrieved, and when the research was performed.
        
        Args:
            url: The URL that was accessed
            timestamp: When the research was performed
            data_retrieved: Description of what data was retrieved
            application_id: Optional application ID for database persistence
            user_id: Optional user ID who triggered the research
            additional_data: Optional additional metadata about the research
            
        Returns:
            AuditEvent: The created audit event
        """
        event_data = {
            "url": url,
            "data_retrieved": data_retrieved,
            **(additional_data or {})
        }
        
        event = AuditEvent(
            timestamp=timestamp,
            event_type="RESEARCH_ACTIVITY",
            description=f"Research performed: {data_retrieved} from {url}",
            user=str(user_id) if user_id else None,
            data=event_data
        )
        
        self.events.append(event)
        
        # Persist to database if application_id provided
        if application_id:
            self.audit_repository.create_audit_event(
                event_type="RESEARCH_ACTIVITY",
                description=event.description,
                application_id=application_id,
                user_id=user_id,
                event_data=event_data,
                timestamp=timestamp
            )
        
        return event

    def record_calculation(
        self,
        calculation_type: str,
        formula: str,
        inputs: Dict[str, Any],
        output: float,
        application_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Record a calculation event.
        
        Documents the formula used, input values, and calculated output.
        
        Args:
            calculation_type: Type of calculation (e.g., "DSCR", "DEBT_EQUITY_RATIO", "LTV")
            formula: The formula used for calculation (e.g., "cash_flow / debt_service")
            inputs: Dictionary of input values used in the calculation
            output: The calculated result
            application_id: Optional application ID for database persistence
            user_id: Optional user ID who triggered the calculation
            additional_data: Optional additional metadata about the calculation
            
        Returns:
            AuditEvent: The created audit event
        """
        event_data = {
            "calculation_type": calculation_type,
            "formula": formula,
            "inputs": inputs,
            "output": output,
            **(additional_data or {})
        }
        
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc),
            event_type="CALCULATION",
            description=f"Calculation performed: {calculation_type} = {output}",
            user=str(user_id) if user_id else None,
            data=event_data
        )
        
        self.events.append(event)
        
        # Persist to database if application_id provided
        if application_id:
            self.audit_repository.create_audit_event(
                event_type="CALCULATION",
                description=event.description,
                application_id=application_id,
                user_id=user_id,
                event_data=event_data,
                timestamp=event.timestamp
            )
        
        return event

    def record_modification(
        self,
        user: str,
        field: str,
        old_value: Any,
        new_value: Any,
        timestamp: datetime,
        application_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Record a data modification event.
        
        Tracks who modified what field, what the old and new values were, and when.
        
        Args:
            user: Username or identifier of the user making the modification
            field: The field that was modified
            old_value: The previous value
            new_value: The new value
            timestamp: When the modification occurred
            application_id: Optional application ID for database persistence
            user_id: Optional user ID for database persistence
            additional_data: Optional additional metadata about the modification
            
        Returns:
            AuditEvent: The created audit event
        """
        event_data = {
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            **(additional_data or {})
        }
        
        event = AuditEvent(
            timestamp=timestamp,
            event_type="MODIFICATION",
            description=f"Field '{field}' modified by {user}: {old_value} → {new_value}",
            user=user,
            data=event_data
        )
        
        self.events.append(event)
        
        # Persist to database if application_id provided
        if application_id:
            self.audit_repository.create_audit_event(
                event_type="MODIFICATION",
                description=event.description,
                application_id=application_id,
                user_id=user_id,
                event_data=event_data,
                timestamp=timestamp
            )
        
        return event

    def get_audit_trail(self) -> AuditTrail:
        """Get the complete audit trail with all recorded events.
        
        Returns:
            AuditTrail: Object containing all recorded events
        """
        return AuditTrail(events=self.events.copy())

    def clear_events(self) -> None:
        """Clear all in-memory events.
        
        Note: This only clears the in-memory cache. Events already persisted
        to the database are not affected.
        """
        self.events.clear()
