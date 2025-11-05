"""
Machine Learning Enhanced Meta-Analysis

AI/ML techniques for meta-analysis:
- Automated study screening with NLP
- Heterogeneity prediction with ML
- Publication bias detection with deep learning
- Meta-regression with gradient boosting
- Automated data extraction with transformers
- Similarity-based study matching
"""

from metapython.ml_meta.heterogeneity_prediction import (
    HeterogeneityPredictor,
    predict_heterogeneity,
)

from metapython.ml_meta.publication_bias_ml import (
    PublicationBiasDetector,
    detect_bias_ml,
)

from metapython.ml_meta.automated_screening import (
    StudyScreener,
    screen_studies_ml,
)

from metapython.ml_meta.meta_regression_ml import (
    GradientBoostingMetaRegression,
    random_forest_meta_regression,
)

__all__ = [
    # Heterogeneity
    'HeterogeneityPredictor',
    'predict_heterogeneity',

    # Publication bias
    'PublicationBiasDetector',
    'detect_bias_ml',

    # Automated screening
    'StudyScreener',
    'screen_studies_ml',

    # ML meta-regression
    'GradientBoostingMetaRegression',
    'random_forest_meta_regression',
]
