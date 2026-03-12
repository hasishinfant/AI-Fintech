"""Database connection and session management with connection pooling."""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Maximum number of connections that can be created beyond pool_size
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class TransactionManager:
    """Transaction management utilities."""

    def __init__(self, db: Session):
        self.db = db

    def begin(self):
        """Begin a new transaction."""
        return self.db.begin()

    def commit(self):
        """Commit the current transaction."""
        self.db.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.db.rollback()

    def flush(self):
        """Flush pending changes to the database."""
        self.db.flush()

    @contextmanager
    def transaction(self):
        """Context manager for transaction handling."""
        try:
            yield self.db
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise


# Event listeners for connection pool monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Event listener for new connections."""
    pass


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Event listener for connection checkout from pool."""
    pass
