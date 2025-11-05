"""
MetaPython Web API

FastAPI-based REST API for meta-analysis:
- RESTful endpoints for all meta-analysis methods
- WebSocket for real-time analysis
- Authentication and authorization
- Rate limiting and caching
- OpenAPI documentation
- CORS support for React frontend
"""

from metapython.web_api.app import create_app, app
from metapython.web_api.routes import (
    meta_analysis_router,
    visualization_router,
    r_integration_router,
    ml_router,
)

__all__ = [
    'create_app',
    'app',
    'meta_analysis_router',
    'visualization_router',
    'r_integration_router',
    'ml_router',
]
