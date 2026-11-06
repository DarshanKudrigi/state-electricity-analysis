"""Main execution pipeline for State Electricity & Dynamic Data Analysis.

Runs data loading, audit, cleaning, statistical analysis, figure generation,
and report production for both pre-fed datasets and arbitrary user-provided data.
"""

from __future__ import annotations

import argparse
import json
import shutil
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
from dvp_project.dynamic_analyzer import (
    analyze_user_dataset,
    generate_custom_figures,
    load_user_data,
)


def run_custom_data_pipeline(
    input_file: Path | str,
    output_dir: Optional[Path | str] = None,
) -> int:
    """Execute dynamic analysis and visualization pipeline for user-provided data."""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"[-] Error: Input file '{input_path}' not found.", file=sys.stderr)
        return 1

    base_output = Path(output_dir) if output_dir else Path(__file__).resolve().parents[2] / "outputs"
    figures_dir = base_output / "figures"
    reports_dir = base_output / "reports"
    figures_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("USER DATA DYNAMIC ANALYSIS & VISUALIZATION PIPELINE")
    print(f"Target dataset: {input_path.name}")
    print("=" * 70)

    # 1. Load user data
    print("\n[Phase 1] Loading and parsing user data...")
    try:
        df = load_user_data(input_path)
        print(f"  [+] Loaded successfully: {len(df):,} records, {len(df.columns)} columns")
        print(f"  [+] Columns: {', '.join(df.columns)}")
    except Exception as err:
        print(f"  [-] Failed to parse user data: {err}", file=sys.stderr)
        return 1

    # 2. Dynamic Analysis
    print("\n[Phase 2] Running statistical and exploratory analysis...")
    analysis = analyze_user_dataset(df, dataset_name=input_path.stem)
    col_types = analysis.get("column_types", {})
    print(f"  [+] Detected Numeric columns ({len(col_types.get('numeric_cols', []))}): {', '.join(col_types.get('numeric_cols', []))}")
    print(f"  [+] Detected Categorical columns ({len(col_types.get('categorical_cols', []))}): {', '.join(col_types.get('categorical_cols', []))}")
    print(f"  [+] Detected Date columns ({len(col_types.get('date_cols', []))}): {', '.join(col_types.get('date_cols', []))}")

    # Print summary highlights
    num_summary = analysis.get("numeric_summary", {})
    for col, st in list(num_summary.items())[:3]:
        print(f"  [+] Metric '{col}': Sum={st['sum']:,}, Mean={st['mean']:,}, Min={st['min']:,}, Max={st['max']:,}")

    # 3. Generate Visualizations
    print("\n[Phase 3] Generating publication-grade visualizations for user data...")
    saved_figures = generate_custom_figures(df, analysis, output_dir=figures_dir)
    for fig_path in saved_figures:
        rel = fig_path.relative_to(Path.cwd()) if fig_path.is_relative_to(Path.cwd()) else fig_path
        print(f"  [+] Generated figure: {rel}")

    # 4. Generate Markdown Findings Report
    print("\n[Phase 4] Producing custom data summary report...")
    report_file = reports_dir / "user_data_analysis_report.md"
    with open(report_file, "w", encoding="utf-8") as rf:
        rf.write(f"# Dynamic Analysis Report: {input_path.name}\n\n")
        rf.write(f"- **Total Rows:** {len(df):,}\n")
        rf.write(f"- **Total Columns:** {len(df.columns)}\n")
        rf.write(f"- **Numeric Columns:** {', '.join(col_types.get('numeric_cols', []))}\n")
        rf.write(f"- **Categorical Columns:** {', '.join(col_types.get('categorical_cols', []))}\n")
        rf.write(f"- **Date Columns:** {', '.join(col_types.get('date_cols', []))}\n\n")
        rf.write("## Statistical Summary\n\n")
        rf.write("| Metric | Mean | Std Dev | Min | Max | Sum |\n")
        rf.write("|:-------|:-----|:--------|:----|:----|:----|\n")
        for col, st in num_summary.items():
            rf.write(f"| **{col}** | {st['mean']} | {st['std']} | {st['min']} | {st['max']} | {st['sum']} |\n")
        rf.write("\n## Generated Visualizations\n\n")
        for fig in saved_figures:
            rf.write(f"- ![{fig.stem}]({fig.name})\n")

    print(f"  [+] Report generated: {report_file}")

    # 5. Export to Dashboard
    dashboard_dir = Path(__file__).resolve().parents[2] / "dashboard"
    custom_json = dashboard_dir / "custom_data.json"
    with open(custom_json, "w", encoding="utf-8") as jf:
        json.dump(analysis, jf, indent=2)

    # Sync figures to dashboard figures directory
    dash_figures = dashboard_dir / "figures"
    dash_figures.mkdir(parents=True, exist_ok=True)
    for fig in saved_figures:
        shutil.copy2(fig, dash_figures / fig.name)

    print(f"  [+] Dashboard dynamic payload exported to: {custom_json}")
    print("\n" + "=" * 70)
    print("USER DATA PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"  To view in interactive browser dashboard:")
    print(f"  Run: uv run python -m dvp_project.serve_dashboard")
    print("=" * 70)
    return 0


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
    parser = argparse.ArgumentParser(
        description="State Electricity & Dynamic User Data Visualization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input", "-i",
        dest="input_file",
        help="Path to user-provided dataset file (CSV, JSON, TSV, Excel) to dynamically analyze and visualize.",
    )
    parser.add_argument(
        "--dashboard", "-d",
        action="store_true",
        help="Launch the interactive web dashboard server and open in browser.",
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port for the interactive dashboard server (default: 8080).",
    )
    parser.add_argument(
        "--output-dir", "-o",
        dest="output_dir",
        help="Custom output directory for figures and reports.",
    )
    parser.add_argument(
        "--data-dir",
        dest="data_dir",
        help="Custom directory for default datasets.",
    )

    args = parser.parse_args()

    if args.dashboard:
        from dvp_project.serve_dashboard import run_dashboard_server
        run_dashboard_server(port=args.port)
        return

    if args.input_file:
        code = run_custom_data_pipeline(args.input_file, output_dir=args.output_dir)
        sys.exit(code)

    code = run_pipeline(data_dir=args.data_dir, output_dir=args.output_dir)
    if code != 0:
        sys.exit(code)


if __name__ == "__main__":
    main()
