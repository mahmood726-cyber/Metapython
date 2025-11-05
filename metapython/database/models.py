"""
Database Models for MetaPython

Comprehensive SQLAlchemy models for meta-analysis persistence:
- User management and authentication
- Meta-analysis projects and studies
- Analysis results and versioning
- Collaboration and audit logging
- Publication bias assessments
- ML predictions and model tracking

References:
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/
- Alembic migrations: https://alembic.sqlalchemy.org/
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum
import json

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    ForeignKey, Enum, JSON, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# Enums
class UserRole(str, PyEnum):
    """User role enumeration."""
    ADMIN = "admin"
    RESEARCHER = "researcher"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class AnalysisStatus(str, PyEnum):
    """Analysis status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class StudyStatus(str, PyEnum):
    """Study screening status."""
    PENDING = "pending"
    INCLUDED = "included"
    EXCLUDED = "excluded"
    UNCERTAIN = "uncertain"


class EffectMeasure(str, PyEnum):
    """Effect size measure types."""
    SMD = "smd"  # Standardized Mean Difference
    MD = "md"   # Mean Difference
    OR = "or"   # Odds Ratio
    RR = "rr"   # Risk Ratio
    HR = "hr"   # Hazard Ratio
    PROPORTION = "proportion"
    CORRELATION = "correlation"


