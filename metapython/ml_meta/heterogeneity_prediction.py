"""
ML-Based Heterogeneity Prediction

Machine learning models to predict heterogeneity in meta-analysis:
- Random forests for I² prediction
- Gradient boosting for τ² estimation
- Neural networks for complex heterogeneity patterns
- Feature importance analysis
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass

from metapython.core.config import logger

# Try to import ML libraries
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")


@dataclass
class HeterogeneityFeatures:
    """Features for heterogeneity prediction."""
    n_studies: int
    mean_sample_size: float
    sd_sample_size: float
    year_range: int
    design_diversity: float
    population_diversity: float
    intervention_diversity: float
    outcome_measure_diversity: float
    risk_of_bias_score: float
    geographic_diversity: float


class HeterogeneityPredictor:
    """
    Predict heterogeneity using machine learning.

    Features:
    - Multiple ML models (RF, GBM, MLP)
    - Automatic feature engineering
    - Cross-validated predictions
    - Feature importance analysis
    - Explainable predictions

    Example:
        >>> predictor = HeterogeneityPredictor()
        >>> predictor.train(training_data)
        >>> I2_pred = predictor.predict(new_study_features)
    """

    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize predictor.

        Args:
            model_type: 'random_forest', 'gradient_boosting', 'neural_network'
        """
        if not HAS_SKLEARN:
            raise ImportError("scikit-learn required")

        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False

        self._initialize_model()

    def _initialize_model(self):
        """Initialize ML model."""
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        elif self.model_type == 'neural_network':
            self.model = MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                alpha=0.001,
                max_iter=1000,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def extract_features(self, study_characteristics: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from study characteristics.

        Args:
            study_characteristics: Dictionary with study info

        Returns:
            Feature vector
        """
        features = []

        # Number of studies
        features.append(study_characteristics.get('n_studies', 0))

        # Sample size statistics
        sample_sizes = study_characteristics.get('sample_sizes', [])
        if sample_sizes:
            features.append(np.mean(sample_sizes))
            features.append(np.std(sample_sizes))
        else:
            features.extend([0, 0])

        # Year range
        years = study_characteristics.get('publication_years', [])
        if years:
            features.append(max(years) - min(years))
        else:
            features.append(0)

        # Design diversity (Shannon entropy)
        designs = study_characteristics.get('study_designs', [])
        features.append(self._calculate_entropy(designs))

        # Population diversity
        populations = study_characteristics.get('populations', [])
        features.append(self._calculate_entropy(populations))

        # Intervention diversity
        interventions = study_characteristics.get('interventions', [])
        features.append(self._calculate_entropy(interventions))

        # Outcome measure diversity
        outcomes = study_characteristics.get('outcome_measures', [])
        features.append(self._calculate_entropy(outcomes))

        # Risk of bias score (0-100)
        features.append(study_characteristics.get('mean_rob_score', 50))

        # Geographic diversity
        countries = study_characteristics.get('countries', [])
        features.append(len(set(countries)) if countries else 0)

        return np.array(features).reshape(1, -1)

    def _calculate_entropy(self, categories: List[str]) -> float:
        """Calculate Shannon entropy for categorical diversity."""
        if not categories:
            return 0.0

        from collections import Counter
        counts = Counter(categories)
        total = len(categories)
        probs = [c / total for c in counts.values()]

        entropy = -sum(p * np.log(p) for p in probs if p > 0)
        return entropy

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train heterogeneity prediction model.

        Args:
            X: Feature matrix (n_samples × n_features)
            y: Target I² values
            cv_folds: Cross-validation folds

        Returns:
            Training results with CV scores
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_scaled, y,
            cv=cv_folds,
            scoring='neg_mean_squared_error'
        )
        rmse_cv = np.sqrt(-cv_scores)

        # Train on full data
        self.model.fit(X_scaled, y)
        self.trained = True

        # Feature importance (if available)
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        else:
            importance = None

        logger.info(f"Model trained. CV RMSE: {rmse_cv.mean():.2f} ± {rmse_cv.std():.2f}")

        return {
            'cv_rmse_mean': float(rmse_cv.mean()),
            'cv_rmse_std': float(rmse_cv.std()),
            'feature_importance': importance.tolist() if importance is not None else None,
            'model_type': self.model_type
        }

    def predict(
        self,
        study_characteristics: Dict[str, Any],
        return_uncertainty: bool = True
    ) -> Dict[str, Any]:
        """
        Predict heterogeneity for new meta-analysis.

        Args:
            study_characteristics: Study characteristics
            return_uncertainty: Whether to estimate prediction uncertainty

        Returns:
            Predicted I² with uncertainty
        """
        if not self.trained:
            raise ValueError("Model not trained. Call train() first.")

        # Extract features
        X = self.extract_features(study_characteristics)
        X_scaled = self.scaler.transform(X)

        # Predict
        I2_pred = self.model.predict(X_scaled)[0]

        # Clip to valid range
        I2_pred = np.clip(I2_pred, 0, 100)

        result = {
            'predicted_I2': float(I2_pred),
            'interpretation': self._interpret_I2(I2_pred)
        }

        # Uncertainty estimation (for ensemble models)
        if return_uncertainty and hasattr(self.model, 'estimators_'):
            # Bootstrap estimates from ensemble
            predictions = [est.predict(X_scaled)[0] for est in self.model.estimators_]
            result['uncertainty'] = float(np.std(predictions))
            result['ci_lower'] = float(np.percentile(predictions, 2.5))
            result['ci_upper'] = float(np.percentile(predictions, 97.5))

        return result

    def _interpret_I2(self, I2: float) -> str:
        """Interpret I² value."""
        if I2 < 25:
            return "Low heterogeneity"
        elif I2 < 50:
            return "Moderate heterogeneity"
        elif I2 < 75:
            return "Substantial heterogeneity"
        else:
            return "Considerable heterogeneity"

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance rankings."""
        if not self.trained:
            return None

        if not hasattr(self.model, 'feature_importances_'):
            return None

        feature_names = [
            'n_studies', 'mean_sample_size', 'sd_sample_size',
            'year_range', 'design_diversity', 'population_diversity',
            'intervention_diversity', 'outcome_diversity',
            'rob_score', 'geographic_diversity'
        ]

        importance = self.model.feature_importances_
        return dict(zip(feature_names, importance))


def predict_heterogeneity(
    study_characteristics: Dict[str, Any],
    training_data: Optional[Tuple[np.ndarray, np.ndarray]] = None
) -> Dict[str, Any]:
    """
    Quick function to predict heterogeneity.

    Args:
        study_characteristics: Study characteristics
        training_data: Optional (X, y) training data tuple

    Returns:
        Prediction results
    """
    predictor = HeterogeneityPredictor(model_type='random_forest')

    if training_data is not None:
        X_train, y_train = training_data
        predictor.train(X_train, y_train)

    return predictor.predict(study_characteristics)


__all__ = [
    'HeterogeneityPredictor',
    'HeterogeneityFeatures',
    'predict_heterogeneity',
]
