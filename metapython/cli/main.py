"""
MetaPython CLI Tool

Comprehensive command-line interface for:
- Database management
- User management
- Project operations
- Analysis execution
- Data import/export
- Server management

Usage:
    metapython --help
    metapython db init
    metapython user create --username alice --email alice@example.com
    metapython analyze --project-id 1 --method random
    metapython server start
"""

import sys
from typing import Optional
import click
from pathlib import Path

from metapython.core.config import logger


@click.group()
@click.version_option(version="0.7.0", prog_name="MetaPython")
def cli():
    """
    MetaPython - Comprehensive Meta-Analysis Platform

    Complete toolkit for systematic review and meta-analysis with:
    - Advanced statistical methods
    - Machine learning predictions
    - R Shiny integration
    - Real-time collaboration
    - Automated reporting
    """
    pass


# ========================================
# Database Commands
# ========================================

@cli.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.option('--url', help='Database URL')
@click.option('--echo/--no-echo', default=False, help='Echo SQL queries')
def init(url: Optional[str], echo: bool):
    """Initialize database (create tables)."""
    from metapython.database import init_database

    try:
        db = init_database(database_url=url, create_tables=True, echo=echo)
        click.echo(click.style("✓ Database initialized successfully", fg="green"))
        click.echo(f"Database type: {db.config.db_type}")
        click.echo(f"Tables created: {', '.join(db.get_table_names())}")
    except Exception as e:
        click.echo(click.style(f"✗ Database initialization failed: {e}", fg="red"))
        sys.exit(1)


