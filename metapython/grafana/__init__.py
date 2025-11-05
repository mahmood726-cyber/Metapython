"""
Grafana Dashboard Integration

Real-time monitoring and visualization of meta-analysis metrics:
- Live heterogeneity tracking
- Publication bias monitoring
- Effect size dashboards
- Study flow visualization
- ML model performance metrics
- Collaborative analytics
"""

from metapython.grafana.dashboard_builder import (
    GrafanaDashboard,
    create_meta_analysis_dashboard,
    create_realtime_dashboard,
)

from metapython.grafana.metrics_exporter import (
    MetricsExporter,
    export_to_prometheus,
    export_to_influxdb,
)

from metapython.grafana.panels import (
    create_heterogeneity_panel,
    create_forest_plot_panel,
    create_funnel_plot_panel,
    create_study_flow_panel,
)

__all__ = [
    # Dashboard builder
    'GrafanaDashboard',
    'create_meta_analysis_dashboard',
    'create_realtime_dashboard',

    # Metrics
    'MetricsExporter',
    'export_to_prometheus',
    'export_to_influxdb',

    # Panels
    'create_heterogeneity_panel',
    'create_forest_plot_panel',
    'create_funnel_plot_panel',
    'create_study_flow_panel',
]
