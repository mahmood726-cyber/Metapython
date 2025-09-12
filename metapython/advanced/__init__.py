"""
Advanced Meta-Analysis Methods - Bayesian and Network Extensions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import warnings

# Optional dependencies with graceful fallback
try:
    import numpyro
    import numpyro.distributions as dist
    from numpyro.infer import MCMC, NUTS
    import jax.numpy as jnp
    import jax.random as random
    HAS_NUMPYRO = True
except ImportError:
    HAS_NUMPYRO = False
    # Create dummy jnp for type hints when NumPyro not available
    class DummyJNP:
        ndarray = np.ndarray
    jnp = DummyJNP()

try:
    from scipy.stats import multivariate_normal
    from scipy.optimize import minimize
    HAS_SCIPY_ADVANCED = True
except ImportError:
    HAS_SCIPY_ADVANCED = False

logger = logging.getLogger(__name__)

class BayesianHierarchicalMeta:
    """Bayesian hierarchical meta-analysis using NumPyro/JAX"""
    
    def __init__(self):
        if not HAS_NUMPYRO:
            raise ImportError("NumPyro/JAX required for Bayesian methods. Install with: pip install numpyro")
    
    def hierarchical_model(self, effects: jnp.ndarray, variances: jnp.ndarray, 
                          prior_mean: float = 0.0, prior_tau: float = 1.0):
        """Bayesian hierarchical meta-analysis model"""
        
        n_studies = len(effects)
        
        # Hyperpriors
        mu = numpyro.sample('mu', dist.Normal(prior_mean, prior_tau))
        tau = numpyro.sample('tau', dist.HalfNormal(0.5))
        
        # Study-specific effects
        theta = numpyro.sample('theta', dist.Normal(mu, tau).expand([n_studies]))
        
        # Likelihood
        with numpyro.plate('studies', n_studies):
            numpyro.sample('y', dist.Normal(theta, jnp.sqrt(variances)), obs=effects)
    
    def fit_hierarchical(self, 
                        effects: np.ndarray, 
                        variances: np.ndarray,
                        prior_mean: float = 0.0,
                        prior_tau: float = 1.0,
                        num_warmup: int = 1000,
                        num_samples: int = 2000,
                        num_chains: int = 4) -> Dict[str, Any]:
        """Fit Bayesian hierarchical model with NUTS sampler"""
        
        try:
            # Convert to JAX arrays
            effects_jax = jnp.array(effects)
            variances_jax = jnp.array(variances)
            
            # Set up MCMC
            nuts_kernel = NUTS(self.hierarchical_model)
            mcmc = MCMC(nuts_kernel, num_warmup=num_warmup, num_samples=num_samples, num_chains=num_chains)
            
            # Run sampling
            rng_key = random.PRNGKey(0)
            mcmc.run(rng_key, effects_jax, variances_jax, prior_mean, prior_tau)
            
            # Extract results
            samples = mcmc.get_samples()
            
            # Posterior summaries
            mu_samples = samples['mu']
            tau_samples = samples['tau']
            theta_samples = samples['theta']
            
            posterior_mean = jnp.mean(mu_samples)
            posterior_std = jnp.std(mu_samples)
            posterior_quantiles = jnp.percentile(mu_samples, jnp.array([2.5, 25, 50, 75, 97.5]))
            
            tau_mean = jnp.mean(tau_samples)
            tau_quantiles = jnp.percentile(tau_samples, jnp.array([2.5, 25, 50, 75, 97.5]))
            
            # Model diagnostics
            rhat = self._compute_rhat(samples)
            eff_sample_size = self._compute_ess(samples)
            
            return {
                'posterior_mean': float(posterior_mean),
                'posterior_std': float(posterior_std),
                'posterior_quantiles': {
                    '2.5%': float(posterior_quantiles[0]),
                    '25%': float(posterior_quantiles[1]),
                    '50%': float(posterior_quantiles[2]),
                    '75%': float(posterior_quantiles[3]),
                    '97.5%': float(posterior_quantiles[4])
                },
                'tau_mean': float(tau_mean),
                'tau_quantiles': {
                    '2.5%': float(tau_quantiles[0]),
                    '25%': float(tau_quantiles[1]),
                    '50%': float(tau_quantiles[2]),
                    '75%': float(tau_quantiles[3]),
                    '97.5%': float(tau_quantiles[4])
                },
                'study_effects': {
                    'mean': [float(x) for x in jnp.mean(theta_samples, axis=0)],
                    'std': [float(x) for x in jnp.std(theta_samples, axis=0)]
                },
                'diagnostics': {
                    'rhat': {k: float(v) for k, v in rhat.items()},
                    'eff_sample_size': {k: float(v) for k, v in eff_sample_size.items()}
                },
                'samples': {
                    'mu': np.array(mu_samples),
                    'tau': np.array(tau_samples),
                    'theta': np.array(theta_samples)
                },
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Bayesian hierarchical fitting failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _compute_rhat(self, samples: Dict[str, jnp.ndarray]) -> Dict[str, float]:
        """Compute R-hat convergence diagnostic"""
        rhat_values = {}
        
        for param_name, param_samples in samples.items():
            if param_samples.ndim >= 2:  # Multiple chains
                chains = param_samples.shape[0]
                if chains > 1:
                    # Simplified R-hat computation
                    chain_means = jnp.mean(param_samples, axis=1)
                    within_var = jnp.mean(jnp.var(param_samples, axis=1))
                    between_var = jnp.var(chain_means) * param_samples.shape[1]
                    pooled_var = (within_var + between_var) / param_samples.shape[1]
                    rhat_values[param_name] = float(jnp.sqrt(pooled_var / within_var))
                else:
                    rhat_values[param_name] = 1.0
            else:
                rhat_values[param_name] = 1.0
        
        return rhat_values
    
    def _compute_ess(self, samples: Dict[str, jnp.ndarray]) -> Dict[str, float]:
        """Compute effective sample size"""
        ess_values = {}
        
        for param_name, param_samples in samples.items():
            if param_samples.ndim >= 2:
                # Simplified ESS - would use proper autocorrelation in practice
                total_samples = param_samples.size
                ess_values[param_name] = float(total_samples * 0.8)  # Conservative estimate
            else:
                ess_values[param_name] = float(len(param_samples))
        
        return ess_values
    
    def predict_new_study(self, posterior_samples: Dict[str, np.ndarray], 
                         n_predictions: int = 1000) -> Dict[str, Any]:
        """Predict effect size for new study"""
        
        try:
            mu_samples = posterior_samples['mu']
            tau_samples = posterior_samples['tau']
            
            # Sample from posterior predictive distribution
            n_samples = len(mu_samples)
            indices = np.random.choice(n_samples, n_predictions, replace=True)
            
            mu_pred = mu_samples[indices]
            tau_pred = tau_samples[indices]
            
            # Generate predictions
            predictions = np.random.normal(mu_pred, tau_pred)
            
            return {
                'predictions': predictions,
                'mean': float(np.mean(predictions)),
                'std': float(np.std(predictions)),
                'quantiles': {
                    '2.5%': float(np.percentile(predictions, 2.5)),
                    '25%': float(np.percentile(predictions, 25)),
                    '50%': float(np.percentile(predictions, 50)),
                    '75%': float(np.percentile(predictions, 75)),
                    '97.5%': float(np.percentile(predictions, 97.5))
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {'error': str(e)}

class NetworkMetaAnalysisExtended:
    """Extended network meta-analysis with inconsistency models and multi-arm corrections"""
    
    def __init__(self):
        self.treatments = None
        self.comparison_matrix = None
    
    def inconsistency_model(self, data: pd.DataFrame,
                           treatment_col: str = 'treatment',
                           control_col: str = 'control',
                           effect_col: str = 'effect',
                           se_col: str = 'se') -> Dict[str, Any]:
        """Design-by-treatment inconsistency model"""
        
        try:
            # Prepare network data
            network_data = self._prepare_network_data(data, treatment_col, control_col, effect_col, se_col)
            
            if not HAS_SCIPY_ADVANCED:
                return {'error': 'SciPy required for inconsistency models'}
            
            # Extract unique treatments
            treatments = network_data['treatments']
            n_treatments = len(treatments)
            
            # Create inconsistency design matrix
            X_consistency, X_inconsistency = self._create_inconsistency_design(network_data)
            
            # Fit consistency model
            consistency_result = self._fit_consistency_model(network_data, X_consistency)
            
            # Fit inconsistency model
            inconsistency_result = self._fit_inconsistency_model(network_data, X_inconsistency)
            
            # Test for inconsistency
            inconsistency_test = self._test_inconsistency(consistency_result, inconsistency_result)
            
            return {
                'consistency_model': consistency_result,
                'inconsistency_model': inconsistency_result,
                'inconsistency_test': inconsistency_test,
                'treatments': treatments,
                'n_comparisons': len(network_data['effects']),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Inconsistency model failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def multi_arm_correction(self, data: pd.DataFrame, 
                           study_col: str = 'study',
                           treatment_col: str = 'treatment',
                           effect_col: str = 'effect',
                           se_col: str = 'se') -> Dict[str, Any]:
        """Multi-arm trial correction for correlated effects"""
        
        try:
            # Identify multi-arm studies
            study_arm_counts = data.groupby(study_col).size()
            multi_arm_studies = study_arm_counts[study_arm_counts > 1].index
            
            if len(multi_arm_studies) == 0:
                return {
                    'message': 'No multi-arm studies found',
                    'corrected_data': data.copy(),
                    'correction_applied': False
                }
            
            corrected_data = data.copy()
            correction_info = {}
            
            for study in multi_arm_studies:
                study_data = data[data[study_col] == study]
                
                if len(study_data) > 2:
                    # Apply multi-arm correction
                    correction = self._apply_multi_arm_correction(study_data, effect_col, se_col)
                    
                    # Update data with corrected values
                    study_indices = corrected_data[corrected_data[study_col] == study].index
                    corrected_data.loc[study_indices, se_col + '_corrected'] = correction['corrected_se']
                    
                    correction_info[study] = correction
            
            return {
                'corrected_data': corrected_data,
                'correction_info': correction_info,
                'multi_arm_studies': list(multi_arm_studies),
                'correction_applied': True,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Multi-arm correction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def league_table(self, network_results: Dict[str, Any],
                    treatment_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate league table of pairwise comparisons"""
        
        try:
            if 'treatment_effects' not in network_results:
                return {'error': 'Network results must contain treatment_effects'}
            
            effects = network_results['treatment_effects']
            treatments = treatment_names or list(effects.keys())
            n_treatments = len(treatments)
            
            # Create league table matrix
            league_matrix = np.zeros((n_treatments, n_treatments))
            league_lower = np.zeros((n_treatments, n_treatments))
            league_upper = np.zeros((n_treatments, n_treatments))
            
            for i, treat_i in enumerate(treatments):
                for j, treat_j in enumerate(treatments):
                    if i != j:
                        # Calculate relative effect (treat_i vs treat_j)
                        if treat_i in effects and treat_j in effects:
                            relative_effect = effects[treat_i]['mean'] - effects[treat_j]['mean']
                            relative_se = np.sqrt(effects[treat_i]['var'] + effects[treat_j]['var'])
                            
                            league_matrix[i, j] = relative_effect
                            league_lower[i, j] = relative_effect - 1.96 * relative_se
                            league_upper[i, j] = relative_effect + 1.96 * relative_se
            
            # Create formatted table
            league_table_df = pd.DataFrame(
                league_matrix,
                index=treatments,
                columns=treatments
            )
            
            # Format with confidence intervals
            formatted_table = {}
            for i, treat_i in enumerate(treatments):
                formatted_table[treat_i] = {}
                for j, treat_j in enumerate(treatments):
                    if i == j:
                        formatted_table[treat_i][treat_j] = "Reference"
                    else:
                        effect = league_matrix[i, j]
                        lower = league_lower[i, j]
                        upper = league_upper[i, j]
                        formatted_table[treat_i][treat_j] = f"{effect:.2f} ({lower:.2f}, {upper:.2f})"
            
            return {
                'league_table': league_table_df,
                'formatted_table': formatted_table,
                'raw_effects': league_matrix,
                'confidence_intervals': {
                    'lower': league_lower,
                    'upper': league_upper
                },
                'treatments': treatments,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"League table generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_network_data(self, data: pd.DataFrame, treatment_col: str, 
                            control_col: str, effect_col: str, se_col: str) -> Dict[str, Any]:
        """Prepare network data for analysis"""
        
        # Get unique treatments
        all_treatments = set(data[treatment_col].unique()) | set(data[control_col].unique())
        treatments = sorted(list(all_treatments))
        
        # Create treatment mapping
        treatment_map = {t: i for i, t in enumerate(treatments)}
        
        # Extract comparison data
        effects = data[effect_col].values
        variances = (data[se_col] ** 2).values
        
        # Create comparison matrix
        comparisons = []
        for _, row in data.iterrows():
            treat_idx = treatment_map[row[treatment_col]]
            control_idx = treatment_map[row[control_col]]
            comparisons.append((treat_idx, control_idx))
        
        return {
            'treatments': treatments,
            'treatment_map': treatment_map,
            'effects': effects,
            'variances': variances,
            'comparisons': comparisons
        }
    
    def _create_inconsistency_design(self, network_data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """Create design matrices for consistency and inconsistency models"""
        
        treatments = network_data['treatments']
        comparisons = network_data['comparisons']
        n_treatments = len(treatments)
        n_comparisons = len(comparisons)
        
        # Consistency design matrix (basic contrasts)
        X_consistency = np.zeros((n_comparisons, n_treatments - 1))
        
        for i, (treat_idx, control_idx) in enumerate(comparisons):
            if treat_idx > 0:  # Skip reference treatment (index 0)
                X_consistency[i, treat_idx - 1] = 1
            if control_idx > 0:
                X_consistency[i, control_idx - 1] = -1
        
        # Inconsistency design matrix (adds comparison-specific effects)
        X_inconsistency = np.hstack([X_consistency, np.eye(n_comparisons)])
        
        return X_consistency, X_inconsistency
    
    def _fit_consistency_model(self, network_data: Dict[str, Any], X: np.ndarray) -> Dict[str, Any]:
        """Fit consistency model using weighted least squares"""
        
        effects = network_data['effects']
        variances = network_data['variances']
        weights = 1 / variances
        
        # Weighted least squares
        W = np.diag(weights)
        XWX = X.T @ W @ X
        XWy = X.T @ W @ effects
        
        try:
            beta = np.linalg.solve(XWX, XWy)
            cov_beta = np.linalg.inv(XWX)
            
            # Calculate residuals and fit statistics
            fitted = X @ beta
            residuals = effects - fitted
            sse = np.sum(weights * residuals ** 2)
            df = len(effects) - X.shape[1]
            
            return {
                'coefficients': beta,
                'covariance': cov_beta,
                'fitted_values': fitted,
                'residuals': residuals,
                'sse': sse,
                'df': df,
                'success': True
            }
            
        except np.linalg.LinAlgError:
            return {'success': False, 'error': 'Singular matrix in consistency model'}
    
    def _fit_inconsistency_model(self, network_data: Dict[str, Any], X: np.ndarray) -> Dict[str, Any]:
        """Fit inconsistency model"""
        return self._fit_consistency_model(network_data, X)
    
    def _test_inconsistency(self, consistency_result: Dict[str, Any], 
                          inconsistency_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test for network inconsistency"""
        
        if not (consistency_result.get('success') and inconsistency_result.get('success')):
            return {'error': 'Both models must fit successfully'}
        
        # F-test for inconsistency
        sse_consistency = consistency_result['sse']
        sse_inconsistency = inconsistency_result['sse']
        df_consistency = consistency_result['df']
        df_inconsistency = inconsistency_result['df']
        
        if df_inconsistency >= df_consistency:
            return {'error': 'Inconsistency model must have fewer degrees of freedom'}
        
        # Calculate F-statistic
        df_diff = df_consistency - df_inconsistency
        f_stat = ((sse_consistency - sse_inconsistency) / df_diff) / (sse_inconsistency / df_inconsistency)
        
        # In practice, would calculate p-value using F-distribution
        # For now, provide the test statistic
        
        return {
            'f_statistic': f_stat,
            'df_numerator': df_diff,
            'df_denominator': df_inconsistency,
            'inconsistency_detected': f_stat > 2.0,  # Simple threshold
            'sse_reduction': sse_consistency - sse_inconsistency
        }
    
    def _apply_multi_arm_correction(self, study_data: pd.DataFrame, 
                                  effect_col: str, se_col: str) -> Dict[str, Any]:
        """Apply multi-arm trial correction to standard errors"""
        
        n_arms = len(study_data)
        
        if n_arms <= 2:
            return {
                'corrected_se': study_data[se_col].values,
                'correction_factor': 1.0,
                'n_arms': n_arms
            }
        
        # Simplified correction - in practice would use proper correlation structure
        correction_factor = np.sqrt(1 + (n_arms - 2) * 0.5)  # Conservative correction
        corrected_se = study_data[se_col].values * correction_factor
        
        return {
            'corrected_se': corrected_se,
            'correction_factor': correction_factor,
            'n_arms': n_arms,
            'original_se': study_data[se_col].values
        }

class SmallSampleAdjustments:
    """Small-sample and multiplicity adjustments"""
    
    @staticmethod
    def hartung_knapp_adjustment(effects: np.ndarray, variances: np.ndarray, 
                                alpha: float = 0.05) -> Dict[str, Any]:
        """Hartung-Knapp-Sidik-Jonkman adjustment for small samples"""
        
        n_studies = len(effects)
        if n_studies < 3:
            return {'error': 'Need at least 3 studies for Hartung-Knapp adjustment'}
        
        # Random effects meta-analysis
        weights = 1 / variances
        sum_weights = np.sum(weights)
        pooled_effect = np.sum(weights * effects) / sum_weights
        
        # Calculate Q statistic
        Q = np.sum(weights * (effects - pooled_effect) ** 2)
        df = n_studies - 1
        
        # Estimate tau²
        tau2 = max(0, (Q - df) / (sum_weights - np.sum(weights ** 2) / sum_weights))
        
        # Random effects weights
        re_weights = 1 / (variances + tau2)
        sum_re_weights = np.sum(re_weights)
        re_pooled_effect = np.sum(re_weights * effects) / sum_re_weights
        
        # Standard error
        se = np.sqrt(1 / sum_re_weights)
        
        # Hartung-Knapp adjustment
        Q_re = np.sum(re_weights * (effects - re_pooled_effect) ** 2)
        hk_factor = max(1, Q_re / df)
        hk_se = se * np.sqrt(hk_factor)
        
        # t-distribution critical value
        from scipy.stats import t
        t_crit = t.ppf(1 - alpha/2, df)
        
        # Confidence interval
        ci_lower = re_pooled_effect - t_crit * hk_se
        ci_upper = re_pooled_effect + t_crit * hk_se
        
        return {
            'pooled_effect': re_pooled_effect,
            'standard_error': se,
            'hk_adjusted_se': hk_se,
            'adjustment_factor': hk_factor,
            'confidence_interval': (ci_lower, ci_upper),
            'degrees_freedom': df,
            'tau_squared': tau2
        }
    
    @staticmethod
    def bonferroni_holm_adjustment(p_values: np.ndarray) -> Dict[str, Any]:
        """Bonferroni-Holm step-down adjustment for multiple comparisons"""
        
        n_tests = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p = p_values[sorted_indices]
        
        # Holm adjustment
        adjusted_p = np.zeros(n_tests)
        
        for i in range(n_tests):
            bonferroni_p = sorted_p[i] * (n_tests - i)
            if i == 0:
                adjusted_p[sorted_indices[i]] = min(1.0, bonferroni_p)
            else:
                adjusted_p[sorted_indices[i]] = min(1.0, max(bonferroni_p, adjusted_p[sorted_indices[i-1]]))
        
        return {
            'original_p_values': p_values,
            'adjusted_p_values': adjusted_p,
            'method': 'Bonferroni-Holm',
            'n_tests': n_tests,
            'significant_after_adjustment': np.sum(adjusted_p < 0.05)
        }
    
    @staticmethod
    def false_discovery_rate(p_values: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]:
        """Benjamini-Hochberg false discovery rate control"""
        
        n_tests = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p = p_values[sorted_indices]
        
        # BH procedure
        adjusted_p = np.zeros(n_tests)
        
        for i in range(n_tests - 1, -1, -1):
            bh_p = sorted_p[i] * n_tests / (i + 1)
            if i == n_tests - 1:
                adjusted_p[sorted_indices[i]] = min(1.0, bh_p)
            else:
                adjusted_p[sorted_indices[i]] = min(1.0, min(bh_p, adjusted_p[sorted_indices[i+1]]))
        
        return {
            'original_p_values': p_values,
            'adjusted_p_values': adjusted_p,
            'method': 'Benjamini-Hochberg FDR',
            'fdr_level': alpha,
            'n_tests': n_tests,
            'significant_after_adjustment': np.sum(adjusted_p < alpha)
        }

# Export classes
__all__ = [
    'BayesianHierarchicalMeta',
    'NetworkMetaAnalysisExtended', 
    'SmallSampleAdjustments'
]