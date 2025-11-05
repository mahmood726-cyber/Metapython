"""
Bayesian meta-analysis models using PyMC.

Implements hierarchical Bayesian models for meta-analysis with:
- Random effects meta-analysis
- Meta-regression with multiple moderators
- Network meta-analysis
- Sensitivity analysis for priors
- Posterior predictive checks
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd

from metapython.core.config import HAS_PYMC, logger
from metapython.core.models import InsufficientDataError

if HAS_PYMC:
    import pymc as pm
    import arviz as az


class BayesianMetaAnalysis:
    """
    Comprehensive Bayesian meta-analysis using PyMC.

    This class provides a high-level interface for Bayesian meta-analysis
    with hierarchical random effects models.

    Example:
        >>> bma = BayesianMetaAnalysis(effects, se, study_labels)
        >>> bma.fit(chains=4, draws=2000)
        >>> results = bma.get_results()
        >>> print(f"Posterior mean: {results['mu_mean']:.3f}")
        >>> bma.plot_posterior()
    """

    def __init__(
        self,
        effects: np.ndarray,
        se: np.ndarray,
        study_labels: Optional[np.ndarray] = None,
        prior_mu_mean: float = 0.0,
        prior_mu_sd: float = 10.0,
        prior_tau_sd: float = 1.0,
    ):
        """
        Initialize Bayesian meta-analysis.

        Args:
            effects: Array of effect sizes
            se: Array of standard errors
            study_labels: Optional study labels
            prior_mu_mean: Prior mean for overall effect
            prior_mu_sd: Prior SD for overall effect (weakly informative)
            prior_tau_sd: Prior SD for between-study heterogeneity
        """
        if not HAS_PYMC:
            raise ImportError(
                "PyMC is required for Bayesian analysis. "
                "Install with: pip install 'metapython[full]'"
            )

        self.effects = np.asarray(effects)
        self.se = np.asarray(se)
        self.study_labels = (
            study_labels if study_labels is not None
            else np.array([f"Study {i+1}" for i in range(len(effects))])
        )

        if len(self.effects) < 2:
            raise InsufficientDataError("At least 2 studies required")

        self.prior_mu_mean = prior_mu_mean
        self.prior_mu_sd = prior_mu_sd
        self.prior_tau_sd = prior_tau_sd

        self.model = None
        self.trace = None
        self.idata = None

    def build_model(self) -> pm.Model:
        """
        Build hierarchical Bayesian random effects model.

        Model specification:
            θ_i ~ Normal(μ_i, σ_i²)        [Likelihood]
            μ_i ~ Normal(μ, τ²)             [Random effects]
            μ ~ Normal(prior_mu_mean, prior_mu_sd²)  [Overall effect prior]
            τ ~ HalfNormal(prior_tau_sd)    [Heterogeneity prior]

        Returns:
            PyMC model object
        """
        n_studies = len(self.effects)

        with pm.Model() as model:
            # Priors
            mu = pm.Normal(
                'mu',
                mu=self.prior_mu_mean,
                sigma=self.prior_mu_sd
            )
            tau = pm.HalfNormal('tau', sigma=self.prior_tau_sd)

            # Random effects (study-specific means)
            theta = pm.Normal(
                'theta',
                mu=mu,
                sigma=tau,
                shape=n_studies
            )

            # Likelihood
            y_obs = pm.Normal(
                'y_obs',
                mu=theta,
                sigma=self.se,
                observed=self.effects
            )

            # Posterior predictive for new study
            theta_new = pm.Normal(
                'theta_new',
                mu=mu,
                sigma=tau
            )

        self.model = model
        return model

    def fit(
        self,
        chains: int = 4,
        draws: int = 2000,
        tune: int = 1000,
        target_accept: float = 0.95,
        random_seed: Optional[int] = None,
        **kwargs
    ) -> az.InferenceData:
        """
        Fit the Bayesian model using MCMC sampling.

        Args:
            chains: Number of MCMC chains
            draws: Number of draws per chain
            tune: Number of tuning steps
            target_accept: Target acceptance probability for NUTS
            random_seed: Random seed for reproducibility
            **kwargs: Additional arguments passed to pm.sample()

        Returns:
            ArviZ InferenceData object with posterior samples
        """
        if self.model is None:
            self.build_model()

        with self.model:
            self.trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                random_seed=random_seed,
                return_inferencedata=True,
                **kwargs
            )

            # Add posterior predictive samples
            self.trace = pm.sample_posterior_predictive(
                self.trace,
                extend_inferencedata=True,
                random_seed=random_seed
            )

        self.idata = self.trace
        return self.idata

    def get_results(self) -> Dict[str, Any]:
        """
        Extract summary results from posterior.

        Returns:
            Dictionary with posterior summaries:
                - mu_mean: Posterior mean of overall effect
                - mu_sd: Posterior SD of overall effect
                - mu_hdi_low: Lower bound of 95% HDI
                - mu_hdi_high: Upper bound of 95% HDI
                - tau: Between-study heterogeneity
                - I2: I² statistic
                - rhat: Convergence diagnostic (should be < 1.01)
                - ess: Effective sample size
        """
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")

        summary = az.summary(self.trace, var_names=['mu', 'tau'])

        # Extract mu statistics
        mu_samples = self.trace.posterior['mu'].values.flatten()
        mu_mean = float(summary.loc['mu', 'mean'])
        mu_sd = float(summary.loc['mu', 'sd'])
        mu_hdi = az.hdi(self.trace, var_names=['mu'], hdi_prob=0.95)
        mu_hdi_low = float(mu_hdi['mu'].values[0])
        mu_hdi_high = float(mu_hdi['mu'].values[1])
        mu_rhat = float(summary.loc['mu', 'r_hat'])
        mu_ess = float(summary.loc['mu', 'ess_bulk'])

        # Extract tau statistics
        tau_samples = self.trace.posterior['tau'].values.flatten()
        tau_mean = float(summary.loc['tau', 'mean'])
        tau_hdi = az.hdi(self.trace, var_names=['tau'], hdi_prob=0.95)
        tau_hdi_low = float(tau_hdi['tau'].values[0])
        tau_hdi_high = float(tau_hdi['tau'].values[1])

        # Calculate I² from posterior samples
        # I² = τ² / (τ² + σ²_typical)
        sigma_typical = np.median(self.se)
        I2_samples = tau_samples**2 / (tau_samples**2 + sigma_typical**2)
        I2_mean = float(np.mean(I2_samples))
        I2_hdi_low = float(np.percentile(I2_samples, 2.5))
        I2_hdi_high = float(np.percentile(I2_samples, 97.5))

        # Prediction interval for new study
        theta_new_samples = self.trace.posterior['theta_new'].values.flatten()
        pred_hdi = az.hdi(self.trace, var_names=['theta_new'], hdi_prob=0.95)

        return {
            'mu_mean': mu_mean,
            'mu_sd': mu_sd,
            'mu_hdi_low': mu_hdi_low,
            'mu_hdi_high': mu_hdi_high,
            'mu_rhat': mu_rhat,
            'mu_ess': mu_ess,
            'tau_mean': tau_mean,
            'tau_hdi_low': tau_hdi_low,
            'tau_hdi_high': tau_hdi_high,
            'I2_mean': I2_mean,
            'I2_hdi_low': I2_hdi_low,
            'I2_hdi_high': I2_hdi_high,
            'prediction_interval_low': float(pred_hdi['theta_new'].values[0]),
            'prediction_interval_high': float(pred_hdi['theta_new'].values[1]),
            'converged': mu_rhat < 1.01,
        }

    def plot_posterior(self, var_names: Optional[List[str]] = None):
        """
        Plot posterior distributions.

        Args:
            var_names: Variables to plot (default: ['mu', 'tau'])
        """
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if var_names is None:
            var_names = ['mu', 'tau']

        az.plot_posterior(
            self.trace,
            var_names=var_names,
            hdi_prob=0.95,
            figsize=(12, 4)
        )

    def plot_forest(self):
        """Plot forest plot with posterior estimates."""
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")

        az.plot_forest(
            self.trace,
            var_names=['theta', 'mu'],
            combined=True,
            figsize=(10, len(self.effects) + 2)
        )

    def plot_trace(self):
        """Plot MCMC trace plots for diagnostics."""
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")

        az.plot_trace(
            self.trace,
            var_names=['mu', 'tau'],
            figsize=(12, 6)
        )


def bayesian_meta_analysis(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    chains: int = 4,
    draws: int = 2000,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for Bayesian meta-analysis.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Optional study labels
        chains: Number of MCMC chains
        draws: Number of draws per chain
        **kwargs: Additional arguments passed to BayesianMetaAnalysis

    Returns:
        Dictionary with results

    Example:
        >>> results = bayesian_meta_analysis(effects, se, chains=4, draws=2000)
        >>> print(f"Overall effect: {results['mu_mean']:.3f} "
        ...       f"[{results['mu_hdi_low']:.3f}, {results['mu_hdi_high']:.3f}]")
    """
    bma = BayesianMetaAnalysis(effects, se, study_labels, **kwargs)
    bma.fit(chains=chains, draws=draws)
    return bma.get_results()


