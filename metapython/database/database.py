"""
Database Connection and Session Management

Provides:
- SQLAlchemy engine configuration
- Session factory and management
- Connection pooling
- Migration helpers
- Database initialization

References:
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Connection pooling: https://docs.sqlalchemy.org/en/20/core/pooling.html
"""

from typing import Generator, Optional, Dict, Any
import os
from contextlib import contextmanager
from urllib.parse import quote_plus

from sqlalchemy import create_engine, event, Engine, pool
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import NullPool, QueuePool

from metapython.core.config import logger
from metapython.database.models import Base


class DatabaseConfig:
    """
    Database configuration management.

    Supports multiple database backends:
    - PostgreSQL (production)
    - SQLite (development/testing)
    - MySQL (optional)
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600
    ):
        """
        Initialize database configuration.

        Args:
            database_url: Database connection URL (default: from environment)
            echo: Enable SQL query logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_timeout: Connection timeout in seconds
            pool_recycle: Connection recycle time in seconds
        """
        self.database_url = database_url or self._get_database_url()
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle

        # Determine database type
        self.db_type = self._detect_database_type()

    def _get_database_url(self) -> str:
        """Get database URL from environment or use default."""
        # Check for standard database URL
        if url := os.getenv("DATABASE_URL"):
            return url

        # Build from components
        db_type = os.getenv("DB_TYPE", "sqlite")

        if db_type == "sqlite":
            db_path = os.getenv("DB_PATH", "metapython.db")
            return f"sqlite:///{db_path}"

        elif db_type == "postgresql":
            user = os.getenv("DB_USER", "postgres")
            password = quote_plus(os.getenv("DB_PASSWORD", ""))
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME", "metapython")

            return f"postgresql://{user}:{password}@{host}:{port}/{name}"

        elif db_type == "mysql":
            user = os.getenv("DB_USER", "root")
            password = quote_plus(os.getenv("DB_PASSWORD", ""))
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "3306")
            name = os.getenv("DB_NAME", "metapython")

            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _detect_database_type(self) -> str:
        """Detect database type from URL."""
        if self.database_url.startswith("postgresql"):
            return "postgresql"
        elif self.database_url.startswith("sqlite"):
            return "sqlite"
        elif self.database_url.startswith("mysql"):
            return "mysql"
        else:
            return "unknown"

    def get_engine_kwargs(self) -> Dict[str, Any]:
        """Get SQLAlchemy engine configuration."""
        kwargs = {
            "echo": self.echo,
        }

        # Configure pooling based on database type
        if self.db_type == "sqlite":
            # SQLite: disable pooling for thread safety
            kwargs["poolclass"] = NullPool
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            # PostgreSQL/MySQL: use connection pooling
            kwargs["poolclass"] = QueuePool
            kwargs["pool_size"] = self.pool_size
            kwargs["max_overflow"] = self.max_overflow
            kwargs["pool_timeout"] = self.pool_timeout
            kwargs["pool_recycle"] = self.pool_recycle
            kwargs["pool_pre_ping"] = True  # Verify connections before using

        return kwargs


class Database:
    """
    Database manager with session handling.

    Features:
    - Lazy engine initialization
    - Session factory
    - Context manager support
    - Connection testing
    - Schema creation
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database manager.

        Args:
            config: Database configuration (default: auto-detect)
        """
        self.config = config or DatabaseConfig()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._scoped_session: Optional[scoped_session] = None

    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine (lazy initialization)."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine."""
        logger.info(f"Creating database engine: {self.config.db_type}")

        engine = create_engine(
            self.config.database_url,
            **self.config.get_engine_kwargs()
        )

        # Configure SQLite for better concurrency
        if self.config.db_type == "sqlite":
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.close()

        logger.info(f"Database engine created successfully")

        return engine

    @property
    def session_factory(self) -> sessionmaker:
        """Get session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        return self._session_factory

    @property
    def scoped_session_factory(self) -> scoped_session:
        """Get scoped session factory (thread-safe)."""
        if self._scoped_session is None:
            self._scoped_session = scoped_session(self.session_factory)
        return self._scoped_session

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Usage:
            with db.session_scope() as session:
                user = session.query(User).first()
                session.commit()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def create_all(self) -> None:
        """Create all database tables."""
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def drop_all(self) -> None:
        """Drop all database tables (use with caution!)."""
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")

    def reset(self) -> None:
        """Reset database (drop and recreate all tables)."""
        self.drop_all()
        self.create_all()

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful
        """
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def get_table_names(self) -> list:
        """Get list of all table names."""
        return list(Base.metadata.tables.keys())

    def close(self) -> None:
        """Close all database connections."""
        if self._engine is not None:
            self._engine.dispose()
            logger.info("Database connections closed")


# Global database instance (singleton pattern)
_db: Optional[Database] = None


def get_database(config: Optional[DatabaseConfig] = None) -> Database:
    """
    Get global database instance.

    Args:
        config: Optional database configuration

    Returns:
        Database instance
    """
    global _db
    if _db is None:
        _db = Database(config)
    return _db


def get_session() -> Session:
    """
    Get database session (FastAPI dependency).

    Usage:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            users = session.query(User).all()
            return users
    """
    db = get_database()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


def init_database(
    database_url: Optional[str] = None,
    create_tables: bool = True,
    echo: bool = False
) -> Database:
    """
    Initialize database with configuration.

    Args:
        database_url: Database connection URL
        create_tables: Whether to create tables
        echo: Enable SQL logging

    Returns:
        Database instance

    Example:
        >>> db = init_database("postgresql://user:pass@localhost/metapython")
        >>> with db.session_scope() as session:
        ...     users = session.query(User).all()
    """
    config = DatabaseConfig(
        database_url=database_url,
        echo=echo
    )

    db = Database(config)

    # Test connection
    if not db.test_connection():
        raise ConnectionError("Failed to connect to database")

    # Create tables if requested
    if create_tables:
        db.create_all()

    logger.info(f"Database initialized: {config.db_type}")

    return db


__all__ = [
    'DatabaseConfig',
    'Database',
    'get_database',
    'get_session',
    'init_database',
]
