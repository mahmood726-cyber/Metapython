"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2025-11-05

Creates all tables for MetaPython database:
- users: User accounts and authentication
- projects: Meta-analysis projects
- project_collaborators: Project collaboration
- studies: Individual studies in meta-analyses
- analyses: Analysis results with versioning
- audit_logs: Audit trail
- saved_visualizations: Saved plot configurations
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('institution', sa.String(length=255), nullable=True),
        sa.Column('orcid', sa.String(length=19), nullable=True),
        sa.Column('role', sa.Enum('admin', 'researcher', 'reviewer', 'viewer', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('research_question', sa.Text(), nullable=True),
        sa.Column('picos_population', sa.Text(), nullable=True),
        sa.Column('picos_intervention', sa.Text(), nullable=True),
        sa.Column('picos_comparator', sa.Text(), nullable=True),
        sa.Column('picos_outcome', sa.Text(), nullable=True),
        sa.Column('picos_study_design', sa.Text(), nullable=True),
        sa.Column('effect_measure', sa.Enum('smd', 'md', 'or', 'rr', 'hr', 'proportion', 'correlation', name='effectmeasure'), nullable=False),
        sa.Column('confidence_level', sa.Float(), nullable=False, server_default='0.95'),
        sa.Column('status', sa.Enum('draft', 'in_progress', 'completed', 'published', 'archived', name='analysisstatus'), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)

    # Project collaborators table
    op.create_table(
        'project_collaborators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('can_edit', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_delete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_publish', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('added_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='unique_project_user')
    )

    # Studies table
    op.create_table(
        'studies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('study_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('authors', sa.Text(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('journal', sa.String(length=255), nullable=True),
        sa.Column('doi', sa.String(length=100), nullable=True),
        sa.Column('pmid', sa.String(length=20), nullable=True),
        sa.Column('effect_size', sa.Float(), nullable=True),
        sa.Column('standard_error', sa.Float(), nullable=True),
        sa.Column('variance', sa.Float(), nullable=True),
        sa.Column('ci_lower', sa.Float(), nullable=True),
        sa.Column('ci_upper', sa.Float(), nullable=True),
        sa.Column('n_intervention', sa.Integer(), nullable=True),
        sa.Column('n_control', sa.Integer(), nullable=True),
        sa.Column('n_total', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'included', 'excluded', 'uncertain', name='studystatus'), nullable=False),
        sa.Column('exclusion_reason', sa.Text(), nullable=True),
        sa.Column('screening_confidence', sa.Float(), nullable=True),
        sa.Column('rob_random_sequence', sa.Integer(), nullable=True),
        sa.Column('rob_allocation_concealment', sa.Integer(), nullable=True),
        sa.Column('rob_blinding_participants', sa.Integer(), nullable=True),
        sa.Column('rob_blinding_outcome', sa.Integer(), nullable=True),
        sa.Column('rob_incomplete_data', sa.Integer(), nullable=True),
        sa.Column('rob_selective_reporting', sa.Integer(), nullable=True),
        sa.Column('rob_other', sa.Integer(), nullable=True),
        sa.Column('moderators', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('effect_size IS NULL OR standard_error IS NOT NULL', name='effect_size_requires_se')
    )
    op.create_index(op.f('ix_studies_id'), 'studies', ['id'], unique=False)
    op.create_index(op.f('ix_studies_project_id'), 'studies', ['project_id'], unique=False)
    op.create_index('idx_study_project_status', 'studies', ['project_id', 'status'], unique=False)
    op.create_index('idx_study_year', 'studies', ['year'], unique=False)

    # Analyses table
    op.create_table(
        'analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('method', sa.String(length=50), nullable=False),
        sa.Column('tau2_estimator', sa.String(length=50), nullable=True),
        sa.Column('pooled_effect', sa.Float(), nullable=False),
        sa.Column('pooled_se', sa.Float(), nullable=False),
        sa.Column('ci_lower', sa.Float(), nullable=False),
        sa.Column('ci_upper', sa.Float(), nullable=False),
        sa.Column('p_value', sa.Float(), nullable=False),
        sa.Column('tau2', sa.Float(), nullable=True),
        sa.Column('i2', sa.Float(), nullable=True),
        sa.Column('h2', sa.Float(), nullable=True),
        sa.Column('q_statistic', sa.Float(), nullable=True),
        sa.Column('q_p_value', sa.Float(), nullable=True),
        sa.Column('pi_lower', sa.Float(), nullable=True),
        sa.Column('pi_upper', sa.Float(), nullable=True),
        sa.Column('egger_intercept', sa.Float(), nullable=True),
        sa.Column('egger_p_value', sa.Float(), nullable=True),
        sa.Column('begg_p_value', sa.Float(), nullable=True),
        sa.Column('ml_predicted_heterogeneity', sa.Float(), nullable=True),
        sa.Column('ml_bias_probability', sa.Float(), nullable=True),
        sa.Column('ml_confidence', sa.Float(), nullable=True),
        sa.Column('results_json', sa.JSON(), nullable=True),
        sa.Column('n_studies', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'version', name='unique_project_version')
    )
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)
    op.create_index(op.f('ix_analyses_project_id'), 'analyses', ['project_id'], unique=False)
    op.create_index('idx_analysis_project_version', 'analyses', ['project_id', 'version'], unique=False)
    op.create_index('idx_analysis_current', 'analyses', ['is_current'], unique=False)

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index('idx_audit_entity', 'audit_logs', ['entity_type', 'entity_id'], unique=False)
    op.create_index('idx_audit_action', 'audit_logs', ['action'], unique=False)

    # Saved visualizations table
    op.create_table(
        'saved_visualizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('plot_type', sa.String(length=50), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('plot_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_visualizations_id'), 'saved_visualizations', ['id'], unique=False)
    op.create_index(op.f('ix_saved_visualizations_project_id'), 'saved_visualizations', ['project_id'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('saved_visualizations')
    op.drop_table('audit_logs')
    op.drop_table('analyses')
    op.drop_table('studies')
    op.drop_table('project_collaborators')
    op.drop_table('projects')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS studystatus')
    op.execute('DROP TYPE IF EXISTS analysisstatus')
    op.execute('DROP TYPE IF EXISTS effectmeasure')
    op.execute('DROP TYPE IF EXISTS userrole')