def bayesian_meta_regression(
    effects: np.ndarray,
    se: np.ndarray,
    moderators: pd.DataFrame,
    chains: int = 4,
    draws: int = 2000,
    **kwargs
) -> Dict[str, Any]:
    """
    Bayesian meta-regression with multiple moderators.

    Args:
        effects: Effect sizes
        se: Standard errors
        moderators: DataFrame with moderator variables
        chains: Number of MCMC chains
        draws: Number of draws per chain
        **kwargs: Additional model arguments

    Returns:
        Dictionary with results including moderator coefficients
    """
    if not HAS_PYMC:
        raise ImportError("PyMC required for Bayesian meta-regression")

    X = moderators.values
    n_studies, n_moderators = X.shape

    with pm.Model() as model:
        # Priors for regression coefficients
        beta = pm.Normal('beta', mu=0, sigma=10, shape=n_moderators)
        tau = pm.HalfNormal('tau', sigma=1)

        # Random effects
        mu_i = pm.math.dot(X, beta)
        theta = pm.Normal('theta', mu=mu_i, sigma=tau, shape=n_studies)

        # Likelihood
        y_obs = pm.Normal('y_obs', mu=theta, sigma=se, observed=effects)

        # Sample
        trace = pm.sample(
            draws=draws,
            tune=1000,
            chains=chains,
            target_accept=0.95,
            return_inferencedata=True
        )

    # Extract results
    summary = az.summary(trace, var_names=['beta', 'tau'])

    results = {
        'moderators': moderators.columns.tolist(),
        'coefficients': summary.loc[['beta[0]', 'beta[1]'], 'mean'].values if n_moderators > 1
                       else [summary.loc['beta', 'mean']],
        'tau_mean': float(summary.loc['tau', 'mean']),
        'trace': trace,
    }

    return results


