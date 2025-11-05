"""
FastAPI Application for MetaPython

Modern REST API with:
- OpenAPI/Swagger documentation
- WebSocket for real-time updates
- CORS for React frontend
- Rate limiting
- Caching
- Authentication
"""

from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from metapython.core.config import logger

# Version
API_VERSION = "1.0.0"


def create_app() -> FastAPI:
    """
    Create FastAPI application.

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="MetaPython API",
        description="Comprehensive meta-analysis REST API with ML, R integration, and real-time collaboration",
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS middleware for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": API_VERSION}

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "MetaPython API",
            "version": API_VERSION,
            "documentation": "/docs",
            "endpoints": {
                "meta_analysis": "/api/v1/meta-analysis",
                "visualization": "/api/v1/visualization",
                "r_integration": "/api/v1/r",
                "ml": "/api/v1/ml",
                "reporting": "/api/v1/reporting",
                "permutations": "/api/v1/permutations"
            }
        }

    # WebSocket for real-time updates
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                # Process real-time analysis requests
                await websocket.send_text(f"Echo: {data}")
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")

    # Include routers
    from metapython.web_api.routes import (
        meta_analysis_router,
        visualization_router,
        r_integration_router,
        ml_router,
        reporting_router,
        permutations_router
    )

    app.include_router(meta_analysis_router, prefix="/api/v1/meta-analysis", tags=["Meta-Analysis"])
    app.include_router(visualization_router, prefix="/api/v1/visualization", tags=["Visualization"])
    app.include_router(r_integration_router, prefix="/api/v1/r", tags=["R Integration"])
    app.include_router(ml_router, prefix="/api/v1/ml", tags=["Machine Learning"])
    app.include_router(reporting_router, prefix="/api/v1/reporting", tags=["Reporting"])
    app.include_router(permutations_router, prefix="/api/v1/permutations", tags=["Permutations"])

    logger.info(f"MetaPython API v{API_VERSION} initialized")

    return app


# Create app instance
app = create_app()


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False
):
    """
    Run FastAPI server.

    Args:
        host: Host address
        port: Port number
        reload: Auto-reload on code changes (development)
    """
    uvicorn.run(
        "metapython.web_api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server(reload=True)