@db.command()
@click.confirmation_option(prompt="Are you sure you want to reset the database?")
def reset():
    """Reset database (drop and recreate all tables)."""
    from metapython.database import get_database

    try:
        db = get_database()
        db.reset()
        click.echo(click.style("✓ Database reset successfully", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Database reset failed: {e}", fg="red"))
        sys.exit(1)


@db.command()
def migrate():
    """Run database migrations."""
    import subprocess

    try:
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.echo(click.style("✓ Migrations applied successfully", fg="green"))
            click.echo(result.stdout)
        else:
            click.echo(click.style("✗ Migration failed", fg="red"))
            click.echo(result.stderr)
            sys.exit(1)

    except FileNotFoundError:
        click.echo(click.style("✗ Alembic not found. Install with: pip install alembic", fg="red"))
        sys.exit(1)


@db.command()
@click.option('--message', '-m', required=True, help='Migration message')
def makemigration(message: str):
    """Create a new migration."""
    import subprocess

    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.echo(click.style("✓ Migration created successfully", fg="green"))
            click.echo(result.stdout)
        else:
            click.echo(click.style("✗ Migration creation failed", fg="red"))
            click.echo(result.stderr)
            sys.exit(1)

    except FileNotFoundError:
        click.echo(click.style("✗ Alembic not found", fg="red"))
        sys.exit(1)


@db.command()
def status():
    """Show database status."""
    from metapython.database import get_database

    try:
        db = get_database()

        if db.test_connection():
            click.echo(click.style("✓ Database connection: OK", fg="green"))
        else:
            click.echo(click.style("✗ Database connection: FAILED", fg="red"))
            sys.exit(1)

        click.echo(f"\nDatabase type: {db.config.db_type}")
        click.echo(f"Tables: {len(db.get_table_names())}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))
        sys.exit(1)


# ========================================
# User Commands
# ========================================

@cli.group()
def user():
    """User management commands."""
    pass


@user.command()
@click.option('--username', prompt=True, help='Username')
@click.option('--email', prompt=True, help='Email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password')
@click.option('--full-name', help='Full name')
@click.option('--institution', help='Institution')
@click.option('--role', type=click.Choice(['admin', 'researcher', 'reviewer', 'viewer']), default='researcher')
def create(username: str, email: str, password: str, full_name: Optional[str], institution: Optional[str], role: str):
    """Create a new user."""
    from metapython.database import get_database, UserCRUD, UserRole

    try:
        db = get_database()

        with db.session_scope() as session:
            user = UserCRUD.create_user(
                session,
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                institution=institution,
                role=UserRole[role.upper()]
            )

        click.echo(click.style(f"✓ User created: {username} (id={user.id})", fg="green"))
        click.echo(f"Email: {user.email}")
        click.echo(f"Role: {user.role.value}")

    except Exception as e:
        click.echo(click.style(f"✗ User creation failed: {e}", fg="red"))
        sys.exit(1)


@user.command()
@click.option('--username', help='Filter by username')
@click.option('--role', type=click.Choice(['admin', 'researcher', 'reviewer', 'viewer']), help='Filter by role')
def list(username: Optional[str], role: Optional[str]):
    """List users."""
    from metapython.database import get_database, UserCRUD, UserRole

    try:
        db = get_database()

        with db.session_scope() as session:
            if username:
                user = UserCRUD.get_user_by_username(session, username)
                users = [user] if user else []
            else:
                role_enum = UserRole[role.upper()] if role else None
                users = UserCRUD.list_users(session, role=role_enum)

        if not users:
            click.echo("No users found")
            return

        click.echo(f"\nFound {len(users)} user(s):\n")

        for user in users:
            click.echo(f"ID: {user.id}")
            click.echo(f"Username: {user.username}")
            click.echo(f"Email: {user.email}")
            click.echo(f"Role: {user.role.value}")
            click.echo(f"Active: {'Yes' if user.is_active else 'No'}")
            click.echo(f"Verified: {'Yes' if user.is_verified else 'No'}")
            click.echo()

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))
        sys.exit(1)


# ========================================
# Project Commands
# ========================================

@cli.group()
def project():
    """Project management commands."""
    pass


@project.command()
@click.option('--user-id', type=int, required=True, help='Owner user ID')
@click.option('--title', prompt=True, help='Project title')
@click.option('--description', help='Project description')
@click.option('--effect-measure', type=click.Choice(['smd', 'md', 'or', 'rr', 'hr', 'proportion', 'correlation']), default='smd')
def create(user_id: int, title: str, description: Optional[str], effect_measure: str):
    """Create a new meta-analysis project."""
    from metapython.database import get_database, ProjectCRUD, EffectMeasure

    try:
        db = get_database()

        with db.session_scope() as session:
            project = ProjectCRUD.create_project(
                session,
                owner_id=user_id,
                title=title,
                description=description,
                effect_measure=EffectMeasure[effect_measure.upper()]
            )

        click.echo(click.style(f"✓ Project created: {title} (id={project.id})", fg="green"))
        click.echo(f"Effect measure: {project.effect_measure.value}")
        click.echo(f"Status: {project.status.value}")

    except Exception as e:
        click.echo(click.style(f"✗ Project creation failed: {e}", fg="red"))
        sys.exit(1)


@project.command()
@click.option('--user-id', type=int, required=True, help='User ID')
@click.option('--status', type=click.Choice(['draft', 'in_progress', 'completed', 'published', 'archived']), help='Filter by status')
def list(user_id: int, status: Optional[str]):
    """List user's projects."""
    from metapython.database import get_database, ProjectCRUD, AnalysisStatus

    try:
        db = get_database()

        with db.session_scope() as session:
            status_enum = AnalysisStatus[status.upper()] if status else None
            projects = ProjectCRUD.list_user_projects(session, user_id, status=status_enum)

        if not projects:
            click.echo("No projects found")
            return

        click.echo(f"\nFound {len(projects)} project(s):\n")

        for proj in projects:
            click.echo(f"ID: {proj.id}")
            click.echo(f"Title: {proj.title}")
            click.echo(f"Status: {proj.status.value}")
            click.echo(f"Studies: {proj.n_studies}")
            click.echo(f"Updated: {proj.updated_at}")
            click.echo()

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))
        sys.exit(1)


# ========================================
# Server Commands
# ========================================

@cli.group()
def server():
    """Server management commands."""
    pass


