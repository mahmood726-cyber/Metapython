"""
R-Based Plotting Endpoints for FastAPI
Publication-quality plots using metafor and meta packages
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np

from metapython.r_plotting import RMetaPlotter

router = APIRouter(prefix="/api/plots", tags=["R-based Plotting"])


class PlotRequest(BaseModel):
    """Request model for R-based plots."""
    effects: List[float]
    se: List[float]
    study_labels: Optional[List[str]] = None
    method: str = "REML"
    width: int = 1000
    height: int = 600


class ForestPlotRequest(PlotRequest):
    """Forest plot specific options."""
    show_weights: bool = True
    show_ci: bool = True
    show_prediction_interval: bool = True
    order_by: Optional[str] = None
    refline: float = 0
    title: Optional[str] = None
    use_meta_package: bool = False  # Use meta package instead of metafor
    layout: Optional[str] = "JAMA"  # For meta package


class FunnelPlotRequest(PlotRequest):
    """Funnel plot specific options."""
    show_contours: bool = True
    contour_levels: Optional[List[float]] = None
    trim_fill: bool = True
    egger_test: bool = True
    title: Optional[str] = None


class BaujatPlotRequest(PlotRequest):
    """Baujat plot options."""
    label_outliers: bool = True


class GOSHPlotRequest(PlotRequest):
    """GOSH plot options."""
    n_subsets: int = 1000


class LabbishPlotRequest(BaseModel):
    """L'Abbé plot for binary data."""
    events_exp: List[int]
    n_exp: List[int]
    events_ctrl: List[int]
    n_ctrl: List[int]
    study_labels: Optional[List[str]] = None
    width: int = 800
    height: int = 800


class CumulativePlotRequest(PlotRequest):
    """Cumulative forest plot options."""
    order_by: Optional[List[float]] = None  # e.g., publication years


@router.post("/forest-metafor")
async def forest_plot_metafor(request: ForestPlotRequest):
    """
    Create publication-quality forest plot using metafor.

    This produces the gold-standard forest plot used in medical journals.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        variances = np.array(request.se) ** 2
        study_labels = np.array(request.study_labels) if request.study_labels else None

        plot_base64 = plotter.forest_plot_metafor(
            effects=effects,
            variances=variances,
            study_labels=study_labels,
            method=request.method,
            show_weights=request.show_weights,
            show_ci=request.show_ci,
            show_prediction_interval=request.show_prediction_interval,
            refline=request.refline,
            title=request.title,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "forest_metafor",
            "image": plot_base64,
            "format": "png",
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forest-meta")
async def forest_plot_meta(request: ForestPlotRequest):
    """
    Create forest plot using meta package (JAMA/RevMan style).

    The meta package offers different journal-specific layouts.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        se = np.array(request.se)
        study_labels = np.array(request.study_labels) if request.study_labels else None

        plot_base64 = plotter.forest_plot_meta(
            effects=effects,
            se=se,
            study_labels=study_labels,
            sm="MD",  # Can be made configurable
            method_tau=request.method,
            prediction=request.show_prediction_interval,
            layout=request.layout or "JAMA",
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "forest_meta",
            "image": plot_base64,
            "format": "png",
            "layout": request.layout,
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/funnel-metafor")
async def funnel_plot_metafor(request: FunnelPlotRequest):
    """
    Create publication-quality funnel plot using metafor.

    Includes optional trim-and-fill and Egger's test.

    Returns:
        Dict with base64 image and test results
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        variances = np.array(request.se) ** 2
        study_labels = np.array(request.study_labels) if request.study_labels else None

        result = plotter.funnel_plot_metafor(
            effects=effects,
            variances=variances,
            study_labels=study_labels,
            method=request.method,
            show_contours=request.show_contours,
            contour_levels=request.contour_levels,
            trim_fill=request.trim_fill,
            egger_test=request.egger_test,
            title=request.title,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "funnel_metafor",
            "image": result['plot'],
            "format": "png",
            "egger_test": result.get('egger_test'),
            "trim_fill": result.get('trim_fill'),
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/baujat")
async def baujat_plot(request: BaujatPlotRequest):
    """
    Create Baujat plot for outlier detection.

    Identifies studies contributing most to heterogeneity
    and having high influence on pooled effect.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        variances = np.array(request.se) ** 2
        study_labels = np.array(request.study_labels) if request.study_labels else None

        plot_base64 = plotter.baujat_plot(
            effects=effects,
            variances=variances,
            study_labels=study_labels,
            method=request.method,
            label_outliers=request.label_outliers,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "baujat",
            "image": plot_base64,
            "format": "png",
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/radial")
async def radial_plot(request: PlotRequest):
    """
    Create Radial (Galbraith) plot.

    Displays studies on a standardized scale for
    visual assessment of heterogeneity.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        variances = np.array(request.se) ** 2
        study_labels = np.array(request.study_labels) if request.study_labels else None

        plot_base64 = plotter.radial_plot(
            effects=effects,
            variances=variances,
            study_labels=study_labels,
            method=request.method,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "radial",
            "image": plot_base64,
            "format": "png",
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gosh")
async def gosh_plot(request: GOSHPlotRequest):
    """
    Create GOSH (Graphical Display of Study Heterogeneity) plot.

    Shows all possible meta-analysis results from different
    combinations of studies.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        variances = np.array(request.se) ** 2

        plot_base64 = plotter.gosh_plot(
            effects=effects,
            variances=variances,
            n_subsets=request.n_subsets,
            method=request.method,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "gosh",
            "image": plot_base64,
            "format": "png",
            "n_subsets": request.n_subsets,
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/labbe")
async def labbe_plot(request: LabbishPlotRequest):
    """
    Create L'Abbé plot for binary outcome data.

    Shows event rates in experimental vs. control groups.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        events_exp = np.array(request.events_exp)
        n_exp = np.array(request.n_exp)
        events_ctrl = np.array(request.events_ctrl)
        n_ctrl = np.array(request.n_ctrl)
        study_labels = np.array(request.study_labels) if request.study_labels else None

        plot_base64 = plotter.labbe_plot(
            events_exp=events_exp,
            n_exp=n_exp,
            events_ctrl=events_ctrl,
            n_ctrl=n_ctrl,
            study_labels=study_labels,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "labbe",
            "image": plot_base64,
            "format": "png",
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cumulative")
async def cumulative_forest_plot(request: CumulativePlotRequest):
    """
    Create cumulative forest plot.

    Shows pooled effect as studies are added sequentially.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        variances = np.array(request.se) ** 2
        study_labels = np.array(request.study_labels) if request.study_labels else None
        order_by = np.array(request.order_by) if request.order_by else None

        plot_base64 = plotter.cumulative_forest_plot(
            effects=effects,
            variances=variances,
            study_labels=study_labels,
            order_by=order_by,
            method=request.method,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "cumulative",
            "image": plot_base64,
            "format": "png",
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leave-one-out")
async def leave_one_out_plot(request: PlotRequest):
    """
    Create leave-one-out forest plot.

    Shows pooled effect with each study removed sequentially.

    Returns:
        Base64 encoded PNG image
    """
    try:
        plotter = RMetaPlotter()

        effects = np.array(request.effects)
        variances = np.array(request.se) ** 2
        study_labels = np.array(request.study_labels) if request.study_labels else None

        plot_base64 = plotter.leave_one_out_plot(
            effects=effects,
            variances=variances,
            study_labels=study_labels,
            method=request.method,
            width=request.width,
            height=request.height
        )

        return {
            "plot_type": "leave_one_out",
            "image": plot_base64,
            "format": "png",
            "width": request.width,
            "height": request.height
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