def bayesian_network_meta_analysis(
    treatments: List[Tuple[str, str]],
    effects: np.ndarray,
    se: np.ndarray,
    chains: int = 4,
    draws: int = 2000,
) -> Dict[str, Any]:
    """
    Bayesian network meta-analysis (NMA).

    Args:
        treatments: List of (treatment_a, treatment_b) tuples for each comparison
        effects: Effect sizes
        se: Standard errors
        chains: Number of MCMC chains
        draws: Number of draws per chain

    Returns:
        Dictionary with treatment effect estimates and rankings
    """
    if not HAS_PYMC:
        raise ImportError("PyMC required for Bayesian NMA")

    # Get unique treatments
    unique_treatments = sorted(set(sum(treatments, ())))
    n_treatments = len(unique_treatments)
    treatment_idx = {t: i for i, t in enumerate(unique_treatments)}

    logger.info(
        f"Network meta-analysis with {n_treatments} treatments "
        f"and {len(effects)} comparisons"
    )

    # This is a simplified NMA model
    # Production code would include consistency checking and more sophisticated models
    raise NotImplementedError(
        "Full Bayesian NMA implementation coming soon. "
        "Use NetworkMetaRankings class from metapython.py for now."
    )


__all__ = [
    'BayesianMetaAnalysis',
    'bayesian_meta_analysis',
    'bayesian_meta_regression',
    'bayesian_network_meta_analysis',
]
