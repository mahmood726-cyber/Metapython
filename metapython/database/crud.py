"""
CRUD Operations for Meta-Analysis Data

Provides database operations for:
- User management
- Project creation and updates
- Study management
- Analysis storage and retrieval
- Collaboration management
- Audit logging

References:
- SQLAlchemy queries: https://docs.sqlalchemy.org/en/20/orm/queryguide/
- Best practices: https://docs.sqlalchemy.org/en/20/tutorial/
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.exc import IntegrityError

from metapython.database.models import (
    User, UserRole,
    MetaAnalysisProject, ProjectCollaborator,
    Study, StudyStatus,
    Analysis, AnalysisStatus,
    AuditLog, SavedVisualization,
    EffectMeasure
)
from metapython.core.config import logger


# ========================================
# User Operations
# ========================================

class UserCRUD:
    """CRUD operations for User model."""

    @staticmethod
    def create_user(
        session: Session,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        institution: Optional[str] = None,
        role: UserRole = UserRole.RESEARCHER
    ) -> User:
        """
        Create a new user.

        Args:
            session: Database session
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            full_name: Full name
            institution: Institutional affiliation
            role: User role

        Returns:
            Created user

        Raises:
            IntegrityError: If username or email already exists
        """
        user = User(
            username=username,
            email=email,
            hashed_password=User.hash_password(password),
            full_name=full_name,
            institution=institution,
            role=role
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        logger.info(f"Created user: {username} (id={user.id})")

        return user

    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return session.get(User, user_id)

    @staticmethod
    def get_user_by_username(session: Session, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(User).where(User.username == username)
        return session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        return session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def authenticate_user(
        session: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user by username and password.

        Args:
            session: Database session
            username: Username
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        user = UserCRUD.get_user_by_username(session, username)

        if user is None or not user.verify_password(password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        session.commit()

        logger.info(f"User authenticated: {username}")

        return user

    @staticmethod
    def update_user(
        session: Session,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """
        Update user fields.

        Args:
            session: Database session
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated user
        """
        user = session.get(User, user_id)
        if user is None:
            return None

        # Hash password if provided
        if 'password' in kwargs:
            kwargs['hashed_password'] = User.hash_password(kwargs.pop('password'))

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        session.commit()
        session.refresh(user)

        logger.info(f"Updated user: {user.username} (id={user_id})")

        return user

    @staticmethod
    def list_users(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """List users with optional filtering."""
        stmt = select(User)

        if role is not None:
            stmt = stmt.where(User.role == role)

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        stmt = stmt.offset(skip).limit(limit)

        return list(session.execute(stmt).scalars().all())


# ========================================
# Project Operations
# ========================================

class ProjectCRUD:
    """CRUD operations for MetaAnalysisProject model."""

    @staticmethod
    def create_project(
        session: Session,
        owner_id: int,
        title: str,
        description: Optional[str] = None,
        effect_measure: EffectMeasure = EffectMeasure.SMD,
        **kwargs
    ) -> MetaAnalysisProject:
        """
        Create a new meta-analysis project.

        Args:
            session: Database session
            owner_id: Project owner user ID
            title: Project title
            description: Project description
            effect_measure: Effect size measure
            **kwargs: Additional project fields

        Returns:
            Created project
        """
        project = MetaAnalysisProject(
            owner_id=owner_id,
            title=title,
            description=description,
            effect_measure=effect_measure,
            **kwargs
        )

        session.add(project)
        session.commit()
        session.refresh(project)

        # Log creation
        AuditLogCRUD.log_action(
            session,
            user_id=owner_id,
            action="create_project",
            entity_type="project",
            entity_id=project.id,
            new_values={"title": title}
        )

        logger.info(f"Created project: {title} (id={project.id})")

        return project

    @staticmethod
    def get_project(
        session: Session,
        project_id: int,
        include_studies: bool = False,
        include_analyses: bool = False
    ) -> Optional[MetaAnalysisProject]:
        """
        Get project by ID with optional eager loading.

        Args:
            session: Database session
            project_id: Project ID
            include_studies: Load studies relationship
            include_analyses: Load analyses relationship

        Returns:
            Project if found
        """
        stmt = select(MetaAnalysisProject).where(MetaAnalysisProject.id == project_id)

        if include_studies:
            stmt = stmt.options(selectinload(MetaAnalysisProject.studies))

        if include_analyses:
            stmt = stmt.options(selectinload(MetaAnalysisProject.analyses))

        return session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_user_projects(
        session: Session,
        user_id: int,
        status: Optional[AnalysisStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MetaAnalysisProject]:
        """
        List projects owned by or shared with a user.

        Args:
            session: Database session
            user_id: User ID
            status: Filter by status
            skip: Offset
            limit: Maximum results

        Returns:
            List of projects
        """
        # Projects owned by user
        owned_stmt = select(MetaAnalysisProject).where(
            MetaAnalysisProject.owner_id == user_id
        )

        # Projects shared with user
        shared_stmt = select(MetaAnalysisProject).join(
            ProjectCollaborator
        ).where(
            ProjectCollaborator.user_id == user_id
        )

        # Combine
        stmt = owned_stmt.union(shared_stmt)

        if status is not None:
            stmt = stmt.where(MetaAnalysisProject.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(
            MetaAnalysisProject.updated_at.desc()
        )

        return list(session.execute(stmt).scalars().all())

    @staticmethod
    def update_project(
        session: Session,
        project_id: int,
        user_id: int,
        **kwargs
    ) -> Optional[MetaAnalysisProject]:
        """
        Update project fields.

        Args:
            session: Database session
            project_id: Project ID
            user_id: User making the change (for audit log)
            **kwargs: Fields to update

        Returns:
            Updated project
        """
        project = session.get(MetaAnalysisProject, project_id)
        if project is None:
            return None

        old_values = {}
        new_values = {}

        for key, value in kwargs.items():
            if hasattr(project, key):
                old_values[key] = getattr(project, key)
                setattr(project, key, value)
                new_values[key] = value

        session.commit()
        session.refresh(project)

        # Log update
        AuditLogCRUD.log_action(
            session,
            user_id=user_id,
            action="update_project",
            entity_type="project",
            entity_id=project_id,
            old_values=old_values,
            new_values=new_values
        )

        logger.info(f"Updated project: {project.title} (id={project_id})")

        return project

    @staticmethod
    def delete_project(
        session: Session,
        project_id: int,
        user_id: int
    ) -> bool:
        """
        Delete project (soft delete by changing status).

        Args:
            session: Database session
            project_id: Project ID
            user_id: User making the change

        Returns:
            True if deleted
        """
        project = session.get(MetaAnalysisProject, project_id)
        if project is None:
            return False

        project.status = AnalysisStatus.ARCHIVED

        session.commit()

        # Log deletion
        AuditLogCRUD.log_action(
            session,
            user_id=user_id,
            action="delete_project",
            entity_type="project",
            entity_id=project_id
        )

        logger.info(f"Deleted project: {project.title} (id={project_id})")

        return True


# ========================================
# Study Operations
# ========================================

class StudyCRUD:
    """CRUD operations for Study model."""

    @staticmethod
    def create_study(
        session: Session,
        project_id: int,
        study_id: str,
        title: str,
        **kwargs
    ) -> Study:
        """
        Create a new study.

        Args:
            session: Database session
            project_id: Project ID
            study_id: Study identifier (e.g., "Smith2020")
            title: Study title
            **kwargs: Additional study fields

        Returns:
            Created study
        """
        study = Study(
            project_id=project_id,
            study_id=study_id,
            title=title,
            **kwargs
        )

        session.add(study)
        session.commit()
        session.refresh(study)

        logger.info(f"Created study: {study_id} in project {project_id}")

        return study

    @staticmethod
    def get_study(session: Session, study_id: int) -> Optional[Study]:
        """Get study by ID."""
        return session.get(Study, study_id)

    @staticmethod
    def list_project_studies(
        session: Session,
        project_id: int,
        status: Optional[StudyStatus] = None,
        skip: int = 0,
        limit: int = 1000
    ) -> List[Study]:
        """
        List studies in a project.

        Args:
            session: Database session
            project_id: Project ID
            status: Filter by status
            skip: Offset
            limit: Maximum results

        Returns:
            List of studies
        """
        stmt = select(Study).where(Study.project_id == project_id)

        if status is not None:
            stmt = stmt.where(Study.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(Study.year.desc())

        return list(session.execute(stmt).scalars().all())

    @staticmethod
    def get_included_studies(
        session: Session,
        project_id: int
    ) -> List[Study]:
        """Get all included studies for a project."""
        return StudyCRUD.list_project_studies(
            session,
            project_id,
            status=StudyStatus.INCLUDED,
            limit=10000
        )

    @staticmethod
    def update_study(
        session: Session,
        study_id: int,
        **kwargs
    ) -> Optional[Study]:
        """Update study fields."""
        study = session.get(Study, study_id)
        if study is None:
            return None

        for key, value in kwargs.items():
            if hasattr(study, key):
                setattr(study, key, value)

        session.commit()
        session.refresh(study)

        return study

    @staticmethod
    def bulk_import_studies(
        session: Session,
        project_id: int,
        studies_data: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk import studies.

        Args:
            session: Database session
            project_id: Project ID
            studies_data: List of study dictionaries

        Returns:
            Number of studies imported
        """
        studies = [
            Study(project_id=project_id, **data)
            for data in studies_data
        ]

        session.add_all(studies)
        session.commit()

        logger.info(f"Bulk imported {len(studies)} studies to project {project_id}")

        return len(studies)


