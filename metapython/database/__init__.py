"""
Database Layer for MetaPython

Complete database persistence with:
- SQLAlchemy ORM models
- Connection management
- CRUD operations
- Alembic migrations
- Audit logging

Usage:
    >>> from metapython.database import init_database, get_session
    >>> from metapython.database import UserCRUD, ProjectCRUD
    >>>
    >>> # Initialize database
    >>> db = init_database("postgresql://user:pass@localhost/metapython")
    >>>
    >>> # Use session
    >>> with db.session_scope() as session:
    ...     user = UserCRUD.create_user(
    ...         session,
    ...         username="researcher",
    ...         email="researcher@example.com",
    ...         password="secure_password"
    ...     )
    ...     project = ProjectCRUD.create_project(
    ...         session,
    ...         owner_id=user.id,
    ...         title="My Meta-Analysis"
    ...     )
"""

# Models
from metapython.database.models import (
    Base,
    User,
    UserRole,
    MetaAnalysisProject,
    ProjectCollaborator,
    Study,
    StudyStatus,
    EffectMeasure,
    Analysis,
    AnalysisStatus,
    AuditLog,
    SavedVisualization,
)

# Database management
from metapython.database.database import (
    DatabaseConfig,
    Database,
    get_database,
    get_session,
    init_database,
)

# CRUD operations
from metapython.database.crud import (
    UserCRUD,
    ProjectCRUD,
    StudyCRUD,
    AnalysisCRUD,
    AuditLogCRUD,
)

__all__ = [
    # Models
    'Base',
    'User',
    'UserRole',
    'MetaAnalysisProject',
    'ProjectCollaborator',
    'Study',
    'StudyStatus',
    'EffectMeasure',
    'Analysis',
    'AnalysisStatus',
    'AuditLog',
    'SavedVisualization',

    # Database
    'DatabaseConfig',
    'Database',
    'get_database',
    'get_session',
    'init_database',

    # CRUD
    'UserCRUD',
    'ProjectCRUD',
    'StudyCRUD',
    'AnalysisCRUD',
    'AuditLogCRUD',
]
