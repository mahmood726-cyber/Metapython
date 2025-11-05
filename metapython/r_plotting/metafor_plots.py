"""
R-Based Publication-Quality Plotting
Uses metafor and meta packages for world-class visualizations

This module provides publication-ready plots that match or exceed
journal standards. All plots are generated using R's metafor and meta
packages, which are the gold standard in meta-analysis.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
import base64
import io
import tempfile
import os
from pathlib import Path

from metapython.core.config import HAS_RPY2, logger

if HAS_RPY2:
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri, numpy2ri
    from rpy2.robjects.packages import importr

    # Activate pandas and numpy conversion
    pandas2ri.activate()
    numpy2ri.activate()

    # Import R packages
    try:
        metafor = importr('metafor')
        meta = importr('meta')
        grdevices = importr('grDevices')
        graphics = importr('graphics')
    except Exception as e:
        logger.warning(f"Failed to import R packages: {e}")
        HAS_RPY2 = False


class RMetaPlotter:
    """
    Publication-quality meta-analysis plots using R's metafor and meta packages.

    Features:
    - Forest plots with custom layouts
    - Funnel plots with trim-and-fill
    - Radial (Galbraith) plots
    - Baujat plots for outlier detection
    - GOSH plots for heterogeneity
    - L'Abbé plots for binary data
    - Cumulative forest plots
    - Leave-one-out plots

    All plots are publication-ready and can be exported as PNG, SVG, or PDF.
    """

    def __init__(self):
        """Initialize R plotter."""
        if not HAS_RPY2:
            raise ImportError(
                "rpy2 is required for R-based plotting. "
                "Install with: pip install rpy2"
            )

        self.r = ro.r

        # Check if required R packages are installed
        self._check_r_packages()

    def _check_r_packages(self):
        """Check if required R packages are installed."""
        required_packages = ['metafor', 'meta']

        for pkg in required_packages:
            try:
                importr(pkg)
            except Exception:
                logger.warning(
                    f"R package '{pkg}' not found. "
                    f"Install with: install.packages('{pkg}')"
                )

    def _prepare_data(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        study_labels: Optional[np.ndarray] = None
    ) -> ro.DataFrame:
        """Prepare data for R plotting."""
        n_studies = len(effects)

        if study_labels is None:
            study_labels = np.array([f"Study {i+1}" for i in range(n_studies)])

        # Create R dataframe
        df = pd.DataFrame({
            'yi': effects,
            'vi': variances,
            'study': study_labels
        })

        return ro.conversion.py2rpy(df)

    def _save_plot_to_base64(
        self,
        plot_func,
        width: int = 800,
        height: int = 600,
        dpi: int = 150,
        format: str = 'png'
    ) -> str:
        """
        Save R plot to base64 encoded string.

        Args:
            plot_func: Function that generates the plot
            width: Plot width in pixels
            height: Plot height in pixels
            dpi: Resolution (dots per inch)
            format: Image format ('png', 'svg', 'pdf')

        Returns:
            Base64 encoded image string
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=f'.{format}',
            delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Open graphics device
            if format == 'png':
                grdevices.png(
                    tmp_path,
                    width=width,
                    height=height,
                    res=dpi
                )
            elif format == 'svg':
                grdevices.svg(
                    tmp_path,
                    width=width / dpi,
                    height=height / dpi
                )
            elif format == 'pdf':
                grdevices.pdf(
                    tmp_path,
                    width=width / dpi,
                    height=height / dpi
                )

            # Generate plot
            plot_func()

            # Close device
            grdevices.dev_off()

            # Read file and encode
            with open(tmp_path, 'rb') as f:
                img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')

            return img_base64

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def forest_plot_metafor(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        method: str = "REML",
        show_weights: bool = True,
        show_ci: bool = True,
        show_prediction_interval: bool = True,
        order_by: Optional[str] = None,
        xlim: Optional[Tuple[float, float]] = None,
        refline: float = 0,
        title: Optional[str] = None,
        width: int = 1000,
        height: int = 600
    ) -> str:
        """
        Create publication-quality forest plot using metafor.

        Args:
            effects: Effect sizes
            variances: Effect size variances
            study_labels: Study names
            method: Meta-analysis method (REML, DL, ML, etc.)
            show_weights: Show study weights
            show_ci: Show confidence intervals
            show_prediction_interval: Show prediction interval
            order_by: Order studies ('effect', 'weight', 'year', None)
            xlim: X-axis limits
            refline: Reference line position
            title: Plot title
            width: Plot width in pixels
            height: Plot height in pixels

        Returns:
            Base64 encoded PNG image
        """
        # Prepare data
        r_data = self._prepare_data(effects, variances, study_labels)

        def plot_func():
            # Fit meta-analysis model
            res = metafor.rma(
                yi=r_data.rx2('yi'),
                vi=r_data.rx2('vi'),
                slab=r_data.rx2('study'),
                method=method
            )

            # Create forest plot
            metafor.forest_rma(
                res,
                showweights=show_weights,
                addpred=show_prediction_interval,
                refline=refline,
                xlim=ro.FloatVector(xlim) if xlim else ro.NULL,
                header=True,
                top=2,
                mlab="Pooled Effect (Random Effects)",
                cex=0.8,
                col="darkblue",
                border="darkblue"
            )

            # Add title if provided
            if title:
                self.r('title')(main=title, cex_main=1.2, font_main=2)

        return self._save_plot_to_base64(plot_func, width, height)

    def funnel_plot_metafor(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        method: str = "REML",
        show_contours: bool = True,
        contour_levels: Optional[List[float]] = None,
        trim_fill: bool = False,
        egger_test: bool = True,
        title: Optional[str] = None,
        width: int = 800,
        height: int = 600
    ) -> Dict[str, Any]:
        """
        Create publication-quality funnel plot using metafor.

        Args:
            effects: Effect sizes
            variances: Effect size variances
            study_labels: Study names
            method: Meta-analysis method
            show_contours: Show significance contours
            contour_levels: Significance levels for contours
            trim_fill: Apply trim-and-fill method
            egger_test: Perform Egger's regression test
            title: Plot title
            width: Plot width
            height: Plot height

        Returns:
            Dict with plot (base64) and test results
        """
        # Prepare data
        r_data = self._prepare_data(effects, variances, study_labels)

        # Fit model
        res = metafor.rma(
            yi=r_data.rx2('yi'),
            vi=r_data.rx2('vi'),
            slab=r_data.rx2('study'),
            method=method
        )

        result = {}

        # Egger's test
        if egger_test:
            egger_result = metafor.regtest(res)
            result['egger_test'] = {
                'z': float(egger_result.rx2('zval')[0]),
                'p_value': float(egger_result.rx2('pval')[0]),
                'significant': float(egger_result.rx2('pval')[0]) < 0.05
            }

        # Trim-and-fill
        if trim_fill:
            tf_res = metafor.trimfill(res)
            result['trim_fill'] = {
                'n_imputed': int(tf_res.rx2('k0')[0]),
                'adjusted_effect': float(tf_res.rx2('beta')[0]),
                'direction': str(tf_res.rx2('side')[0])
            }
            plot_res = tf_res
        else:
            plot_res = res

        # Create plot
        def plot_func():
            if contour_levels is None:
                levels = [0.1, 0.05, 0.01]
            else:
                levels = contour_levels

            if show_contours:
                metafor.funnel_rma(
                    plot_res,
                    level=ro.FloatVector(levels),
                    shade=ro.StrVector(['white', 'gray90', 'gray70']),
                    refline=0,
                    legend=True,
                    back="white"
                )
            else:
                metafor.funnel_rma(
                    plot_res,
                    refline=0,
                    back="white"
                )

            if title:
                self.r('title')(main=title, cex_main=1.2, font_main=2)

        result['plot'] = self._save_plot_to_base64(plot_func, width, height)

        return result

    def forest_plot_meta(
        self,
        effects: np.ndarray,
        se: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        sm: str = "MD",
        method_tau: str = "REML",
        prediction: bool = True,
        layout: str = "JAMA",
        width: int = 1000,
        height: int = 600
    ) -> str:
        """
        Create forest plot using meta package (alternative style).

        The meta package offers different aesthetics and layouts
        (JAMA, RevMan, etc.) popular in medical journals.

        Args:
            effects: Effect sizes
            se: Standard errors
            study_labels: Study names
            sm: Summary measure (MD, SMD, OR, RR, etc.)
            method_tau: Method for tau² estimation
            prediction: Show prediction interval
            layout: Plot layout ("meta", "JAMA", "RevMan")
            width: Plot width
            height: Plot height

        Returns:
            Base64 encoded PNG image
        """
        n_studies = len(effects)

        if study_labels is None:
            study_labels = np.array([f"Study {i+1}" for i in range(n_studies)])

        # Create R vectors
        r_effects = ro.FloatVector(effects)
        r_se = ro.FloatVector(se)
        r_labels = ro.StrVector(study_labels)

        def plot_func():
            # Run meta-analysis with meta package
            m = meta.metagen(
                TE=r_effects,
                seTE=r_se,
                studlab=r_labels,
                sm=sm,
                method_tau=method_tau,
                prediction=prediction
            )

            # Create forest plot
            if layout == "JAMA":
                meta.forest_meta(
                    m,
                    layout="JAMA",
                    fontsize=10,
                    colgap_forest="1cm"
                )
            elif layout == "RevMan":
                meta.forest_meta(
                    m,
                    layout="RevMan5",
                    fontsize=10
                )
            else:
                meta.forest_meta(
                    m,
                    fontsize=10
                )

        return self._save_plot_to_base64(plot_func, width, height)

    def baujat_plot(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        method: str = "REML",
        label_outliers: bool = True,
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        Create Baujat plot for outlier and influential study detection.

        Baujat plots show each study's contribution to overall
        heterogeneity vs. influence on pooled effect.

        Args:
            effects: Effect sizes
            variances: Effect size variances
            study_labels: Study names
            method: Meta-analysis method
            label_outliers: Label outlying studies
            width: Plot width
            height: Plot height

        Returns:
            Base64 encoded PNG image
        """
        r_data = self._prepare_data(effects, variances, study_labels)

        def plot_func():
            res = metafor.rma(
                yi=r_data.rx2('yi'),
                vi=r_data.rx2('vi'),
                slab=r_data.rx2('study'),
                method=method
            )

            metafor.baujat_rma(
                res,
                symbol="slab" if label_outliers else "pch",
                cex=0.8,
                col="darkred"
            )

            self.r('title')(
                main="Baujat Plot",
                xlab="Contribution to Overall Heterogeneity",
                ylab="Influence on Pooled Effect"
            )

        return self._save_plot_to_base64(plot_func, width, height)

    def radial_plot(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        method: str = "REML",
        width: int = 800,
        height: int = 800
    ) -> str:
        """
        Create Radial (Galbraith) plot.

        Radial plots display studies on a standardized scale,
        useful for assessing heterogeneity visually.

        Args:
            effects: Effect sizes
            variances: Effect size variances
            study_labels: Study names
            method: Meta-analysis method
            width: Plot width
            height: Plot height

        Returns:
            Base64 encoded PNG image
        """
        r_data = self._prepare_data(effects, variances, study_labels)

        def plot_func():
            res = metafor.rma(
                yi=r_data.rx2('yi'),
                vi=r_data.rx2('vi'),
                slab=r_data.rx2('study'),
                method=method
            )

            metafor.radial_rma(
                res,
                cex=0.8,
                col="darkblue"
            )

        return self._save_plot_to_base64(plot_func, width, height)

    def gosh_plot(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        n_subsets: int = 1000,
        method: str = "REML",
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        Create GOSH (Graphical Display of Study Heterogeneity) plot.

        GOSH plots show all possible meta-analysis results from
        different combinations of studies, revealing patterns and outliers.

        Args:
            effects: Effect sizes
            variances: Effect size variances
            n_subsets: Number of subsets to sample
            method: Meta-analysis method
            width: Plot width
            height: Plot height

        Returns:
            Base64 encoded PNG image
        """
        r_data = self._prepare_data(effects, variances)

        def plot_func():
            res = metafor.rma(
                yi=r_data.rx2('yi'),
                vi=r_data.rx2('vi'),
                method=method
            )

            # Generate GOSH diagnostics
            gosh_res = metafor.gosh_rma(
                res,
                subsets=min(n_subsets, 2 ** len(effects) - 1)
            )

            # Plot GOSH diagnostics
            self.r('plot')(gosh_res)

        return self._save_plot_to_base64(plot_func, width, height)

    def labbe_plot(
        self,
        events_exp: np.ndarray,
        n_exp: np.ndarray,
        events_ctrl: np.ndarray,
        n_ctrl: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        width: int = 800,
        height: int = 800
    ) -> str:
        """
        Create L'Abbé plot for binary outcome data.

        L'Abbé plots display event rates in experimental vs. control
        groups, showing individual study results and pooled estimates.

        Args:
            events_exp: Events in experimental group
            n_exp: Sample size in experimental group
            events_ctrl: Events in control group
            n_ctrl: Sample size in control group
            study_labels: Study names
            width: Plot width
            height: Plot height

        Returns:
            Base64 encoded PNG image
        """
        n_studies = len(events_exp)

        if study_labels is None:
            study_labels = np.array([f"Study {i+1}" for i in range(n_studies)])

        # Create R vectors
        r_events_exp = ro.IntVector(events_exp)
        r_n_exp = ro.IntVector(n_exp)
        r_events_ctrl = ro.IntVector(events_ctrl)
        r_n_ctrl = ro.IntVector(n_ctrl)
        r_labels = ro.StrVector(study_labels)

        def plot_func():
            # Run meta-analysis
            m = meta.metabin(
                event_e=r_events_exp,
                n_e=r_n_exp,
                event_c=r_events_ctrl,
                n_c=r_n_ctrl,
                studlab=r_labels,
                sm="OR"
            )

            # Create L'Abbé plot
            meta.labbe_metabin(m, cex=1.2, col="darkblue")

        return self._save_plot_to_base64(plot_func, width, height)

    def cumulative_forest_plot(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        order_by: Optional[np.ndarray] = None,
        method: str = "REML",
        width: int = 1000,
        height: int = 800
    ) -> str:
        """
        Create cumulative forest plot.

        Shows pooled effect as studies are added sequentially,
        useful for assessing temporal trends or small-study effects.

        Args:
            effects: Effect sizes
            variances: Effect size variances
            study_labels: Study names
            order_by: Variable to order studies (e.g., publication year)
            method: Meta-analysis method
            width: Plot width
            height: Plot height

        Returns:
            Base64 encoded PNG image
        """
        r_data = self._prepare_data(effects, variances, study_labels)

        # Add ordering variable if provided
        if order_by is not None:
            r_order = ro.FloatVector(order_by)
        else:
            r_order = ro.IntVector(range(len(effects)))

        def plot_func():
            # Sort data by order variable
            order_idx = self.r('order')(r_order)

            res = metafor.rma(
                yi=r_data.rx2('yi'),
                vi=r_data.rx2('vi'),
                slab=r_data.rx2('study'),
                method=method
            )

            # Create cumulative forest plot
            metafor.cumul_rma(
                res,
                order=order_idx,
                transf="exp"  # If using log measures
            )

        return self._save_plot_to_base64(plot_func, width, height)

    def leave_one_out_plot(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        method: str = "REML",
        width: int = 1000,
        height: int = 800
    ) -> str:
        """
        Create leave-one-out forest plot.

        Shows pooled effect with each study removed sequentially,
        revealing influential studies.

        Args:
            effects: Effect sizes
            variances: Effect size variances
            study_labels: Study names
            method: Meta-analysis method
            width: Plot width
            height: Plot height

        Returns:
            Base64 encoded PNG image
        """
        r_data = self._prepare_data(effects, variances, study_labels)

        def plot_func():
            res = metafor.rma(
                yi=r_data.rx2('yi'),
                vi=r_data.rx2('vi'),
                slab=r_data.rx2('study'),
                method=method
            )

            # Create leave-one-out plot
            loo = metafor.leave1out_rma(res)

            # Forest plot of LOO results
            metafor.forest_default(
                loo.rx2('estimate'),
                loo.rx2('ci.lb'),
                loo.rx2('ci.ub'),
                slab=r_data.rx2('study'),
                xlab="Effect Size (with study removed)",
                refline=float(res.rx2('beta')[0])
            )

        return self._save_plot_to_base64(plot_func, width, height)


def create_forest_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    method: str = "REML",
    **kwargs
) -> str:
    """
    Convenience function to create forest plot.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Study names
        method: Meta-analysis method
        **kwargs: Additional arguments for forest_plot_metafor

    Returns:
        Base64 encoded PNG image
    """
    plotter = RMetaPlotter()
    variances = se ** 2
    return plotter.forest_plot_metafor(
        effects, variances, study_labels, method, **kwargs
    )


def create_funnel_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    method: str = "REML",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to create funnel plot.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Study names
        method: Meta-analysis method
        **kwargs: Additional arguments for funnel_plot_metafor

    Returns:
        Dict with plot and test results
    """
    plotter = RMetaPlotter()
    variances = se ** 2
    return plotter.funnel_plot_metafor(
        effects, variances, study_labels, method, **kwargs
    )


__all__ = [
    'RMetaPlotter',
    'create_forest_plot',
    'create_funnel_plot',
]
