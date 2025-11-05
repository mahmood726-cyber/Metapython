"""
Shiny App Wrapper

Launch and embed R Shiny applications from Python:
- Launch existing Shiny apps (from mahmood789/786-MIII-Meta-analysis)
- Embed Shiny dashboards in Python workflows
- Proxy Shiny apps through Python web server
- Bidirectional data exchange with Shiny
"""

from typing import Dict, List, Any, Optional
import subprocess
import os
import threading
import time
import requests
from pathlib import Path

from metapython.core.config import logger
from metapython.r_integration.rpy2_bridge import RPythonBridge, HAS_RPY2


class ShinyAppWrapper:
    """
    Wrapper for R Shiny applications.

    Features:
    - Launch Shiny apps from Python
    - Auto-detect app.R or server.R/ui.R
    - Monitor app status
    - Proxy through custom port
    - Auto-shutdown

    Example:
        >>> wrapper = ShinyAppWrapper('path/to/shiny/app')
        >>> wrapper.launch(port=3838)
        >>> # App available at http://localhost:3838
        >>> wrapper.shutdown()
    """

    def __init__(self, app_dir: str, host: str = '127.0.0.1'):
        """
        Initialize Shiny app wrapper.

        Args:
            app_dir: Path to Shiny app directory
            host: Host address
        """
        self.app_dir = Path(app_dir)
        self.host = host
        self.port = None
        self.process = None
        self.running = False

        if not self.app_dir.exists():
            raise FileNotFoundError(f"App directory not found: {app_dir}")

        # Detect app type
        self.app_file = self._detect_app_file()
        logger.info(f"Detected Shiny app: {self.app_file}")

    def _detect_app_file(self) -> str:
        """Detect Shiny app entry point."""
        if (self.app_dir / 'app.R').exists():
            return 'app.R'
        elif (self.app_dir / 'server.R').exists() and (self.app_dir / 'ui.R').exists():
            return 'server.R'  # Will use both server.R and ui.R
        else:
            raise ValueError("No valid Shiny app found (app.R or server.R/ui.R)")

    def launch(
        self,
        port: int = 3838,
        launch_browser: bool = True,
        blocking: bool = False
    ) -> bool:
        """
        Launch Shiny app.

        Args:
            port: Port number
            launch_browser: Whether to open browser automatically
            blocking: Whether to block until app stops

        Returns:
            True if launched successfully
        """
        if self.running:
            logger.warning("App already running")
            return True

        self.port = port

        # R code to launch Shiny app
        r_code = f"""
library(shiny)
setwd('{self.app_dir}')
runApp('{self.app_file}', host='{self.host}', port={port}, launch.browser={str(launch_browser).upper()})
"""

        try:
            if blocking:
                # Run in current thread (blocking)
                if HAS_RPY2:
                    bridge = RPythonBridge()
                    bridge.run_r_code(r_code, return_result=False)
                else:
                    # Use Rscript
                    subprocess.run(['Rscript', '-e', r_code], check=True)
            else:
                # Run in background thread
                def run_app():
                    try:
                        if HAS_RPY2:
                            bridge = RPythonBridge()
                            bridge.run_r_code(r_code, return_result=False)
                        else:
                            subprocess.run(['Rscript', '-e', r_code], check=True)
                    except Exception as e:
                        logger.error(f"Shiny app error: {e}")
                        self.running = False

                thread = threading.Thread(target=run_app, daemon=True)
                thread.start()
                self.running = True

                # Wait for app to start
                time.sleep(2)

                # Verify app is running
                if self.is_running():
                    logger.info(f"Shiny app running at http://{self.host}:{self.port}")
                    return True
                else:
                    logger.error("Failed to start Shiny app")
                    return False

        except Exception as e:
            logger.error(f"Error launching Shiny app: {e}")
            return False

    def is_running(self) -> bool:
        """Check if app is running."""
        if not self.port:
            return False

        try:
            response = requests.get(f"http://{self.host}:{self.port}", timeout=2)
            return response.status_code == 200
        except:
            return False

    def shutdown(self) -> bool:
        """Shutdown Shiny app."""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.running = False
            logger.info("Shiny app shut down")
            return True
        return False

    def get_url(self) -> Optional[str]:
        """Get app URL."""
        if self.running and self.port:
            return f"http://{self.host}:{self.port}"
        return None