class User(Base):
    """
    User model for authentication and authorization.

    Features:
    - Password hashing with bcrypt
    - Role-based access control
    - Email verification
    - Account status management
    - Audit timestamps
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    institution: Mapped[Optional[str]] = mapped_column(String(255))
    orcid: Mapped[Optional[str]] = mapped_column(String(19))  # 0000-0002-1825-0097 format

    # Permissions
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.RESEARCHER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    projects: Mapped[List["MetaAnalysisProject"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    collaborations: Mapped[List["ProjectCollaborator"]] = relationship(back_populates="user")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role={self.role})>"


class MetaAnalysisProject(Base):
    """
    Meta-analysis project container.

    Represents a complete meta-analysis study with:
    - Multiple studies
    - Analysis configurations
    - Results and versions
    - Collaboration settings
    """
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Project metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    research_question: Mapped[Optional[str]] = mapped_column(Text)

    # PICOS criteria
    picos_population: Mapped[Optional[str]] = mapped_column(Text)
    picos_intervention: Mapped[Optional[str]] = mapped_column(Text)
    picos_comparator: Mapped[Optional[str]] = mapped_column(Text)
    picos_outcome: Mapped[Optional[str]] = mapped_column(Text)
    picos_study_design: Mapped[Optional[str]] = mapped_column(Text)

    # Configuration
    effect_measure: Mapped[EffectMeasure] = mapped_column(Enum(EffectMeasure), default=EffectMeasure.SMD)
    confidence_level: Mapped[float] = mapped_column(Float, default=0.95)

    # Status
    status: Mapped[AnalysisStatus] = mapped_column(Enum(AnalysisStatus), default=AnalysisStatus.DRAFT)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    owner: Mapped[User] = relationship(back_populates="projects")
    studies: Mapped[List["Study"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    analyses: Mapped[List["Analysis"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    collaborators: Mapped[List["ProjectCollaborator"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    @hybrid_property
    def n_studies(self) -> int:
        """Number of included studies."""
        return sum(1 for s in self.studies if s.status == StudyStatus.INCLUDED)

    def __repr__(self) -> str:
        return f"<MetaAnalysisProject(id={self.id}, title='{self.title}', status={self.status})>"


class ProjectCollaborator(Base):
    """
    Project collaboration model.

    Enables multi-user collaboration with role-based permissions.
    """
    __tablename__ = "project_collaborators"
    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='unique_project_user'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Permissions
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    can_publish: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project: Mapped[MetaAnalysisProject] = relationship(back_populates="collaborators")
    user: Mapped[User] = relationship(back_populates="collaborations")

    def __repr__(self) -> str:
        return f"<ProjectCollaborator(project_id={self.project_id}, user_id={self.user_id})>"


class Study(Base):
    """
    Individual study in a meta-analysis.

    Stores:
    - Study characteristics
    - Effect size data
    - Risk of bias assessment
    - Moderator variables
    """
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    # Study identification
    study_id: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Smith2020"
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[Optional[str]] = mapped_column(Text)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    journal: Mapped[Optional[str]] = mapped_column(String(255))
    doi: Mapped[Optional[str]] = mapped_column(String(100))
    pmid: Mapped[Optional[str]] = mapped_column(String(20))

    # Effect size data
    effect_size: Mapped[Optional[float]] = mapped_column(Float)
    standard_error: Mapped[Optional[float]] = mapped_column(Float)
    variance: Mapped[Optional[float]] = mapped_column(Float)
    ci_lower: Mapped[Optional[float]] = mapped_column(Float)
    ci_upper: Mapped[Optional[float]] = mapped_column(Float)

    # Sample size
    n_intervention: Mapped[Optional[int]] = mapped_column(Integer)
    n_control: Mapped[Optional[int]] = mapped_column(Integer)
    n_total: Mapped[Optional[int]] = mapped_column(Integer)

    # Screening
    status: Mapped[StudyStatus] = mapped_column(Enum(StudyStatus), default=StudyStatus.PENDING)
    exclusion_reason: Mapped[Optional[str]] = mapped_column(Text)
    screening_confidence: Mapped[Optional[float]] = mapped_column(Float)  # ML confidence

    # Risk of bias (0-7 scale per Cochrane RoB 2)
    rob_random_sequence: Mapped[Optional[int]] = mapped_column(Integer)
    rob_allocation_concealment: Mapped[Optional[int]] = mapped_column(Integer)
    rob_blinding_participants: Mapped[Optional[int]] = mapped_column(Integer)
    rob_blinding_outcome: Mapped[Optional[int]] = mapped_column(Integer)
    rob_incomplete_data: Mapped[Optional[int]] = mapped_column(Integer)
    rob_selective_reporting: Mapped[Optional[int]] = mapped_column(Integer)
    rob_other: Mapped[Optional[int]] = mapped_column(Integer)

    # Moderators (flexible JSON storage)
    moderators: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project: Mapped[MetaAnalysisProject] = relationship(back_populates="studies")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_study_project_status', 'project_id', 'status'),
        Index('idx_study_year', 'year'),
        CheckConstraint('effect_size IS NULL OR standard_error IS NOT NULL', name='effect_size_requires_se'),
    )

    @hybrid_property
    def total_rob_score(self) -> Optional[int]:
        """Calculate total risk of bias score (0-7)."""
        scores = [
            self.rob_random_sequence,
            self.rob_allocation_concealment,
            self.rob_blinding_participants,
            self.rob_blinding_outcome,
            self.rob_incomplete_data,
            self.rob_selective_reporting,
            self.rob_other
        ]
        non_null_scores = [s for s in scores if s is not None]
        return sum(non_null_scores) if non_null_scores else None

    def __repr__(self) -> str:
        return f"<Study(id={self.id}, study_id='{self.study_id}', status={self.status})>"


class Analysis(Base):
    """
    Meta-analysis results with versioning.

    Stores:
    - Pooled effect estimates
    - Heterogeneity statistics
    - Publication bias tests
    - Subgroup/sensitivity analyses
    - ML predictions
    """
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Analysis configuration
    method: Mapped[str] = mapped_column(String(50))  # "fixed", "random", "bayesian", "ml"
    tau2_estimator: Mapped[Optional[str]] = mapped_column(String(50))  # "DL", "REML", "PM", "ML"

    # Pooled effect
    pooled_effect: Mapped[float] = mapped_column(Float, nullable=False)
    pooled_se: Mapped[float] = mapped_column(Float, nullable=False)
    ci_lower: Mapped[float] = mapped_column(Float, nullable=False)
    ci_upper: Mapped[float] = mapped_column(Float, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, nullable=False)

    # Heterogeneity
    tau2: Mapped[Optional[float]] = mapped_column(Float)
    i2: Mapped[Optional[float]] = mapped_column(Float)
    h2: Mapped[Optional[float]] = mapped_column(Float)
    q_statistic: Mapped[Optional[float]] = mapped_column(Float)
    q_p_value: Mapped[Optional[float]] = mapped_column(Float)

    # Prediction interval
    pi_lower: Mapped[Optional[float]] = mapped_column(Float)
    pi_upper: Mapped[Optional[float]] = mapped_column(Float)

    # Publication bias
    egger_intercept: Mapped[Optional[float]] = mapped_column(Float)
    egger_p_value: Mapped[Optional[float]] = mapped_column(Float)
    begg_p_value: Mapped[Optional[float]] = mapped_column(Float)

    # ML predictions (if applicable)
    ml_predicted_heterogeneity: Mapped[Optional[float]] = mapped_column(Float)
    ml_bias_probability: Mapped[Optional[float]] = mapped_column(Float)
    ml_confidence: Mapped[Optional[float]] = mapped_column(Float)

    # Full results (JSON for complex structures)
    results_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Metadata
    n_studies: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    project: Mapped[MetaAnalysisProject] = relationship(back_populates="analyses")

    __table_args__ = (
        Index('idx_analysis_project_version', 'project_id', 'version'),
        Index('idx_analysis_current', 'is_current'),
        UniqueConstraint('project_id', 'version', name='unique_project_version'),
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, project_id={self.project_id}, version={self.version}, method='{self.method}')>"


class AuditLog(Base):
    """
    Audit logging for compliance and tracking.

    Records all significant actions for:
    - Regulatory compliance
    - Data integrity
    - Collaboration tracking
    - Security monitoring
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)

    # Action details
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # "create_project", "add_study", etc.
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "project", "study", "analysis"
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Changes
    old_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    new_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 support
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user: Mapped[Optional[User]] = relationship(back_populates="audit_logs")

    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_action', 'action'),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', entity_type='{self.entity_type}')>"


class SavedVisualization(Base):
    """
    Saved visualization configurations.

    Stores plot settings for:
    - Forest plots
    - Funnel plots
    - Interactive dashboards
    - Custom visualizations
    """
    __tablename__ = "saved_visualizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    # Visualization details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plot_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "forest", "funnel", "dashboard"

    # Configuration (JSON)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Plot data (base64 encoded image or Plotly JSON)
    plot_data: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SavedVisualization(id={self.id}, name='{self.name}', type='{self.plot_type}')>"


__all__ = [
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
]