@server.command()
@click.option('--host', default='0.0.0.0', help='Host address')
@click.option('--port', default=8000, type=int, help='Port number')
@click.option('--reload/--no-reload', default=False, help='Enable auto-reload')
def start(host: str, port: int, reload: bool):
    """Start FastAPI server."""
    import uvicorn

    click.echo(click.style("Starting MetaPython API server...", fg="blue"))
    click.echo(f"Server: http://{host}:{port}")
    click.echo(f"API docs: http://{host}:{port}/docs")

    try:
        uvicorn.run(
            "metapython.web_api.app:app",
            host=host,
            port=port,
            reload=reload
        )
    except KeyboardInterrupt:
        click.echo(click.style("\n✓ Server stopped", fg="yellow"))
    except Exception as e:
        click.echo(click.style(f"✗ Server error: {e}", fg="red"))
        sys.exit(1)


@server.command()
@click.option('--port', default=3000, type=int, help='Port number')
def frontend(port: int):
    """Start React frontend (development)."""
    import subprocess
    import os

    frontend_dir = Path(__file__).parent.parent.parent / 'frontend'

    if not frontend_dir.exists():
        click.echo(click.style("✗ Frontend directory not found", fg="red"))
        sys.exit(1)

    click.echo(click.style("Starting React frontend...", fg="blue"))
    click.echo(f"Frontend: http://localhost:{port}")

    try:
        env = os.environ.copy()
        env['PORT'] = str(port)

        subprocess.run(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            env=env
        )
    except KeyboardInterrupt:
        click.echo(click.style("\n✓ Frontend stopped", fg="yellow"))
    except Exception as e:
        click.echo(click.style(f"✗ Frontend error: {e}", fg="red"))
        sys.exit(1)


# ========================================
# Analysis Commands
# ========================================

@cli.group()
def analyze():
    """Run meta-analysis."""
    pass


@analyze.command()
@click.option('--project-id', type=int, required=True, help='Project ID')
@click.option('--method', type=click.Choice(['fixed', 'random', 'bayesian']), default='random', help='Analysis method')
@click.option('--output', type=click.Path(), help='Output file path')
def run(project_id: int, method: str, output: Optional[str]):
    """Run meta-analysis on a project."""
    from metapython.database import get_database, ProjectCRUD, StudyCRUD
    from metapython.core.meta_analysis import run_meta_analysis

    try:
        db = get_database()

        with db.session_scope() as session:
            # Get project
            project = ProjectCRUD.get_project(session, project_id)
            if not project:
                click.echo(click.style(f"✗ Project {project_id} not found", fg="red"))
                sys.exit(1)

            # Get included studies
            studies = StudyCRUD.get_included_studies(session, project_id)

            if len(studies) < 2:
                click.echo(click.style(f"✗ Insufficient studies: {len(studies)} (minimum 2 required)", fg="red"))
                sys.exit(1)

            click.echo(f"Running {method} meta-analysis on {len(studies)} studies...")

            # Extract data
            effects = [s.effect_size for s in studies]
            variances = [s.variance for s in studies]

            # Run analysis
            result = run_meta_analysis(effects, variances, method=method)

            # Display results
            click.echo(click.style("\n✓ Analysis completed", fg="green"))
            click.echo(f"\nPooled effect: {result['pooled_effect']:.3f} [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")
            click.echo(f"P-value: {result['p_value']:.4f}")

            if 'i2' in result:
                click.echo(f"\nHeterogeneity:")
                click.echo(f"  I²: {result['i2']:.1f}%")
                click.echo(f"  τ²: {result['tau2']:.3f}")

            # Save results
            if output:
                import json
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2)
                click.echo(f"\nResults saved to: {output}")

    except Exception as e:
        click.echo(click.style(f"✗ Analysis failed: {e}", fg="red"))
        logger.exception("Analysis error")
        sys.exit(1)


# ========================================
# Main Entry Point
# ========================================

def main():
    """Main CLI entry point."""
    cli()


if __name__ == '__main__':
    main()


__all__ = ['cli', 'main']
