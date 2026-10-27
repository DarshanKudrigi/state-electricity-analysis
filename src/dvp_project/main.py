"""Main execution pipeline for State Electricity Consumption Analysis.

Runs data loading, audit, cleaning, statistical analysis, figure generation,
and report production.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Ensure package root 'src' is discoverable
_src_dir = str(Path(__file__).resolve().parents[1])
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from dvp_project.data_loader import audit_datasets, load_all_datasets
from dvp_project.cleaning import clean_all
from dvp_project.analysis import run_full_analysis
from dvp_project.visualizations import generate_all_visualizations
from dvp_project.reports import generate_data_audit_report, generate_findings_report


def run_pipeline(
    data_dir: Optional[Path | str] = None,
    output_dir: Optional[Path | str] = None,
) -> int:
    """Execute the full end-to-end data analysis pipeline."""
    base_output = Path(output_dir) if output_dir else Path(__file__).resolve().parents[2] / "outputs"
    figures_dir = base_output / "figures"
    reports_dir = base_output / "reports"

    print("=" * 70)
    print("STATE ELECTRICITY CONSUMPTION ANALYSIS AND VISUALIZATION")
    print("=" * 70)

    # 1. Load Datasets
    print("\n[Phase 1] Loading and validating datasets...")
    try:
        raw_data = load_all_datasets(data_dir=data_dir)
        for name, df in raw_data.items():
            print(f"  [+] Loaded '{name}': {df.shape[0]:,} rows, {df.shape[1]} columns")
    except FileNotFoundError as err:
        print(f"  [-] Error loading dataset: {err}", file=sys.stderr)
        return 1

    # 2. Audit Datasets
    print("\n[Phase 2] Auditing datasets...")
    audit_results = audit_datasets(raw_data)
    audit_report_path = generate_data_audit_report(audit_results, reports_dir=reports_dir)
    print(f"  [+] Audit report generated: {audit_report_path.relative_to(Path.cwd()) if audit_report_path.is_relative_to(Path.cwd()) else audit_report_path}")

    # 3. Clean Datasets
    print("\n[Phase 3] Cleaning and standardizing datasets...")
    cleaned_data = clean_all(raw_data)
    for name, df in cleaned_data.items():
        print(f"  [+] Cleaned '{name}': {df.shape[0]:,} rows, {df.shape[1]} columns")

    # 4. Statistical Analysis
    print("\n[Phase 4] Performing exploratory and statistical analysis...")
    analysis_results = run_full_analysis(cleaned_data)
    
    # Print key highlights to console
    if "daily_trends" in analysis_results:
        daily_t = analysis_results["daily_trends"]
        print(f"  [+] Historical All-India Daily Mean: {daily_t.get('overall_mean', 0):,.1f} GWh/day")
        print(f"  [+] Peak Daily Record: {daily_t.get('overall_max', 0):,.1f} GWh/day")

    if "population_corr" in analysis_results:
        r_pop = analysis_results["population_corr"]["pearson"].loc[
            "Population_Million", "Electricity_Consumption_GWh"
        ]
        print(f"  [+] Population vs Electricity Consumption Correlation: r = {r_pop:.3f}")

    if "weather_corr" in analysis_results:
        r_temp = analysis_results["weather_corr"]["pearson"].loc[
            "Avg_Temperature_C", "Electricity_Consumption_GWh"
        ]
        print(f"  [+] Temperature vs Electricity Consumption Correlation: r = {r_temp:+.3f}")

    # 5. Visualizations
    print("\n[Phase 5] Generating publication-grade visualizations...")
    saved_figures = generate_all_visualizations(cleaned_data, analysis_results, figures_dir=figures_dir)
    for fig_path in saved_figures:
        rel = fig_path.relative_to(Path.cwd()) if fig_path.is_relative_to(Path.cwd()) else fig_path
        print(f"  [+] Saved figure: {rel}")

    # 6. Reports Generation
    print("\n[Phase 6] Generating comprehensive findings report...")
    findings_report_path = generate_findings_report(
        analysis_results, saved_figures, reports_dir=reports_dir
    )
    rel_report = (
        findings_report_path.relative_to(Path.cwd())
        if findings_report_path.is_relative_to(Path.cwd())
        else findings_report_path
    )
    print(f"  [+] Findings report generated: {rel_report}")

    # 7. Update Dashboard Data
    try:
        from dvp_project.dashboard_data import export_dashboard_data
        import shutil
        dashboard_dir = Path(__file__).resolve().parents[2] / "dashboard"
        export_dashboard_data(dashboard_dir / "data.json")
        figures_dest = dashboard_dir / "figures"
        figures_dest.mkdir(parents=True, exist_ok=True)
        for fig in saved_figures:
            shutil.copy2(fig, figures_dest / fig.name)
        print("  [+] Interactive dashboard assets updated: dashboard/index.html")
    except Exception as err:
        print(f"  [!] Note: Dashboard data export skipped ({err})")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"  Outputs generated in: {base_output.resolve()}")
    print(f"  - Figures ({len(saved_figures)}): {figures_dir.resolve()}")
    print(f"  - Reports (2): {reports_dir.resolve()}")
    print(f"  - Web Dashboard: {dashboard_dir.resolve() / 'index.html'}")
    print("  Run 'uv run python -m dvp_project.serve_dashboard' or 'uv run dvp-project --dashboard' to launch.")
    print("=" * 70)

    return 0


def main() -> None:
    """CLI entry point for dvp-project."""
    if "--dashboard" in sys.argv:
        from dvp_project.serve_dashboard import run_dashboard_server
        run_dashboard_server()
        return

    code = run_pipeline()
    if code != 0:
        sys.exit(code)


if __name__ == "__main__":
    main()
