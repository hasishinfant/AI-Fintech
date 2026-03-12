"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> T:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, id: UUID) -> Optional[T]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(
            getattr(self.model, self._get_id_field()) == id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: UUID, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance

    def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        instance = self.get_by_id(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False

    def _get_id_field(self) -> str:
        """Get the primary key field name for the model."""
        # Default to common ID field names
        for field in ["id", f"{self.model.__tablename__}_id"]:
            if hasattr(self.model, field):
                return field
        raise ValueError(f"Could not determine ID field for {self.model.__name__}")