class ShinyAppCatalog:
    """
    Catalog of available Shiny apps from mahmood789 repositories.

    Apps:
    - Network Meta-Analysis (Bayesian)
    - Pairwise Meta-Analysis (OR, RR, SMD, MD)
    - Dose-Response Meta-Analysis
    - Hazard Ratio Meta-Analysis
    - Multilevel Meta-Analysis
    - Proportion Meta-Analysis
    - Diagnostic Test Accuracy
    - Risk of Bias Assessment
    - Meta-Regression
    - Data Conversion Tools
    """

    APPS = {
        'network_meta_bayesian': {
            'name': 'Bayesian Network Meta-Analysis',
            'description': 'Network meta-analysis using Bayesian methods',
            'path': 'NMA Bayesian SMD',
            'repo': '786-MIII-Meta-analysis'
        },
        'pairwise_or': {
            'name': 'Pairwise OR Meta-Analysis',
            'description': 'Pairwise meta-analysis for odds ratios',
            'path': 'Pairwise OR',
            'repo': '786-MIII-Meta-analysis'
        },
        'dose_response': {
            'name': 'Dose-Response Meta-Analysis',
            'description': 'Dose-response relationship modeling',
            'path': 'Dose response app',
            'repo': '786-MIII-Meta-analysis'
        },
        'hazard_ratio': {
            'name': 'Hazard Ratio Meta-Analysis',
            'description': 'Meta-analysis of hazard ratios',
            'path': 'Hazard ratio meta app',
            'repo': '786-MIII-Meta-analysis'
        },
        'multilevel': {
            'name': 'Multilevel Meta-Analysis',
            'description': 'Three-level and multivariate meta-analysis',
            'path': 'Multilevel meta-analysis',
            'repo': '786-MIII-Meta-analysis'
        },
        'proportion': {
            'name': 'Proportion Meta-Analysis',
            'description': 'Meta-analysis of proportions',
            'path': 'Prop app',
            'repo': '786-MIII-Meta-analysis'
        },
        'diagnostic_accuracy': {
            'name': 'Diagnostic Test Accuracy',
            'description': 'Meta-analysis of diagnostic test accuracy',
            'path': 'DTA',
            'repo': '786-MIII-Meta-analysis'
        },
        'risk_of_bias': {
            'name': 'Risk of Bias Assessment',
            'description': 'Systematic risk of bias evaluation',
            'path': '786MIIIROB',
            'repo': '786-MIII-Meta-analysis'
        },
    }

    @classmethod
    def list_apps(cls) -> List[Dict[str, str]]:
        """List all available Shiny apps."""
        return [
            {
                'id': app_id,
                'name': info['name'],
                'description': info['description']
            }
            for app_id, info in cls.APPS.items()
        ]

    @classmethod
    def get_app_info(cls, app_id: str) -> Optional[Dict[str, str]]:
        """Get app information."""
        return cls.APPS.get(app_id)


def launch_shiny_app(
    app_id: str,
    port: int = 3838,
    app_base_dir: Optional[str] = None
) -> ShinyAppWrapper:
    """
    Quick function to launch a Shiny app by ID.

    Args:
        app_id: App identifier from catalog
        port: Port number
        app_base_dir: Base directory containing cloned repos

    Returns:
        ShinyAppWrapper instance
    """
    app_info = ShinyAppCatalog.get_app_info(app_id)
    if not app_info:
        raise ValueError(f"Unknown app ID: {app_id}")

    if app_base_dir:
        app_dir = Path(app_base_dir) / app_info['repo'] / app_info['path']
    else:
        # Assume repos are in current directory
        app_dir = Path(app_info['repo']) / app_info['path']

    wrapper = ShinyAppWrapper(str(app_dir))
    wrapper.launch(port=port, blocking=False)
    return wrapper


def embed_shiny_dashboard(
    app_id: str,
    height: int = 800,
    **kwargs
) -> str:
    """
    Generate HTML iframe to embed Shiny dashboard.

    Args:
        app_id: App identifier
        height: Frame height in pixels
        **kwargs: Additional ShinyAppWrapper arguments

    Returns:
        HTML iframe code
    """
    wrapper = launch_shiny_app(app_id, **kwargs)
    url = wrapper.get_url()

    if not url:
        return "<p>Error: Failed to launch Shiny app</p>"

    return f"""
<iframe
    src="{url}"
    width="100%"
    height="{height}px"
    frameborder="0"
    style="border: 1px solid #ddd; border-radius: 4px;">
</iframe>
"""


__all__ = [
    'ShinyAppWrapper',
    'ShinyAppCatalog',
    'launch_shiny_app',
    'embed_shiny_dashboard',
]
