"""
Grafana Dashboard Builder

Create comprehensive Grafana dashboards for meta-analysis:
- Real-time metrics
- Time-series analysis
- Interactive plots
- Alerting rules
- Multiple data sources (Prometheus, InfluxDB)
"""

from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass, asdict

from metapython.core.config import logger


@dataclass
class GrafanaPanel:
    """Grafana dashboard panel configuration."""
    id: int
    title: str
    type: str
    gridPos: Dict[str, int]
    targets: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None
    fieldConfig: Optional[Dict[str, Any]] = None


class GrafanaDashboard:
    """
    Comprehensive Grafana dashboard builder for meta-analysis.

    Features:
    - Pre-configured meta-analysis dashboards
    - Custom panel layouts
    - Multi-datasource support
    - Real-time updates
    - Alert configuration
    - JSON export for Grafana import

    Example:
        >>> dashboard = GrafanaDashboard("Meta-Analysis Monitoring")
        >>> dashboard.add_heterogeneity_panel()
        >>> dashboard.add_effect_size_panel()
        >>> json_config = dashboard.export()
    """

    def __init__(
        self,
        title: str = "MetaPython Dashboard",
        uid: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Initialize dashboard builder.

        Args:
            title: Dashboard title
            uid: Unique dashboard ID
            tags: Dashboard tags for organization
        """
        self.title = title
        self.uid = uid or self._generate_uid()
        self.tags = tags or ['meta-analysis', 'metapython']
        self.panels = []
        self.panel_id_counter = 1

    def _generate_uid(self) -> str:
        """Generate unique dashboard ID."""
        import hashlib
        import time
        uid_string = f"{self.title}_{time.time()}"
        return hashlib.md5(uid_string.encode()).hexdigest()[:12]

    def add_panel(self, panel: GrafanaPanel) -> 'GrafanaDashboard':
        """
        Add panel to dashboard.

        Args:
            panel: Panel configuration

        Returns:
            Self for chaining
        """
        self.panels.append(panel)
        return self

    def add_heterogeneity_panel(
        self,
        datasource: str = "Prometheus",
        x: int = 0,
        y: int = 0,
        width: int = 12,
        height: int = 8
    ) -> 'GrafanaDashboard':
        """
        Add heterogeneity monitoring panel.

        Displays I², τ², and Q statistics over time.
        """
        panel = GrafanaPanel(
            id=self.panel_id_counter,
            title="Heterogeneity Metrics",
            type="timeseries",
            gridPos={"x": x, "y": y, "w": width, "h": height},
            targets=[
                {
                    "expr": "metapython_I2",
                    "legendFormat": "I² statistic",
                    "refId": "A"
                },
                {
                    "expr": "metapython_tau2",
                    "legendFormat": "τ² (between-study variance)",
                    "refId": "B"
                },
                {
                    "expr": "metapython_Q / 100",
                    "legendFormat": "Q statistic / 100",
                    "refId": "C"
                }
            ],
            options={
                "tooltip": {"mode": "multi"},
                "legend": {"displayMode": "list", "placement": "bottom"},
            },
            fieldConfig={
                "defaults": {
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 10,
                        "spanNulls": True
                    },
                    "unit": "percent",
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "green"},
                            {"value": 50, "color": "yellow"},
                            {"value": 75, "color": "red"}
                        ]
                    }
                }
            }
        )

        self.panel_id_counter += 1
        return self.add_panel(panel)

    def add_effect_size_panel(
        self,
        datasource: str = "Prometheus",
        x: int = 12,
        y: int = 0,
        width: int = 12,
        height: int = 8
    ) -> 'GrafanaDashboard':
        """Add pooled effect size panel with confidence intervals."""
        panel = GrafanaPanel(
            id=self.panel_id_counter,
            title="Pooled Effect Size",
            type="timeseries",
            gridPos={"x": x, "y": y, "w": width, "h": height},
            targets=[
                {
                    "expr": "metapython_pooled_effect",
                    "legendFormat": "Pooled Effect",
                    "refId": "A"
                },
                {
                    "expr": "metapython_ci_lower",
                    "legendFormat": "95% CI Lower",
                    "refId": "B"
                },
                {
                    "expr": "metapython_ci_upper",
                    "legendFormat": "95% CI Upper",
                    "refId": "C"
                }
            ],
            options={
                "tooltip": {"mode": "multi"},
                "legend": {"displayMode": "list", "placement": "bottom"},
            },
            fieldConfig={
                "defaults": {
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 0
                    },
                    "unit": "short"
                }
            }
        )

        self.panel_id_counter += 1
        return self.add_panel(panel)

    def add_study_count_panel(
        self,
        datasource: str = "Prometheus",
        x: int = 0,
        y: int = 8,
        width: int = 6,
        height: int = 6
    ) -> 'GrafanaDashboard':
        """Add study count gauge panel."""
        panel = GrafanaPanel(
            id=self.panel_id_counter,
            title="Number of Studies",
            type="gauge",
            gridPos={"x": x, "y": y, "w": width, "h": height},
            targets=[
                {
                    "expr": "metapython_n_studies",
                    "refId": "A"
                }
            ],
            options={
                "showThresholdLabels": False,
                "showThresholdMarkers": True,
            },
            fieldConfig={
                "defaults": {
                    "unit": "short",
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 5, "color": "yellow"},
                            {"value": 10, "color": "green"}
                        ]
                    }
                }
            }
        )

        self.panel_id_counter += 1
        return self.add_panel(panel)

    def add_publication_bias_panel(
        self,
        datasource: str = "Prometheus",
        x: int = 6,
        y: int = 8,
        width: int = 6,
        height: int = 6
    ) -> 'GrafanaDashboard':
        """Add publication bias indicator panel."""
        panel = GrafanaPanel(
            id=self.panel_id_counter,
            title="Publication Bias Indicator",
            type="stat",
            gridPos={"x": x, "y": y, "w": width, "h": height},
            targets=[
                {
                    "expr": "metapython_egger_p_value",
                    "legendFormat": "Egger's p-value",
                    "refId": "A"
                }
            ],
            options={
                "graphMode": "none",
                "colorMode": "background",
                "textMode": "value_and_name",
            },
            fieldConfig={
                "defaults": {
                    "unit": "short",
                    "decimals": 4,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 0.05, "color": "green"}
                        ]
                    }
                }
            }
        )

        self.panel_id_counter += 1
        return self.add_panel(panel)

    def add_ml_prediction_panel(
        self,
        datasource: str = "Prometheus",
        x: int = 12,
        y: int = 8,
        width: int = 12,
        height: int = 6
    ) -> 'GrafanaDashboard':
        """Add ML prediction accuracy panel."""
        panel = GrafanaPanel(
            id=self.panel_id_counter,
            title="ML Model Performance",
            type="timeseries",
            gridPos={"x": x, "y": y, "w": width, "h": height},
            targets=[
                {
                    "expr": "metapython_ml_accuracy",
                    "legendFormat": "Heterogeneity Prediction Accuracy",
                    "refId": "A"
                },
                {
                    "expr": "metapython_ml_bias_detection",
                    "legendFormat": "Bias Detection AUC",
                    "refId": "B"
                }
            ],
            options={
                "tooltip": {"mode": "multi"},
                "legend": {"displayMode": "list", "placement": "bottom"},
            },
            fieldConfig={
                "defaults": {
                    "custom": {
                        "lineWidth": 2
                    },
                    "unit": "percentunit",
                    "min": 0,
                    "max": 1
                }
            }
        )

        self.panel_id_counter += 1
        return self.add_panel(panel)

    def add_realtime_updates_panel(
        self,
        datasource: str = "Prometheus",
        x: int = 0,
        y: int = 14,
        width: int = 24,
        height: int = 6
    ) -> 'GrafanaDashboard':
        """Add real-time collaboration updates panel."""
        panel = GrafanaPanel(
            id=self.panel_id_counter,
            title="Real-Time Collaboration Activity",
            type="logs",
            gridPos={"x": x, "y": y, "w": width, "h": height},
            targets=[
                {
                    "expr": "{job=\"metapython\"} |= \"collaboration\"",
                    "refId": "A"
                }
            ],
            options={
                "showTime": True,
                "wrapLogMessage": True,
                "sortOrder": "Descending"
            }
        )

        self.panel_id_counter += 1
        return self.add_panel(panel)

    def export(self) -> Dict[str, Any]:
        """
        Export dashboard as JSON for Grafana import.

        Returns:
            Dashboard JSON configuration
        """
        dashboard = {
            "dashboard": {
                "title": self.title,
                "uid": self.uid,
                "tags": self.tags,
                "timezone": "browser",
                "schemaVersion": 38,
                "version": 1,
                "refresh": "5s",
                "panels": [asdict(panel) for panel in self.panels],
                "time": {
                    "from": "now-6h",
                    "to": "now"
                },
                "timepicker": {
                    "refresh_intervals": ["5s", "10s", "30s", "1m", "5m"]
                },
                "annotations": {
                    "list": []
                },
                "templating": {
                    "list": []
                }
            },
            "overwrite": True
        }

        return dashboard

    def save_json(self, filepath: str) -> bool:
        """
        Save dashboard to JSON file.

        Args:
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            dashboard_json = self.export()
            with open(filepath, 'w') as f:
                json.dump(dashboard_json, f, indent=2)

            logger.info(f"Dashboard saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving dashboard: {e}")
            return False


def create_meta_analysis_dashboard() -> GrafanaDashboard:
    """
    Create comprehensive meta-analysis dashboard.

    Returns:
        Configured dashboard with all panels
    """
    dashboard = GrafanaDashboard(title="MetaPython: Comprehensive Meta-Analysis")

    # Add all panels in optimized layout
    dashboard.add_heterogeneity_panel(x=0, y=0, width=12, height=8)
    dashboard.add_effect_size_panel(x=12, y=0, width=12, height=8)
    dashboard.add_study_count_panel(x=0, y=8, width=6, height=6)
    dashboard.add_publication_bias_panel(x=6, y=8, width=6, height=6)
    dashboard.add_ml_prediction_panel(x=12, y=8, width=12, height=6)
    dashboard.add_realtime_updates_panel(x=0, y=14, width=24, height=6)

    logger.info("Created comprehensive meta-analysis dashboard")

    return dashboard


def create_realtime_dashboard() -> GrafanaDashboard:
    """
    Create real-time collaboration dashboard.

    Returns:
        Dashboard for live monitoring
    """
    dashboard = GrafanaDashboard(title="MetaPython: Real-Time Collaboration")

    # Focus on real-time metrics
    dashboard.add_effect_size_panel(x=0, y=0, width=16, height=10)
    dashboard.add_study_count_panel(x=16, y=0, width=8, height=5)
    dashboard.add_publication_bias_panel(x=16, y=5, width=8, height=5)
    dashboard.add_realtime_updates_panel(x=0, y=10, width=24, height=8)

    logger.info("Created real-time collaboration dashboard")

    return dashboard


__all__ = [
    'GrafanaPanel',
    'GrafanaDashboard',
    'create_meta_analysis_dashboard',
    'create_realtime_dashboard',
]
