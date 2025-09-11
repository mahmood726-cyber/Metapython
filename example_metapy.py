#!/usr/bin/env python3
"""
Example script demonstrating the metapy package functionality
============================================================

This script shows how to use the new metapy package for meta-analysis,
providing R-like APIs similar to the 'meta' and 'metafor' packages.
"""

import numpy as np
import pandas as pd
import metapy

def main():
    print("=" * 60)
    print("metapy Package Demonstration")
    print("=" * 60)
    print()
    
    # Example 1: Generic meta-analysis with metagen()
    print("1. Generic Meta-Analysis (metagen)")
    print("-" * 35)
    
    # Effect sizes and standard errors from multiple studies
    effects = [0.2, 0.4, 0.3, 0.5, 0.1, 0.35, 0.25]
    ses = [0.1, 0.15, 0.12, 0.18, 0.08, 0.14, 0.11]
    studies = [f"Study {i+1}" for i in range(len(effects))]
    
    # Run meta-analysis with DerSimonian-Laird method
    result1 = metapy.metagen(effects, ses, studlab=studies, method="DL")
    print(result1)
    print()
    print("Summary table:")
    print(result1.summary_table())
    print()
    
    # Example 2: Continuous outcomes with metacont()
    print("2. Continuous Outcomes Meta-Analysis (metacont)")
    print("-" * 45)
    
    # Data for comparing two treatments on a continuous outcome
    data_cont = {
        'study': ['RCT-A', 'RCT-B', 'RCT-C', 'RCT-D'],
        'mean_treat': [12.5, 14.2, 13.1, 15.0],
        'sd_treat': [2.3, 2.8, 2.1, 3.0],
        'n_treat': [30, 35, 28, 40],
        'mean_ctrl': [10.1, 11.8, 11.2, 12.5],
        'sd_ctrl': [2.1, 2.5, 2.0, 2.8],
        'n_ctrl': [32, 33, 30, 38]
    }
    df_cont = pd.DataFrame(data_cont)
    
    # Standardized mean difference meta-analysis
    result2 = metapy.metacont(
        m1=df_cont['mean_treat'], sd1=df_cont['sd_treat'], n1=df_cont['n_treat'],
        m2=df_cont['mean_ctrl'], sd2=df_cont['sd_ctrl'], n2=df_cont['n_ctrl'],
        studlab=df_cont['study'], sm="SMD", method="PM"
    )
    
    print("Standardized Mean Difference Analysis:")
    print(result2.random_result)
    print()
    
    # Example 3: Binary outcomes with metabin()
    print("3. Binary Outcomes Meta-Analysis (metabin)")
    print("-" * 40)
    
    # Data for comparing event rates between two groups
    data_bin = {
        'study': ['Trial-1', 'Trial-2', 'Trial-3', 'Trial-4', 'Trial-5'],
        'events_exp': [15, 22, 18, 12, 20],
        'total_exp': [100, 120, 95, 80, 110],
        'events_ctrl': [25, 35, 28, 18, 32],
        'total_ctrl': [105, 115, 98, 85, 108]
    }
    df_bin = pd.DataFrame(data_bin)
    
    # Odds ratio meta-analysis
    result3 = metapy.metabin(
        event1=df_bin['events_exp'], n1=df_bin['total_exp'],
        event2=df_bin['events_ctrl'], n2=df_bin['total_ctrl'],
        studlab=df_bin['study'], sm="OR", hakn=True  # Use Hartung-Knapp adjustment
    )
    
    print("Odds Ratio Analysis (with Hartung-Knapp adjustment):")
    print(result3.random_result)
    print(f"Back-transformed OR: {np.exp(result3.random_result.effect):.3f}")
    print(f"95% CI: [{np.exp(result3.random_result.ci_lower):.3f}, {np.exp(result3.random_result.ci_upper):.3f}]")
    print()
    
    # Example 4: Proportions meta-analysis with metaprop()
    print("4. Proportions Meta-Analysis (metaprop)")
    print("-" * 37)
    
    # Single-arm studies reporting event rates
    data_prop = {
        'study': ['Study-A', 'Study-B', 'Study-C', 'Study-D'],
        'events': [8, 12, 15, 6],
        'total': [50, 60, 75, 40]
    }
    df_prop = pd.DataFrame(data_prop)
    
    result4 = metapy.metaprop(
        event=df_prop['events'], n=df_prop['total'],
        studlab=df_prop['study'], method="DL"
    )
    
    print("Logit-transformed Proportions Analysis:")
    print(result4.random_result)
    # Back-transform to proportion scale
    from metapy.effect_sizes import inv_logit
    pooled_prop = inv_logit(result4.random_result.effect)
    print(f"Pooled proportion: {pooled_prop:.3f}")
    print()
    
    # Example 5: Using rma() function (metafor-like interface)
    print("5. RMA Function (metafor-like interface)")
    print("-" * 40)
    
    # Effect sizes with variances
    yi = [0.3, 0.5, 0.2, 0.4, 0.6, 0.1]
    vi = [0.01, 0.02, 0.008, 0.025, 0.03, 0.006]  # variances
    slab = ['A', 'B', 'C', 'D', 'E', 'F']
    
    result5 = metapy.rma(yi=yi, vi=vi, slab=slab, method="PM", knha=True)
    
    print("RMA with Paule-Mandel and Knapp-Hartung:")
    print(result5.random_result)
    print()
    
    # Example 6: Comparison of methods
    print("6. Method Comparison")
    print("-" * 20)
    
    # Same data with different tau² estimation methods
    effects = [0.3, 0.5, 0.2, 0.4, 0.6]
    ses = [0.1, 0.15, 0.09, 0.16, 0.18]
    
    result_dl = metapy.metagen(effects, ses, method="DL")
    result_pm = metapy.metagen(effects, ses, method="PM")
    
    print("DerSimonian-Laird method:")
    print(f"  Effect: {result_dl.random_result.effect:.3f}, τ² = {result_dl.random_result.tau2:.3f}")
    
    print("Paule-Mandel method:")
    print(f"  Effect: {result_pm.random_result.effect:.3f}, τ² = {result_pm.random_result.tau2:.3f}")
    print()
    
    # Example 7: Working with pandas DataFrame
    print("7. DataFrame Integration")
    print("-" * 25)
    
    # Create a dataset
    df = pd.DataFrame({
        'study_name': ['Alpha', 'Beta', 'Gamma', 'Delta'],
        'effect_size': [0.25, 0.40, 0.15, 0.35],
        'std_error': [0.08, 0.12, 0.06, 0.10]
    })
    
    # Use column names directly
    result7 = metapy.metagen(
        effect='effect_size', 
        se='std_error', 
        studlab='study_name',
        data=df,
        level=0.90  # 90% confidence intervals
    )
    
    print("Using DataFrame with 90% confidence intervals:")
    print(result7.random_result)
    print()
    
    print("=" * 60)
    print("metapy demonstration completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()