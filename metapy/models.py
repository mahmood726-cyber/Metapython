from __future__ import annotations
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass
class MetaResult:
    """Core meta-analysis result class"""
    # Point estimate and uncertainty
    effect: float = 0.0
    se: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    
    # Test statistics
    z_statistic: float = 0.0
    p_value: float = 1.0
    
    # Heterogeneity
    tau2: float = 0.0
    Q: float = 0.0
    df: int = 0
    Q_pval: float = 1.0
    I2: float = 0.0
    H2: float = 1.0
    
    # Model details
    method: str = "DL"
    model: str = "random"
    k: int = 0
    
    # Optional components
    prediction_interval: Optional[tuple] = None
    
    def __str__(self) -> str:
        lines = []
        lines.append(f"Meta-Analysis Results ({self.model} effects, {self.method})")
        lines.append(f"Studies: {self.k}")
        lines.append(f"Effect: {self.effect:.3f} [{self.ci_lower:.3f}, {self.ci_upper:.3f}]")
        lines.append(f"SE: {self.se:.3f}, Z: {self.z_statistic:.2f}, p = {self.p_value:.3f}")
        lines.append(f"Heterogeneity: Q = {self.Q:.2f} (df = {self.df}, p = {self.Q_pval:.3f})")
        lines.append(f"I² = {self.I2:.1f}%, τ² = {self.tau2:.3f}")
        
        if self.prediction_interval:
            pi_low, pi_high = self.prediction_interval
            lines.append(f"Prediction interval: [{pi_low:.3f}, {pi_high:.3f}]")
        
        return "\n".join(lines)
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if effect is statistically significant"""
        return self.p_value < alpha
    
    def has_heterogeneity(self, alpha: float = 0.10) -> bool:
        """Check if significant heterogeneity is present"""
        return self.Q_pval < alpha
    
    def summary_dict(self) -> Dict[str, Any]:
        """Return summary as dictionary"""
        return {
            'effect': self.effect,
            'se': self.se,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
            'z_statistic': self.z_statistic,
            'p_value': self.p_value,
            'tau2': self.tau2,
            'Q': self.Q,
            'df': self.df,
            'Q_pval': self.Q_pval,
            'I2': self.I2,
            'H2': self.H2,
            'method': self.method,
            'model': self.model,
            'k': self.k,
            'significant': self.is_significant(),
            'heterogeneous': self.has_heterogeneity()
        }


@dataclass 
class MetaAnalysis:
    """Container for meta-analysis data and results"""
    # Data
    studies: pd.DataFrame = field(default_factory=pd.DataFrame)
    effect_col: str = "effect"
    se_col: str = "se"
    study_col: str = "study"
    
    # Results
    fixed_result: Optional[MetaResult] = None
    random_result: Optional[MetaResult] = None
    
    # Settings
    alpha: float = 0.05
    
    def __post_init__(self):
        """Validate data after initialization"""
        if not self.studies.empty:
            required_cols = [self.effect_col, self.se_col, self.study_col]
            missing = [col for col in required_cols if col not in self.studies.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            
            # Validate data
            if (self.studies[self.se_col] <= 0).any():
                raise ValueError("Standard errors must be positive")
            
            if self.studies[self.effect_col].isna().any():
                raise ValueError("Effect sizes cannot be missing")
    
    @property
    def k(self) -> int:
        """Number of studies"""
        return len(self.studies)
    
    @property 
    def effects(self) -> np.ndarray:
        """Effect sizes as numpy array"""
        return self.studies[self.effect_col].values
    
    @property
    def variances(self) -> np.ndarray:
        """Variances as numpy array"""
        return (self.studies[self.se_col] ** 2).values
    
    @property
    def weights_fixed(self) -> np.ndarray:
        """Fixed-effects weights"""
        return 1.0 / self.variances
    
    def weights_random(self, tau2: float) -> np.ndarray:
        """Random-effects weights given tau²"""
        return 1.0 / (self.variances + tau2)
    
    def __str__(self) -> str:
        lines = []
        lines.append(f"MetaAnalysis with {self.k} studies")
        
        if self.fixed_result:
            lines.append("\nFixed-effects:")
            lines.append(f"  Effect: {self.fixed_result.effect:.3f} [{self.fixed_result.ci_lower:.3f}, {self.fixed_result.ci_upper:.3f}]")
        
        if self.random_result:
            lines.append("\nRandom-effects:")
            lines.append(f"  Effect: {self.random_result.effect:.3f} [{self.random_result.ci_lower:.3f}, {self.random_result.ci_upper:.3f}]")
            lines.append(f"  τ² = {self.random_result.tau2:.3f}, I² = {self.random_result.I2:.1f}%")
        
        return "\n".join(lines)
    
    def summary_table(self) -> pd.DataFrame:
        """Create summary table of results"""
        rows = []
        
        if self.fixed_result:
            rows.append({
                'Model': 'Fixed',
                'Effect': f"{self.fixed_result.effect:.3f}",
                'SE': f"{self.fixed_result.se:.3f}",
                '95% CI': f"[{self.fixed_result.ci_lower:.3f}, {self.fixed_result.ci_upper:.3f}]",
                'Z': f"{self.fixed_result.z_statistic:.2f}",
                'p-value': f"{self.fixed_result.p_value:.3f}",
                'τ²': '0.000'
            })
        
        if self.random_result:
            rows.append({
                'Model': 'Random',
                'Effect': f"{self.random_result.effect:.3f}",
                'SE': f"{self.random_result.se:.3f}",
                '95% CI': f"[{self.random_result.ci_lower:.3f}, {self.random_result.ci_upper:.3f}]",
                'Z': f"{self.random_result.z_statistic:.2f}",
                'p-value': f"{self.random_result.p_value:.3f}",
                'τ²': f"{self.random_result.tau2:.3f}"
            })
        
        return pd.DataFrame(rows)