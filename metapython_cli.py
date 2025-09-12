#!/usr/bin/env python3
"""
MetaPython CLI - Command Line Interface for Meta-Analysis Platform
Phase 8: Enhanced CLI with observability and enterprise features
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
import datetime

# Structured logging setup
try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False

# Rich console output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
    from rich.logging import RichHandler
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# CLI framework
try:
    import typer
    from typer import Option, Argument
    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False

# Import main metapython functionality
try:
    from metapython import (
        UnifiedMetaAnalysis, UnifiedMetaConfig, MetaCLI,
        quick_meta, meta_from_summary_stats, run_unified_demo,
        __version__, __description__
    )
except ImportError:
    # Fallback for development
    import sys
    sys.path.insert(0, '.')
    try:
        from metapython import (
            UnifiedMetaAnalysis, UnifiedMetaConfig, MetaCLI,
            quick_meta, meta_from_summary_stats, run_unified_demo,
            __version__, __description__
        )
    except ImportError as e:
        print(f"Error importing metapython: {e}")
        sys.exit(1)

# Configure structured logging
def setup_logging(level: str = "INFO", structured: bool = True) -> logging.Logger:
    """Setup structured logging with optional rich output"""
    
    if HAS_STRUCTLOG and structured:
        # Configure structlog for JSON output
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        logger = structlog.get_logger("metapython.cli")
    else:
        # Fallback to standard logging
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger("metapython.cli")
    
    return logger

# Initialize console for rich output
console = Console() if HAS_RICH else None
logger = setup_logging()

def print_info(message: str) -> None:
    """Print info message with rich formatting if available"""
    if console:
        console.print(f"[blue]ℹ[/blue] {message}")
    else:
        print(f"INFO: {message}")

def print_success(message: str) -> None:
    """Print success message with rich formatting if available"""
    if console:
        console.print(f"[green]✓[/green] {message}")
    else:
        print(f"SUCCESS: {message}")

def print_error(message: str) -> None:
    """Print error message with rich formatting if available"""
    if console:
        console.print(f"[red]✗[/red] {message}")
    else:
        print(f"ERROR: {message}")

def print_warning(message: str) -> None:
    """Print warning message with rich formatting if available"""
    if console:
        console.print(f"[yellow]⚠[/yellow] {message}")
    else:
        print(f"WARNING: {message}")

# CLI Commands using argparse (fallback if typer not available)

def cmd_analyze(args) -> None:
    """Run meta-analysis from data file"""
    logger.info("Starting meta-analysis", file=args.input, output=args.output)
    
    try:
        import pandas as pd
        
        # Load data
        if args.input.endswith('.csv'):
            data = pd.read_csv(args.input)
        elif args.input.endswith('.xlsx'):
            data = pd.read_excel(args.input)
        else:
            raise ValueError(f"Unsupported file format: {args.input}")
        
        print_info(f"Loaded {len(data)} studies from {args.input}")
        
        # Configure analysis
        config = UnifiedMetaConfig(
            tau2_method=args.tau2_method,
            use_hksj=args.use_hksj,
            alpha=args.alpha
        )
        
        # Run analysis
        meta = UnifiedMetaAnalysis(
            data=data,
            effect_col=args.effect_col,
            se_col=args.se_col,
            label_col=args.label_col,
            subgroup_col=args.subgroup_col,
            config=config
        ).analyze(
            include_bias_tests=args.include_bias,
            include_prediction_interval=args.prediction_interval,
            include_conflicts=args.conflict_detection
        )
        
        # Display results
        if console:
            table = Table(title="Meta-Analysis Results")
            table.add_column("Model", style="cyan")
            table.add_column("Effect", justify="right")
            table.add_column("95% CI", justify="right") 
            table.add_column("P-value", justify="right")
            
            fe = meta.results.fixed_effects
            re = meta.results.random_effects
            
            table.add_row(
                "Fixed Effects",
                f"{fe.effect:.3f}",
                f"[{fe.ci_low:.3f}, {fe.ci_high:.3f}]",
                f"{fe.p_value:.3f}"
            )
            table.add_row(
                "Random Effects", 
                f"{re.effect:.3f}",
                f"[{re.ci_low:.3f}, {re.ci_high:.3f}]",
                f"{re.p_value:.3f}"
            )
            
            console.print(table)
        else:
            print("\nMeta-Analysis Results:")
            print(f"Fixed Effects: {meta.results.fixed_effects.effect:.3f} [{meta.results.fixed_effects.ci_low:.3f}, {meta.results.fixed_effects.ci_high:.3f}] p={meta.results.fixed_effects.p_value:.3f}")
            print(f"Random Effects: {meta.results.random_effects.effect:.3f} [{meta.results.random_effects.ci_low:.3f}, {meta.results.random_effects.ci_high:.3f}] p={meta.results.random_effects.p_value:.3f}")
        
        # Save outputs
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save results
            summary = meta.summary_table()
            summary.to_csv(output_dir / "results.csv", index=False)
            
            # Save report
            if args.report:
                report = meta.comprehensive_report()
                with open(output_dir / "report.txt", 'w') as f:
                    f.write(report)
            
            # Save plots
            if args.plots:
                try:
                    import matplotlib.pyplot as plt
                    forest_plot = meta.create_forest_plot()
                    forest_plot.savefig(output_dir / "forest_plot.png", dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    funnel_plot = meta.create_funnel_plot()
                    funnel_plot.savefig(output_dir / "funnel_plot.png", dpi=300, bbox_inches='tight')
                    plt.close()
                except Exception as e:
                    print_warning(f"Plot generation failed: {e}")
            
            print_success(f"Results saved to {output_dir}")
        
        logger.info("Meta-analysis completed successfully")
        
    except Exception as e:
        logger.error("Meta-analysis failed", error=str(e))
        print_error(f"Analysis failed: {e}")
        sys.exit(1)

def cmd_pipeline(args) -> None:
    """Run meta-analysis pipeline from YAML config"""
    logger.info("Starting pipeline", config=args.config)
    
    try:
        cli = MetaCLI()
        result = cli.run_pipeline(args.config)
        
        if result['success']:
            print_success(f"Pipeline completed successfully")
            if 'provenance' in result:
                prov = result['provenance']
                print_info(f"Steps completed: {prov['steps_completed']}/{prov['total_steps']}")
        else:
            print_error(f"Pipeline failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error("Pipeline execution failed", error=str(e))
        print_error(f"Pipeline failed: {e}")
        sys.exit(1)

def cmd_demo(args) -> None:
    """Run comprehensive demo"""
    logger.info("Starting demo", n_studies=args.n_studies, seed=args.seed)
    
    try:
        demo_meta = run_unified_demo(
            n_studies=args.n_studies,
            seed=args.seed,
            output_dir=args.output or "demo_output",
            save_visuals=args.save_plots,
            save_text_report=args.save_report
        )
        print_success("Demo completed successfully!")
        
    except Exception as e:
        logger.error("Demo failed", error=str(e))
        print_error(f"Demo failed: {e}")
        sys.exit(1)

def cmd_version(args) -> None:
    """Show version information"""
    version_info = {
        "version": __version__,
        "description": __description__,
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    if args.json:
        print(json.dumps(version_info, indent=2))
    else:
        if console:
            table = Table(title="MetaPython Version Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="yellow")
            
            for key, value in version_info.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
        else:
            print(f"MetaPython {__version__}")
            print(f"Description: {__description__}")

def cmd_health(args) -> None:
    """Health check for dependencies and system status"""
    logger.info("Running health check")
    
    # Check core dependencies
    deps_status = {}
    core_deps = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy']
    
    for dep in core_deps:
        try:
            __import__(dep)
            deps_status[dep] = "✓"
        except ImportError:
            deps_status[dep] = "✗"
    
    # Check optional dependencies
    optional_deps = {
        'statsmodels': 'Advanced statistics',
        'sklearn': 'Machine learning',
        'numba': 'Performance optimization',
        'pymc': 'Bayesian methods',
        'cvxpy': 'Optimization',
        'biopython': 'PubMed integration',
        'streamlit': 'Web dashboard',
        'fastapi': 'API service'
    }
    
    for dep, desc in optional_deps.items():
        try:
            __import__(dep.replace('sklearn', 'sklearn.cluster'))
            deps_status[f"{dep} ({desc})"] = "✓"
        except ImportError:
            deps_status[f"{dep} ({desc})"] = "✗"
    
    # Display status
    if console:
        table = Table(title="MetaPython Health Check")
        table.add_column("Component", style="cyan")
        table.add_column("Status", justify="center")
        
        for dep, status in deps_status.items():
            color = "green" if status == "✓" else "red"
            table.add_row(dep, f"[{color}]{status}[/{color}]")
        
        console.print(table)
    else:
        print("MetaPython Health Check:")
        for dep, status in deps_status.items():
            print(f"  {dep}: {status}")
    
    # Overall status
    core_ok = all(deps_status[dep] == "✓" for dep in core_deps)
    if core_ok:
        print_success("Core functionality available")
    else:
        print_error("Missing core dependencies")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    
    if HAS_TYPER:
        # Use typer if available (preferred)
        app = typer.Typer(
            name="metapython",
            help="MetaPython - Comprehensive Meta-Analysis Platform",
            no_args_is_help=True
        )
        
        # Add commands here if using typer
        # For now, fall back to argparse for compatibility
        pass
    
    # Argparse implementation (fallback)
    parser = argparse.ArgumentParser(
        prog="metapython",
        description="MetaPython - Comprehensive Meta-Analysis Platform"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version", 
        version=f"MetaPython {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run meta-analysis")
    analyze_parser.add_argument("input", help="Input data file (CSV/Excel)")
    analyze_parser.add_argument("--output", "-o", help="Output directory")
    analyze_parser.add_argument("--effect-col", default="effect", help="Effect size column")
    analyze_parser.add_argument("--se-col", default="se", help="Standard error column")
    analyze_parser.add_argument("--label-col", default="study", help="Study label column")
    analyze_parser.add_argument("--subgroup-col", help="Subgroup column")
    analyze_parser.add_argument("--tau2-method", default="REML", choices=["DL", "REML", "HS", "EB"])
    analyze_parser.add_argument("--use-hksj", action="store_true", help="Use Hartung-Knapp adjustment")
    analyze_parser.add_argument("--alpha", type=float, default=0.05, help="Significance level")
    analyze_parser.add_argument("--include-bias", action="store_true", help="Include bias assessment")
    analyze_parser.add_argument("--prediction-interval", action="store_true", help="Calculate prediction interval")
    analyze_parser.add_argument("--conflict-detection", action="store_true", help="Detect conflicting results")
    analyze_parser.add_argument("--report", action="store_true", help="Generate text report")
    analyze_parser.add_argument("--plots", action="store_true", help="Generate plots")
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run analysis pipeline")
    pipeline_parser.add_argument("config", help="Pipeline configuration file (YAML)")
    pipeline_parser.set_defaults(func=cmd_pipeline)
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run comprehensive demo")
    demo_parser.add_argument("--n-studies", type=int, default=25, help="Number of studies")
    demo_parser.add_argument("--seed", type=int, default=42, help="Random seed")
    demo_parser.add_argument("--output", help="Output directory")
    demo_parser.add_argument("--save-plots", action="store_true", help="Save visualization plots")
    demo_parser.add_argument("--save-report", action="store_true", help="Save text report")
    demo_parser.set_defaults(func=cmd_demo)
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.add_argument("--json", action="store_true", help="Output as JSON")
    version_parser.set_defaults(func=cmd_version)
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check system health")
    health_parser.set_defaults(func=cmd_health)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print_warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()