#!/usr/bin/env python3
"""
Metapython Streamlit Demo App
============================

Interactive demo of Metapython v0.3.0 Phase 3 features.

Run with: streamlit run streamlit_demo.py

Requirements:
    pip install metapython[viz]
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

try:
    import metapython as mp
    HAS_METAPYTHON = True
except ImportError:
    HAS_METAPYTHON = False
    st.error("Metapython not installed. Run: pip install metapython")

def main():
    st.set_page_config(
        page_title="Metapython Demo",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔬 Metapython v0.3.0 - Interactive Demo")
    st.markdown("**Unified Meta-Analysis Suite with Bayesian Engines & Automated Reporting**")
    
    if not HAS_METAPYTHON:
        st.stop()
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Data input method
    input_method = st.sidebar.radio(
        "Data Input Method",
        ["Use Example Data", "Upload CSV", "Manual Entry"]
    )
    
    # Initialize data
    data = None
    
    if input_method == "Use Example Data":
        # Example datasets
        dataset_choice = st.sidebar.selectbox(
            "Choose Example Dataset",
            ["Antidepressants", "Vaccines", "Educational Interventions"]
        )
        
        if dataset_choice == "Antidepressants":
            data = pd.DataFrame({
                'study': [f'Study_{i+1}' for i in range(8)],
                'effect': [0.47, 0.23, 0.65, 0.31, 0.58, 0.19, 0.41, 0.72],
                'se': [0.12, 0.15, 0.11, 0.14, 0.13, 0.16, 0.10, 0.12],
                'n1': [120, 85, 150, 95, 110, 75, 130, 140],
                'n2': [115, 90, 145, 100, 105, 80, 125, 135]
            })
            st.sidebar.info("**Antidepressants vs Placebo**\\nEffect sizes: Standardized mean differences")
            
        elif dataset_choice == "Vaccines":
            data = pd.DataFrame({
                'study': [f'Trial_{i+1}' for i in range(6)],
                'effect': [0.82, 0.91, 0.76, 0.88, 0.79, 0.85],
                'se': [0.08, 0.09, 0.10, 0.07, 0.11, 0.08],
                'n1': [2000, 1500, 2500, 1800, 1200, 2200],
                'n2': [2000, 1500, 2500, 1800, 1200, 2200]
            })
            st.sidebar.info("**Vaccine Efficacy**\\nEffect sizes: Log risk ratios")
            
        else:  # Educational Interventions
            data = pd.DataFrame({
                'study': [f'School_{i+1}' for i in range(10)],
                'effect': [0.31, 0.45, 0.18, 0.52, 0.27, 0.39, 0.63, 0.22, 0.41, 0.35],
                'se': [0.09, 0.11, 0.13, 0.08, 0.12, 0.10, 0.07, 0.14, 0.09, 0.11],
                'n1': [250, 180, 320, 200, 275, 190, 340, 160, 230, 210],
                'n2': [240, 185, 315, 195, 280, 185, 335, 165, 225, 205]
            })
            st.sidebar.info("**Educational Interventions**\\nEffect sizes: Cohen's d")
    
    elif input_method == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="CSV should contain columns: study, effect, se"
        )
        
        if uploaded_file:
            try:
                data = pd.read_csv(uploaded_file)
                st.sidebar.success(f"Loaded {len(data)} studies")
            except Exception as e:
                st.sidebar.error(f"Error loading file: {e}")
                
    else:  # Manual Entry
        st.sidebar.markdown("**Enter Study Data**")
        n_studies = st.sidebar.number_input("Number of studies", min_value=2, max_value=20, value=4)
        
        study_data = []
        for i in range(n_studies):
            with st.sidebar.expander(f"Study {i+1}"):
                study_name = st.text_input(f"Study name", value=f"Study_{i+1}", key=f"name_{i}")
                effect = st.number_input(f"Effect size", value=0.5, step=0.01, key=f"effect_{i}")
                se = st.number_input(f"Standard error", value=0.1, min_value=0.001, step=0.01, key=f"se_{i}")
                study_data.append({'study': study_name, 'effect': effect, 'se': se})
        
        data = pd.DataFrame(study_data)
    
    if data is not None and len(data) >= 2:
        # Display data
        st.subheader("📋 Input Data")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(data, use_container_width=True)
            
        with col2:
            st.metric("Number of Studies", len(data))
            if 'effect' in data.columns:
                st.metric("Effect Range", f"{data['effect'].min():.2f} to {data['effect'].max():.2f}")
            if 'se' in data.columns:
                st.metric("SE Range", f"{data['se'].min():.3f} to {data['se'].max():.3f}")
        
        # Analysis options
        st.subheader("⚙️ Analysis Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            include_bayesian = st.checkbox("Include Bayesian Analysis", value=True, help="Requires PyMC")
            include_r_validation = st.checkbox("R Validation", value=False, help="Requires R and rpy2")
            
        with col2:
            output_format = st.selectbox("Report Format", ["HTML", "Markdown", "Both"], index=2)
            save_plots = st.checkbox("Save Plots", value=True)
            
        with col3:
            tau2_method = st.selectbox("Tau² Method", ["REML", "DL", "HS", "EB"], index=0)
            use_hksj = st.checkbox("HKSJ Adjustment", value=True, help="Hartung-Knapp-Sidik-Jonkman")
        
        # Run analysis button
        if st.button("🚀 Run Meta-Analysis", type="primary"):
            
            with st.spinner("Running comprehensive meta-analysis..."):
                try:
                    # Configure analysis
                    config = mp.UnifiedMetaConfig(
                        tau2_method=tau2_method,
                        use_hksj=use_hksj
                    )
                    
                    # Run automated report
                    result = mp.meta_auto_report(
                        data,
                        config=config,
                        output_format=output_format.lower(),
                        include_bayesian=include_bayesian
                    )
                    
                    # Display results
                    st.subheader("📊 Meta-Analysis Results")
                    
                    # Key results
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Random Effects",
                            f"{result.basic_results.random_effects.effect:.3f}",
                            help="Pooled effect size with random effects model"
                        )
                        
                    with col2:
                        ci_low = result.basic_results.random_effects.ci_low
                        ci_high = result.basic_results.random_effects.ci_high
                        st.metric(
                            "95% CI",
                            f"[{ci_low:.3f}, {ci_high:.3f}]",
                            help="95% confidence interval"
                        )
                        
                    with col3:
                        st.metric(
                            "I² Heterogeneity",
                            f"{result.basic_results.heterogeneity.I2:.1f}%",
                            help="Percentage of variability due to heterogeneity"
                        )
                        
                    with col4:
                        p_val = result.basic_results.random_effects.p_value
                        significance = "Significant" if p_val < 0.05 else "Not Significant"
                        st.metric(
                            "P-value",
                            f"{p_val:.3f}",
                            delta=significance,
                            delta_color="normal"
                        )
                    
                    # Detailed results tabs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📈 Visualization", "📝 Report", "🔍 Diagnostics", 
                        "🎯 Bayesian", "📋 Reproducibility"
                    ])
                    
                    with tab1:
                        # Create visualizations
                        meta = mp.UnifiedMetaAnalysis(data, effect_col='effect', se_col='se', label_col='study', config=config)
                        meta.analyze()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Forest Plot**")
                            try:
                                forest_fig = meta.create_interactive_forest_plot()
                                if hasattr(forest_fig, 'show'):  # Plotly figure
                                    st.plotly_chart(forest_fig, use_container_width=True)
                                else:  # Matplotlib figure
                                    st.pyplot(forest_fig)
                            except Exception as e:
                                st.error(f"Forest plot error: {e}")
                        
                        with col2:
                            st.markdown("**Funnel Plot**")
                            try:
                                funnel_fig = meta.create_funnel_plot()
                                st.pyplot(funnel_fig)
                            except Exception as e:
                                st.error(f"Funnel plot error: {e}")
                    
                    with tab2:
                        # Display reports
                        if result.report_html:
                            st.markdown("**HTML Report**")
                            st.components.v1.html(result.report_html, height=600, scrolling=True)
                            
                            # Download button
                            st.download_button(
                                "📥 Download HTML Report",
                                data=result.report_html,
                                file_name="metaanalysis_report.html",
                                mime="text/html"
                            )
                        
                        if result.report_markdown:
                            with st.expander("View Markdown Report"):
                                st.markdown(result.report_markdown)
                                
                                st.download_button(
                                    "📥 Download Markdown Report",
                                    data=result.report_markdown,
                                    file_name="metaanalysis_report.md",
                                    mime="text/markdown"
                                )
                    
                    with tab3:
                        # Diagnostics
                        if result.diagnostics:
                            st.markdown("**Publication Bias Tests**")
                            bias_data = {
                                'Test': ['Egger', 'Begg'],
                                'P-value': [
                                    result.diagnostics.bias_tests.egger_p_value,
                                    result.diagnostics.bias_tests.begg_p_value
                                ],
                                'Significant': [
                                    result.diagnostics.bias_tests.egger_significant,
                                    result.diagnostics.bias_tests.begg_significant
                                ]
                            }
                            st.dataframe(pd.DataFrame(bias_data))
                            
                            st.markdown("**Heterogeneity Assessment**")
                            het_data = {
                                'Statistic': ['Q', 'df', 'P-value', 'I²', 'H²', 'τ²'],
                                'Value': [
                                    f"{result.diagnostics.heterogeneity.Q:.2f}",
                                    result.diagnostics.heterogeneity.df,
                                    f"{result.diagnostics.heterogeneity.p_value:.3f}",
                                    f"{result.diagnostics.heterogeneity.I2:.1f}%",
                                    f"{result.diagnostics.heterogeneity.H2:.2f}",
                                    f"{result.diagnostics.heterogeneity.tau2:.3f}"
                                ]
                            }
                            st.dataframe(pd.DataFrame(het_data))
                    
                    with tab4:
                        # Bayesian results
                        if result.bayesian_results and result.bayesian_results.success:
                            st.markdown("**Bayesian Analysis Results**")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Posterior Mean", f"{result.bayesian_results.posterior_mean:.3f}")
                                st.metric("Posterior SD", f"{result.bayesian_results.posterior_sd:.3f}")
                                
                            with col2:
                                st.metric("95% CrI Lower", f"{result.bayesian_results.ci_low:.3f}")
                                st.metric("95% CrI Upper", f"{result.bayesian_results.ci_high:.3f}")
                            
                            st.metric("Between-study Heterogeneity (τ)", f"{result.bayesian_results.tau_mean:.3f}")
                            
                        else:
                            st.info("Bayesian analysis not available. Install PyMC: `pip install metapython[bayes]`")
                    
                    with tab5:
                        # Reproducibility
                        if result.metadata:
                            st.markdown("**Analysis Metadata**")
                            meta_df = pd.DataFrame([
                                ["Timestamp", result.metadata.get('timestamp', 'N/A')],
                                ["Metapython Version", result.metadata.get('version', 'N/A')],
                                ["Number of Studies", result.metadata.get('n_studies', 'N/A')],
                                ["Analysis Type", result.metadata.get('analysis_type', 'N/A')]
                            ], columns=['Attribute', 'Value'])
                            st.dataframe(meta_df)
                            
                            if include_r_validation:
                                st.markdown("**R Validation**")
                                with st.spinner("Generating R validation script..."):
                                    try:
                                        r_script = meta.generate_r_script("/tmp/validation.R")
                                        st.success("R script generated successfully!")
                                        
                                        with open("/tmp/validation.R", 'r') as f:
                                            r_content = f.read()
                                        
                                        st.download_button(
                                            "📥 Download R Validation Script",
                                            data=r_content,
                                            file_name="metaanalysis_validation.R",
                                            mime="text/plain"
                                        )
                                        
                                    except Exception as e:
                                        st.error(f"R validation failed: {e}")
                
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.exception(e)
    
    else:
        st.info("👈 Please provide data using the sidebar options to begin meta-analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🔬 **Metapython v0.3.0** - Unified Meta-Analysis Suite | "
        "📚 [Documentation](https://github.com/mahmood726-cyber/Metapython) | "
        "🐛 [Report Issues](https://github.com/mahmood726-cyber/Metapython/issues)"
    )

if __name__ == "__main__":
    main()