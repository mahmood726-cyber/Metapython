"""
Command-Line Interface for MetaPython

Comprehensive CLI tool for:
- Database management
- User operations
- Project management
- Analysis execution
- Server control

Usage:
    $ metapython --help
    $ metapython db init
    $ metapython user create
    $ metapython project create
    $ metapython analyze run --project-id 1
    $ metapython server start
"""

from metapython.cli.main import cli, main

__all__ = ['cli', 'main']
