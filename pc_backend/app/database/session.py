"""
Database session management for the Parkinson's Monitoring System.

This module provides database session management utilities,
including session creation, dependency injection for FastAPI,
and test database support.

Architecture:
- One shared application engine per DatabaseManager instance
- Engine is configured with SQLite PRAGMAs (WAL, foreign_keys)
- Session factory binds to the shared engine
- Test databases use isolated in-memory engines
"""

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy.orm import Session, sessionmaker

from pc_backend.app.database.base import create_configured_engine


class DatabaseManager:
    """
    Database session manager.

    Manages a single shared database engine and session factory.
    All sessions created by this manager share the same engine
    with consistent configuration.
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.

        Args:
            database_url: Optional database URL override
        """
        from pc_backend.app.core.config import settings
        self._database_url = database_url or settings.DATABASE_URL
        self._engine = create_configured_engine(self._database_url)
        self._session_factory = sessionmaker(bind=self._engine)

    @property
    def engine(self):
        """Get the SQLAlchemy engine."""
        return self._engine

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            Session: Configured database session
        """
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional session scope.

        Usage:
            with db_manager.session_scope() as session:
                session.add(record)
                # Auto-commits on success, rolls back on exception

        Yields:
            Session: Database session
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        """Dispose of the database engine and connections."""
        self._engine.dispose()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        DatabaseManager: Configured database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def reset_database_manager() -> None:
    """
    Reset the global database manager instance.

    Used for testing to ensure clean state between tests.
    """
    global _db_manager
    if _db_manager is not None:
        _db_manager.dispose()
    _db_manager = None


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session
            pass

    Yields:
        Session: Database session
    """
    db_manager = get_database_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def init_database(database_url: Optional[str] = None) -> None:
    """
    Initialize database tables.

    Args:
        database_url: Optional database URL override
    """
    from pc_backend.app.database.base import init_database as _init_database
    _init_database(database_url)


def create_test_database() -> DatabaseManager:
    """
    Create a test database manager with in-memory SQLite.

    Returns:
        DatabaseManager: Test database manager
    """
    return DatabaseManager("sqlite:///:memory:")
