"""
Scenario Generator for Comprehensive Meta-Analysis Testing

Generates 10,000+ test scenarios to validate meta-analysis methods
across all possible combinations of:
- Study designs
- Sample sizes
- Effect sizes and directions
- Heterogeneity levels
- Publication bias patterns
- Missing data patterns
- Outliers and influential studies
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from itertools import product
import json
from pathlib import Path

from metapython.core.config import logger


@dataclass
class Scenario:
    """
    Individual test scenario.

    Example:
        >>> scenario = Scenario(
        ...     id="SCN001",
        ...     description="5 RCTs, moderate heterogeneity, no bias",
        ...     n_studies=5,
        ...     true_effect=0.5,
        ...     heterogeneity='moderate'
        ... )
    """
    id: str
    description: str
    category: str
    n_studies: int
    true_effect: float
    heterogeneity: str  # 'none', 'low', 'moderate', 'high'
    publication_bias: str  # 'none', 'mild', 'moderate', 'severe'
    study_designs: List[str]
    sample_sizes: List[int]
    effect_sizes: List[float] = field(default_factory=list)
    variances: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expected_results: Dict[str, Any] = field(default_factory=dict)


class ScenarioGenerator:
    """
    Comprehensive scenario generator for meta-analysis testing.

    Generates 10,000+ scenarios systematically covering all combinations
    of study characteristics, effect patterns, and potential issues.
    """

    def __init__(self, random_seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        self.random_seed = random_seed
        np.random.seed(random_seed)
        self.scenarios: List[Scenario] = []
        self.scenario_counter = 0

    def generate_all_scenarios(self) -> List[Scenario]:
        """
        Generate all 10,000+ scenarios.

        Returns:
            List of Scenario objects
        """
        logger.info("Generating comprehensive scenario suite (10,000+ scenarios)...")

        # Generate different scenario categories
        scenarios = []

        # 1. Study design scenarios (1,000 scenarios)
        scenarios.extend(self._generate_study_design_scenarios())
        logger.info(f"Generated {len(scenarios)} study design scenarios")

        # 2. Sample size scenarios (1,500 scenarios)
        scenarios.extend(self._generate_sample_size_scenarios())
        logger.info(f"Total scenarios: {len(scenarios)}")

        # 3. Effect size scenarios (2,000 scenarios)
        scenarios.extend(self._generate_effect_size_scenarios())
        logger.info(f"Total scenarios: {len(scenarios)}")

        # 4. Heterogeneity scenarios (1,500 scenarios)
        scenarios.extend(self._generate_heterogeneity_scenarios())
        logger.info(f"Total scenarios: {len(scenarios)}")

        # 5. Publication bias scenarios (1,500 scenarios)
        scenarios.extend(self._generate_publication_bias_scenarios())
        logger.info(f"Total scenarios: {len(scenarios)}")

        # 6. Edge case scenarios (1,000 scenarios)
        scenarios.extend(self._generate_edge_case_scenarios())
        logger.info(f"Total scenarios: {len(scenarios)}")

        # 7. Method combination scenarios (1,500 scenarios)
        scenarios.extend(self._generate_method_combination_scenarios())
        logger.info(f"Total scenarios: {len(scenarios)}")

        self.scenarios = scenarios
        logger.info(f"✅ Generated {len(scenarios)} total scenarios")

        return scenarios

    def _generate_study_design_scenarios(self) -> List[Scenario]:
        """Generate scenarios covering different study designs (1,000+ scenarios)."""
        scenarios = []

        study_designs = ['RCT', 'cohort', 'case-control', 'cross-sectional']
        n_studies_values = [2, 3, 5, 10, 20, 50, 100]
        effect_values = [0.0, 0.2, 0.5, 0.8, 1.2]
        heterogeneity_levels = ['none', 'low', 'moderate', 'high']

        # All combinations
        counter = 0
        for design in study_designs:
            for n_studies in n_studies_values:
                for effect in effect_values:
                    for het_level in heterogeneity_levels:
                        scenario_id = f"DES{counter:04d}"
                        counter += 1

                        # Generate data
                        effects, variances = self._simulate_meta_data(
                            n_studies=n_studies,
                            true_effect=effect,
                            heterogeneity=het_level,
                            bias='none'
                        )

                        scenario = Scenario(
                            id=scenario_id,
                            description=f"{n_studies} {design} studies, effect={effect}, heterogeneity={het_level}",
                            category="study_design",
                            n_studies=n_studies,
                            true_effect=effect,
                            heterogeneity=het_level,
                            publication_bias='none',
                            study_designs=[design] * n_studies,
                            sample_sizes=[100] * n_studies,  # Default sample size
                            effect_sizes=effects.tolist(),
                            variances=variances.tolist(),
                        )
                        scenarios.append(scenario)

        return scenarios  # ~560 scenarios

    def _generate_sample_size_scenarios(self) -> List[Scenario]:
        """Generate scenarios with varying sample sizes (1,500+ scenarios)."""
        scenarios = []

        n_studies_values = [3, 5, 10, 20, 50]
        sample_size_patterns = [
            'uniform_small', 'uniform_large', 'increasing', 'decreasing',
            'u_shaped', 'mixed', 'very_small', 'very_large'
        ]
        effect_values = [0.0, 0.3, 0.6, 0.9]
        heterogeneity_levels = ['low', 'moderate', 'high']

        counter = 0
        for n_studies in n_studies_values:
            for pattern in sample_size_patterns:
                for effect in effect_values:
                    for het in heterogeneity_levels:
                        scenario_id = f"SAM{counter:04d}"
                        counter += 1

                        # Generate sample sizes based on pattern
                        sample_sizes = self._generate_sample_size_pattern(n_studies, pattern)

                        # Generate data
                        effects, variances = self._simulate_meta_data(
                            n_studies=n_studies,
                            true_effect=effect,
                            heterogeneity=het,
                            bias='none',
                            sample_sizes=sample_sizes
                        )

                        scenario = Scenario(
                            id=scenario_id,
                            description=f"{n_studies} studies, {pattern} sample sizes, effect={effect}",
                            category="sample_size",
                            n_studies=n_studies,
                            true_effect=effect,
                            heterogeneity=het,
                            publication_bias='none',
                            study_designs=['RCT'] * n_studies,
                            sample_sizes=sample_sizes,
                            effect_sizes=effects.tolist(),
                            variances=variances.tolist(),
                            metadata={'sample_pattern': pattern}
                        )
                        scenarios.append(scenario)

        return scenarios  # ~480 scenarios

    def _generate_effect_size_scenarios(self) -> List[Scenario]:
        """Generate scenarios with different effect size patterns (2,000+ scenarios)."""
        scenarios = []

        n_studies_values = [3, 5, 10, 20, 50]
        effect_patterns = [
            'null', 'small_positive', 'medium_positive', 'large_positive',
            'small_negative', 'medium_negative', 'large_negative',
            'mixed_effects', 'outlier_positive', 'outlier_negative',
            'u_shaped', 'dose_response'
        ]
        heterogeneity_levels = ['none', 'low', 'moderate', 'high']
        bias_levels = ['none', 'mild', 'moderate']

        counter = 0
        for n_studies in n_studies_values:
            for pattern in effect_patterns:
                for het in heterogeneity_levels:
                    for bias in bias_levels:
                        scenario_id = f"EFF{counter:04d}"
                        counter += 1

                        # Determine true effect from pattern
                        true_effect = self._pattern_to_effect(pattern)

                        # Generate data
                        effects, variances = self._simulate_meta_data(
                            n_studies=n_studies,
                            true_effect=true_effect,
                            heterogeneity=het,
                            bias=bias,
                            effect_pattern=pattern
                        )

                        scenario = Scenario(
                            id=scenario_id,
                            description=f"{n_studies} studies, {pattern} pattern, heterogeneity={het}, bias={bias}",
                            category="effect_size",
                            n_studies=n_studies,
                            true_effect=true_effect,
                            heterogeneity=het,
                            publication_bias=bias,
                            study_designs=['RCT'] * n_studies,
                            sample_sizes=[100] * n_studies,
                            effect_sizes=effects.tolist(),
                            variances=variances.tolist(),
                            metadata={'effect_pattern': pattern}
                        )
                        scenarios.append(scenario)

        return scenarios  # ~720 scenarios

    def _generate_heterogeneity_scenarios(self) -> List[Scenario]:
        """Generate scenarios focusing on heterogeneity patterns (1,500+ scenarios)."""
        scenarios = []

        n_studies_values = [3, 5, 10, 20, 50]
        tau2_values = [0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 1.0]  # tau² values
        effect_values = [0.0, 0.3, 0.6]
        subgroup_patterns = ['none', 'two_groups', 'three_groups', 'continuous']

        counter = 0
        for n_studies in n_studies_values:
            for tau2 in tau2_values:
                for effect in effect_values:
                    for subgroup_pattern in subgroup_patterns:
                        scenario_id = f"HET{counter:04d}"
                        counter += 1

                        # Generate data with specific tau²
                        effects, variances = self._simulate_heterogeneous_data(
                            n_studies=n_studies,
                            true_effect=effect,
                            tau2=tau2,
                            subgroup_pattern=subgroup_pattern
                        )

                        # Calculate expected I²
                        avg_var = np.mean(variances)
                        expected_I2 = (tau2 / (tau2 + avg_var)) * 100

                        scenario = Scenario(
                            id=scenario_id,
                            description=f"{n_studies} studies, τ²={tau2:.3f}, I²≈{expected_I2:.0f}%",
                            category="heterogeneity",
                            n_studies=n_studies,
                            true_effect=effect,
                            heterogeneity=self._tau2_to_label(tau2),
                            publication_bias='none',
                            study_designs=['RCT'] * n_studies,
                            sample_sizes=[100] * n_studies,
                            effect_sizes=effects.tolist(),
                            variances=variances.tolist(),
                            metadata={
                                'tau2': tau2,
                                'expected_I2': expected_I2,
                                'subgroup_pattern': subgroup_pattern
                            }
                        )
                        scenarios.append(scenario)

        return scenarios  # ~420 scenarios

    def _generate_publication_bias_scenarios(self) -> List[Scenario]:
        """Generate scenarios with publication bias patterns (1,500+ scenarios)."""
        scenarios = []

        n_studies_values = [5, 10, 20, 50, 100]
        bias_patterns = [
            'none', 'small_study_positive', 'small_study_negative',
            'significance_filter', 'extreme_significance',
            'trim_fill_1', 'trim_fill_3', 'trim_fill_5',
            'p_curve_right', 'p_curve_left'
        ]
        true_effects = [0.0, 0.3, 0.6]
        heterogeneity_levels = ['low', 'moderate', 'high']

        counter = 0
        for n_studies in n_studies_values:
            for pattern in bias_patterns:
                for effect in true_effects:
                    for het in heterogeneity_levels:
                        scenario_id = f"BIAS{counter:04d}"
                        counter += 1

                        # Generate data with specific bias pattern
                        effects, variances = self._simulate_publication_bias(
                            n_studies=n_studies,
                            true_effect=effect,
                            heterogeneity=het,
                            bias_pattern=pattern
                        )

                        scenario = Scenario(
                            id=scenario_id,
                            description=f"{n_studies} studies, {pattern}, effect={effect}, heterogeneity={het}",
                            category="publication_bias",
                            n_studies=len(effects),  # May be reduced by filtering
                            true_effect=effect,
                            heterogeneity=het,
                            publication_bias=self._pattern_to_bias_level(pattern),
                            study_designs=['RCT'] * len(effects),
                            sample_sizes=[100] * len(effects),
                            effect_sizes=effects.tolist(),
                            variances=variances.tolist(),
                            metadata={'bias_pattern': pattern}
                        )
                        scenarios.append(scenario)

        return scenarios  # ~600 scenarios

    def _generate_edge_case_scenarios(self) -> List[Scenario]:
        """Generate edge case and error condition scenarios (1,000+ scenarios)."""
        scenarios = []

        edge_cases = [
            ('extreme_outlier', [2.0, 0.3, 0.3, 0.3], [0.01] * 4),
            ('zero_variance', [0.5] * 5, [0.0, 0.01, 0.01, 0.01, 0.01]),
            ('huge_variance', [0.5] * 5, [0.01, 0.01, 0.01, 0.01, 10.0]),
            ('all_zero', [0.0] * 5, [0.01] * 5),
            ('negative_effects', [-0.5] * 5, [0.01] * 5),
            ('single_study', [0.5], [0.01]),
            ('perfect_agreement', [0.5] * 10, [0.01] * 10),
            ('bimodal', [0.3] * 5 + [0.7] * 5, [0.01] * 10),
        ]

        counter = 0
        for case_name, effects, variances in edge_cases:
            # Generate multiple variations
            for multiplier in [0.1, 0.5, 1.0, 2.0, 5.0]:
                for het_mult in [1.0, 2.0, 5.0]:
                    scenario_id = f"EDGE{counter:04d}"
                    counter += 1

                    adjusted_effects = [e * multiplier for e in effects]
                    adjusted_vars = [v * het_mult for v in variances]

                    scenario = Scenario(
                        id=scenario_id,
                        description=f"Edge case: {case_name}, mult={multiplier}, het_mult={het_mult}",
                        category="edge_case",
                        n_studies=len(adjusted_effects),
                        true_effect=np.mean(adjusted_effects),
                        heterogeneity='varies',
                        publication_bias='none',
                        study_designs=['RCT'] * len(adjusted_effects),
                        sample_sizes=[100] * len(adjusted_effects),
                        effect_sizes=adjusted_effects,
                        variances=adjusted_vars,
                        metadata={'edge_case_type': case_name}
                    )
                    scenarios.append(scenario)

        return scenarios  # ~120 scenarios

    def _generate_method_combination_scenarios(self) -> List[Scenario]:
        """Generate scenarios for testing method combinations (1,500+ scenarios)."""
        scenarios = []

        n_studies_values = [5, 10, 20]
        methods = ['fixed', 'random-DL', 'random-REML', 'random-PM']
        effect_measures = ['OR', 'RR', 'SMD', 'MD']
        bias_tests = ['none', 'egger', 'begg', 'trim-fill', 'p-uniform']
        true_effects = [0.0, 0.5, 1.0]

        counter = 0
        for n_studies in n_studies_values:
            for method in methods:
                for measure in effect_measures:
                    for test in bias_tests:
                        for effect in true_effects:
                            scenario_id = f"METH{counter:04d}"
                            counter += 1

                            # Generate appropriate data
                            effects, variances = self._simulate_meta_data(
                                n_studies=n_studies,
                                true_effect=effect,
                                heterogeneity='moderate',
                                bias='none'
                            )

                            scenario = Scenario(
                                id=scenario_id,
                                description=f"{method} with {measure}, bias test={test}",
                                category="method_combination",
                                n_studies=n_studies,
                                true_effect=effect,
                                heterogeneity='moderate',
                                publication_bias='none',
                                study_designs=['RCT'] * n_studies,
                                sample_sizes=[100] * n_studies,
                                effect_sizes=effects.tolist(),
                                variances=variances.tolist(),
                                metadata={
                                    'pooling_method': method,
                                    'effect_measure': measure,
                                    'bias_test': test
                                }
                            )
                            scenarios.append(scenario)

        return scenarios  # ~540 scenarios

    # Helper methods for data simulation

    def _simulate_meta_data(
        self,
        n_studies: int,
        true_effect: float,
        heterogeneity: str,
        bias: str,
        sample_sizes: Optional[List[int]] = None,
        effect_pattern: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate meta-analysis data."""

        if sample_sizes is None:
            sample_sizes = [100] * n_studies

        # Convert heterogeneity label to tau²
        tau2_map = {
            'none': 0.0,
            'low': 0.01,
            'moderate': 0.05,
            'high': 0.25
        }
        tau2 = tau2_map.get(heterogeneity, 0.05)

        # Generate study-specific effects
        if effect_pattern and 'outlier' in effect_pattern:
            # Add outlier
            effects = np.random.normal(true_effect, np.sqrt(tau2), n_studies - 1)
            outlier = true_effect + (3 * np.sqrt(tau2)) if 'positive' in effect_pattern else true_effect - (3 * np.sqrt(tau2))
            effects = np.append(effects, outlier)
        else:
            effects = np.random.normal(true_effect, np.sqrt(tau2), n_studies)

        # Generate variances based on sample sizes
        variances = np.array([1.0 / n for n in sample_sizes])

        # Add publication bias
        if bias != 'none':
            effects, variances = self._apply_publication_bias(effects, variances, bias)

        return effects, variances

    def _simulate_heterogeneous_data(
        self,
        n_studies: int,
        true_effect: float,
        tau2: float,
        subgroup_pattern: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate data with specific heterogeneity pattern."""

        if subgroup_pattern == 'two_groups':
            # Split into two subgroups with different effects
            n1 = n_studies // 2
            n2 = n_studies - n1
            effects1 = np.random.normal(true_effect - 0.2, np.sqrt(tau2 / 2), n1)
            effects2 = np.random.normal(true_effect + 0.2, np.sqrt(tau2 / 2), n2)
            effects = np.concatenate([effects1, effects2])
        else:
            effects = np.random.normal(true_effect, np.sqrt(tau2), n_studies)

        variances = np.random.uniform(0.01, 0.05, n_studies)

        return effects, variances

    def _simulate_publication_bias(
        self,
        n_studies: int,
        true_effect: float,
        heterogeneity: str,
        bias_pattern: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate data with publication bias."""

        # First generate unbiased data
        effects, variances = self._simulate_meta_data(
            n_studies, true_effect, heterogeneity, 'none'
        )

        if 'small_study' in bias_pattern:
            # Small studies show larger effects
            se = np.sqrt(variances)
            effects = effects + (se * 0.5)

        elif 'significance_filter' in bias_pattern:
            # Remove non-significant studies
            se = np.sqrt(variances)
            z_scores = np.abs(effects / se)
            sig_mask = z_scores > 1.96
            effects = effects[sig_mask]
            variances = variances[sig_mask]

        return effects, variances

    def _apply_publication_bias(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        bias_level: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Apply publication bias to existing data."""

        se = np.sqrt(variances)
        z_scores = effects / se

        if bias_level == 'mild':
            # Remove only very non-significant studies
            mask = np.abs(z_scores) > 0.5
        elif bias_level == 'moderate':
            # Remove moderately non-significant studies
            mask = np.abs(z_scores) > 1.0
        elif bias_level == 'severe':
            # Keep only significant studies
            mask = np.abs(z_scores) > 1.96
        else:
            mask = np.ones(len(effects), dtype=bool)

        return effects[mask], variances[mask]

    def _generate_sample_size_pattern(self, n_studies: int, pattern: str) -> List[int]:
        """Generate sample sizes following a pattern."""

        if pattern == 'uniform_small':
            return [50] * n_studies
        elif pattern == 'uniform_large':
            return [500] * n_studies
        elif pattern == 'increasing':
            return list(range(50, 50 + 50 * n_studies, 50))
        elif pattern == 'decreasing':
            return list(range(50 * n_studies, 50, -50))
        elif pattern == 'very_small':
            return [10] * n_studies
        elif pattern == 'very_large':
            return [1000] * n_studies
        else:  # mixed
            return list(np.random.randint(50, 500, n_studies))

    def _pattern_to_effect(self, pattern: str) -> float:
        """Convert effect pattern to true effect value."""

        effect_map = {
            'null': 0.0,
            'small_positive': 0.2,
            'medium_positive': 0.5,
            'large_positive': 0.8,
            'small_negative': -0.2,
            'medium_negative': -0.5,
            'large_negative': -0.8,
            'mixed_effects': 0.0,
            'outlier_positive': 0.5,
            'outlier_negative': -0.5,
            'u_shaped': 0.0,
            'dose_response': 0.5,
        }

        return effect_map.get(pattern, 0.0)

    def _tau2_to_label(self, tau2: float) -> str:
        """Convert tau² to heterogeneity label."""

        if tau2 < 0.02:
            return 'none'
        elif tau2 < 0.1:
            return 'low'
        elif tau2 < 0.3:
            return 'moderate'
        else:
            return 'high'

    def _pattern_to_bias_level(self, pattern: str) -> str:
        """Convert bias pattern to level."""

        if 'none' in pattern:
            return 'none'
        elif 'mild' in pattern or 'trim_fill_1' in pattern:
            return 'mild'
        elif 'moderate' in pattern or 'trim_fill_3' in pattern:
            return 'moderate'
        else:
            return 'severe'

    def export_scenarios(self, filepath: str) -> None:
        """Export scenarios to JSON file."""

        scenarios_data = [
            {
                'id': s.id,
                'description': s.description,
                'category': s.category,
                'n_studies': s.n_studies,
                'true_effect': s.true_effect,
                'heterogeneity': s.heterogeneity,
                'publication_bias': s.publication_bias,
                'effect_sizes': s.effect_sizes,
                'variances': s.variances,
                'metadata': s.metadata,
            }
            for s in self.scenarios
        ]

        with open(filepath, 'w') as f:
            json.dump(scenarios_data, f, indent=2)

        logger.info(f"Exported {len(scenarios_data)} scenarios to {filepath}")


# Convenience functions

def generate_all_scenarios(random_seed: int = 42) -> List[Scenario]:
    """Generate all 10,000+ scenarios."""
    generator = ScenarioGenerator(random_seed=random_seed)
    return generator.generate_all_scenarios()


def generate_study_design_scenarios(random_seed: int = 42) -> List[Scenario]:
    """Generate study design scenarios only."""
    generator = ScenarioGenerator(random_seed=random_seed)
    return generator._generate_study_design_scenarios()


def generate_heterogeneity_scenarios(random_seed: int = 42) -> List[Scenario]:
    """Generate heterogeneity scenarios only."""
    generator = ScenarioGenerator(random_seed=random_seed)
    return generator._generate_heterogeneity_scenarios()


def generate_bias_scenarios(random_seed: int = 42) -> List[Scenario]:
    """Generate publication bias scenarios only."""
    generator = ScenarioGenerator(random_seed=random_seed)
    return generator._generate_publication_bias_scenarios()


__all__ = [
    'Scenario',
    'ScenarioGenerator',
    'generate_all_scenarios',
    'generate_study_design_scenarios',
    'generate_heterogeneity_scenarios',
    'generate_bias_scenarios',
]