# ========================================
# Analysis Operations
# ========================================

class AnalysisCRUD:
    """CRUD operations for Analysis model."""

    @staticmethod
    def create_analysis(
        session: Session,
        project_id: int,
        method: str,
        pooled_effect: float,
        pooled_se: float,
        ci_lower: float,
        ci_upper: float,
        p_value: float,
        n_studies: int,
        **kwargs
    ) -> Analysis:
        """
        Create a new analysis result.

        Args:
            session: Database session
            project_id: Project ID
            method: Analysis method
            pooled_effect: Pooled effect estimate
            pooled_se: Standard error
            ci_lower: Lower confidence interval
            ci_upper: Upper confidence interval
            p_value: P-value
            n_studies: Number of studies
            **kwargs: Additional analysis fields

        Returns:
            Created analysis
        """
        # Get next version number
        stmt = select(func.max(Analysis.version)).where(
            Analysis.project_id == project_id
        )
        max_version = session.execute(stmt).scalar_one_or_none() or 0
        version = max_version + 1

        # Mark previous analyses as not current
        session.execute(
            update(Analysis).where(
                and_(
                    Analysis.project_id == project_id,
                    Analysis.is_current == True
                )
            ).values(is_current=False)
        )

        # Create new analysis
        analysis = Analysis(
            project_id=project_id,
            version=version,
            is_current=True,
            method=method,
            pooled_effect=pooled_effect,
            pooled_se=pooled_se,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            p_value=p_value,
            n_studies=n_studies,
            **kwargs
        )

        session.add(analysis)
        session.commit()
        session.refresh(analysis)

        logger.info(f"Created analysis v{version} for project {project_id}")

        return analysis

    @staticmethod
    def get_current_analysis(
        session: Session,
        project_id: int
    ) -> Optional[Analysis]:
        """Get current (latest) analysis for a project."""
        stmt = select(Analysis).where(
            and_(
                Analysis.project_id == project_id,
                Analysis.is_current == True
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_project_analyses(
        session: Session,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        """List all analyses for a project."""
        stmt = select(Analysis).where(
            Analysis.project_id == project_id
        ).order_by(
            Analysis.version.desc()
        ).offset(skip).limit(limit)

        return list(session.execute(stmt).scalars().all())


# ========================================
# Audit Log Operations
# ========================================

class AuditLogCRUD:
    """CRUD operations for AuditLog model."""

    @staticmethod
    def log_action(
        session: Session,
        user_id: Optional[int],
        action: str,
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an action to audit log.

        Args:
            session: Database session
            user_id: User performing action
            action: Action name
            entity_type: Entity type
            entity_id: Entity ID
            old_values: Previous values
            new_values: New values
            ip_address: IP address
            user_agent: User agent

        Returns:
            Created audit log entry
        """
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

        session.add(log)
        session.commit()

        return log

    @staticmethod
    def get_entity_history(
        session: Session,
        entity_type: str,
        entity_id: int,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit history for an entity."""
        stmt = select(AuditLog).where(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit)

        return list(session.execute(stmt).scalars().all())


__all__ = [
    'UserCRUD',
    'ProjectCRUD',
    'StudyCRUD',
    'AnalysisCRUD',
    'AuditLogCRUD',
]
