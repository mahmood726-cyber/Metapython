"""
API Routes for MetaPython

Comprehensive REST endpoints for:
- Meta-analysis operations
- Visualizations
- R Shiny integration
- ML predictions
- Automated reporting
- Permutation tests
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd

from metapython.core.config import logger

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MetaAnalysisRequest(BaseModel):
    """Request model for meta-analysis."""
    effects: List[float] = Field(..., description="Effect sizes")
    variances: List[float] = Field(..., description="Variances")
    study_labels: Optional[List[str]] = None
    method: str = Field("random_effects", description="Method: fixed_effects or random_effects")
    alpha: float = Field(0.05, description="Significance level")


class VisualizationRequest(BaseModel):
    """Request model for visualization."""
    effects: List[float]
    se: List[float]
    study_labels: List[str]
    plot_type: str = Field(..., description="Plot type: forest, funnel, radial, etc.")
    title: Optional[str] = "Meta-Analysis Plot"
    journal_style: Optional[str] = "default"


class RIntegrationRequest(BaseModel):
    """Request model for R integration."""
    app_id: str = Field(..., description="Shiny app ID from catalog")
    port: int = Field(3838, description="Port number")
    data: Optional[Dict[str, Any]] = None


class MLPredictionRequest(BaseModel):
    """Request model for ML predictions."""
    study_characteristics: Dict[str, Any]
    prediction_type: str = Field(..., description="heterogeneity, publication_bias, or screening")


class ReportingRequest(BaseModel):
    """Request model for automated reporting."""
    section_type: str = Field(..., description="methods or results")
    data: Dict[str, Any]
    format: str = Field("markdown", description="markdown, latex, or html")


class PermutationRequest(BaseModel):
    """Request model for permutation tests."""
    effects: List[float]
    variances: List[float]
    test_type: str = Field(..., description="pooled_effect, heterogeneity, or publication_bias")
    n_permutations: int = Field(10000, description="Number of permutations")


# ============================================================================
# META-ANALYSIS ROUTER
# ============================================================================

meta_analysis_router = APIRouter()


@meta_analysis_router.post("/fixed-effects")
async def fixed_effects_analysis(request: MetaAnalysisRequest):
    """Perform fixed-effects meta-analysis."""
    try:
        from metapython.core.utils import calculate_pooled_estimate

        effects = np.array(request.effects)
        variances = np.array(request.variances)

        result = calculate_pooled_estimate(effects, variances, method='fixed')

        return {
            "pooled_effect": float(result['pooled']),
            "se": float(result['se']),
            "ci_low": float(result['ci_low']),
            "ci_high": float(result['ci_high']),
            "z_statistic": float(result['z']),
            "p_value": float(result['p']),
            "method": "Fixed-effects"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@meta_analysis_router.post("/random-effects")
async def random_effects_analysis(request: MetaAnalysisRequest):
    """Perform random-effects meta-analysis."""
    try:
        from metapython.core.utils import calculate_pooled_estimate

        effects = np.array(request.effects)
        variances = np.array(request.variances)

        result = calculate_pooled_estimate(effects, variances, method='random')

        return {
            "pooled_effect": float(result['pooled']),
            "se": float(result['se']),
            "ci_low": float(result['ci_low']),
            "ci_high": float(result['ci_high']),
            "z_statistic": float(result['z']),
            "p_value": float(result['p']),
            "tau2": float(result.get('tau2', 0)),
            "I2": float(result.get('I2', 0)),
            "method": "Random-effects"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@meta_analysis_router.post("/heterogeneity")
async def heterogeneity_assessment(request: MetaAnalysisRequest):
    """Assess heterogeneity."""
    try:
        effects = np.array(request.effects)
        variances = np.array(request.variances)

        # Calculate heterogeneity statistics
        weights = 1 / variances
        pooled = np.sum(weights * effects) / np.sum(weights)
        Q = np.sum(weights * (effects - pooled) ** 2)
        df = len(effects) - 1
        C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau2 = max(0, (Q - df) / C)
        I2 = max(0, 100 * (Q - df) / Q) if Q > 0 else 0

        from scipy import stats
        p_hetero = 1 - stats.chi2.cdf(Q, df)

        return {
            "Q": float(Q),
            "df": int(df),
            "p_value": float(p_hetero),
            "tau2": float(tau2),
            "I2": float(I2),
            "interpretation": "Low" if I2 < 25 else "Moderate" if I2 < 50 else "Substantial" if I2 < 75 else "Considerable"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VISUALIZATION ROUTER
# ============================================================================

visualization_router = APIRouter()


@visualization_router.post("/forest-plot")
async def generate_forest_plot(request: VisualizationRequest):
    """Generate forest plot."""
    try:
        from metapython.enhanced_viz import advanced_forest_plot
        import base64
        from io import BytesIO

        effects = np.array(request.effects)
        se = np.array(request.se)
        labels = np.array(request.study_labels)

        # Calculate pooled
        weights = 1 / (se ** 2)
        pooled = np.sum(weights * effects) / np.sum(weights)
        pooled_se = np.sqrt(1 / np.sum(weights))

        fig = advanced_forest_plot(
            effects=effects,
            se=se,
            study_labels=labels,
            pooled_effect=pooled,
            pooled_se=pooled_se,
            title=request.title,
            journal_style=request.journal_style
        )

        # Convert to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()

        return {
            "image": f"data:image/png;base64,{img_base64}",
            "format": "png"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@visualization_router.post("/interactive-dashboard")
async def generate_dashboard(request: VisualizationRequest):
    """Generate interactive dashboard."""
    try:
        from metapython.enhanced_viz import create_meta_analysis_dashboard

        effects = np.array(request.effects)
        se = np.array(request.se)
        labels = np.array(request.study_labels)

        # Calculate pooled
        variances = se ** 2
        weights = 1 / variances
        pooled = np.sum(weights * effects) / np.sum(weights)
        pooled_se = np.sqrt(1 / np.sum(weights))

        # Heterogeneity
        Q = np.sum(weights * (effects - pooled) ** 2)
        df = len(effects) - 1
        I2 = max(0, 100 * (Q - df) / Q) if Q > 0 else 0
        C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau2 = max(0, (Q - df) / C)

        fig = create_meta_analysis_dashboard(
            effects=effects,
            se=se,
            study_labels=labels,
            pooled_effect=pooled,
            pooled_se=pooled_se,
            heterogeneity={'I2': I2, 'tau2': tau2, 'Q': Q}
        )

        # Return Plotly JSON
        return {
            "plot": fig.to_json(),
            "type": "plotly"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# R INTEGRATION ROUTER
# ============================================================================

r_integration_router = APIRouter()


@r_integration_router.get("/shiny-apps")
async def list_shiny_apps():
    """List available Shiny apps."""
    try:
        from metapython.r_integration import ShinyAppCatalog

        apps = ShinyAppCatalog.list_apps()
        return {"apps": apps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@r_integration_router.post("/launch-shiny-app")
async def launch_shiny(request: RIntegrationRequest):
    """Launch Shiny app."""
    try:
        from metapython.r_integration import launch_shiny_app

        wrapper = launch_shiny_app(request.app_id, port=request.port)

        return {
            "status": "launched",
            "app_id": request.app_id,
            "url": wrapper.get_url(),
            "port": request.port
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@r_integration_router.post("/network-meta-analysis")
async def r_network_meta(data: Dict[str, Any] = Body(...)):
    """Run network meta-analysis in R."""
    try:
        from metapython.r_integration import r_network_meta_analysis

        result = r_network_meta_analysis(
            studies=pd.DataFrame(data['studies']),
            method=data.get('method', 'frequentist')
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ML ROUTER
# ============================================================================

ml_router = APIRouter()


@ml_router.post("/predict-heterogeneity")
async def predict_heterogeneity(request: MLPredictionRequest):
    """Predict heterogeneity using ML."""
    try:
        from metapython.ml_meta import predict_heterogeneity

        result = predict_heterogeneity(request.study_characteristics)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# REPORTING ROUTER
# ============================================================================

reporting_router = APIRouter()


@reporting_router.post("/generate-methods")
async def generate_methods_section(request: ReportingRequest):
    """Generate PRISMA-compliant methods section."""
    try:
        from metapython.reporting import generate_methods_section

        result = generate_methods_section(
            methods_data=request.data,
            format=request.format
        )

        return {
            "text": result['text'],
            "compliance_score": result['compliance_score'],
            "validation": result['validation']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@reporting_router.post("/generate-results")
async def generate_results_section(request: ReportingRequest):
    """Generate PRISMA-compliant results section."""
    try:
        from metapython.reporting import generate_results_section

        result = generate_results_section(
            results_data=request.data,
            format=request.format
        )

        return {
            "text": result['text'],
            "compliance_score": result['compliance_score'],
            "validation": result['validation']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PERMUTATIONS ROUTER
# ============================================================================

permutations_router = APIRouter()


@permutations_router.post("/permutation-test")
async def run_permutation_test(request: PermutationRequest):
    """Run permutation test."""
    try:
        from metapython.permutations import run_permutation_test

        result = run_permutation_test(
            effects=np.array(request.effects),
            variances=np.array(request.variances),
            test_type=request.test_type,
            n_permutations=request.n_permutations
        )

        return {
            "observed_statistic": result.observed_statistic,
            "p_value": result.p_value,
            "p_value_two_sided": result.p_value_two_sided,
            "ci_lower": result.ci_lower,
            "ci_upper": result.ci_upper,
            "n_permutations": result.n_permutations,
            "method": result.method
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


__all__ = [
    'meta_analysis_router',
    'visualization_router',
    'r_integration_router',
    'ml_router',
    'reporting_router',
    'permutations_router',
]
