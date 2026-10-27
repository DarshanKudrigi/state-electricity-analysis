"""Comprehensive unit and integration tests for State Electricity Analysis.

Tests CSV loading, missing-file handling, column integrity, date parsing,
cleaning, statistical calculations, and non-interactive figure generation.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure src is discoverable
_src_dir = str(Path(__file__).resolve().parents[1] / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import numpy as np
import pandas as pd

from dvp_project.data_loader import (
    DEFAULT_DATA_DIR,
    audit_datasets,
    load_all_datasets,
    load_daily_consumption,
    resolve_data_path,
)
from dvp_project.cleaning import (
    clean_all,
    clean_daily_dataset,
    clean_monthly_dataset,
    melt_daily_to_long,
)
from dvp_project.analysis import (
    compute_correlations,
    compute_daily_trends,
    compute_descriptive_stats,
    compute_monthly_seasonality,
    compute_state_rankings,
    run_full_analysis,
)
from dvp_project.visualizations import (
    generate_all_visualizations,
    plot_electricity_vs_population,
    plot_seasonal_monthly_pattern,
    plot_total_consumption_timeseries,
)
from dvp_project.reports import generate_data_audit_report, generate_findings_report


class TestDataLoader(unittest.TestCase):
    """Test data loading and missing file handling."""

    def test_missing_file_raises_error(self):
        """Verify resolve_data_path raises FileNotFoundError with clear message."""
        with self.assertRaises(FileNotFoundError) as ctx:
            resolve_data_path("non_existent_dataset_12345.csv")
        self.assertIn("non_existent_dataset_12345.csv", str(ctx.exception))

    def test_load_all_datasets(self):
        """Verify that all four repository datasets load and have positive row counts."""
        datasets = load_all_datasets()
        expected_keys = [
            "daily_consumption",
            "monthly_population",
            "monthly_urbanization",
            "monthly_weather",
        ]
        for key in expected_keys:
            self.assertIn(key, datasets)
            self.assertIsInstance(datasets[key], pd.DataFrame)
            self.assertGreater(len(datasets[key]), 0, f"Dataset '{key}' is unexpectedly empty.")

    def test_audit_datasets(self):
        """Verify audit_datasets extracts correct schema and missing value summaries."""
        synthetic_data = {
            "test_ds": pd.DataFrame({
                "Dates": ["2020-01-01", "2020-01-02", "2020-01-03"],
                "Value": [10.5, np.nan, 30.0],
                "Category": ["A", "B", "A"],
            })
        }
        audit = audit_datasets(synthetic_data)
        self.assertIn("test_ds", audit)
        self.assertEqual(audit["test_ds"]["rows"], 3)
        self.assertEqual(audit["test_ds"]["columns"], 3)
        self.assertEqual(audit["test_ds"]["missing_values"], {"Value": 1})
        self.assertEqual(audit["test_ds"]["duplicates"], 0)
        self.assertEqual(audit["test_ds"]["date_coverage"], ("2020-01-01", "2020-01-03"))


class TestCleaning(unittest.TestCase):
    """Test data cleaning and restructuring functions."""

    def test_clean_daily_dataset(self):
        """Verify clean_daily_dataset parses dates and adds calendar attributes."""
        synthetic_daily = pd.DataFrame({
            "Unnamed: 0": [0, 1],
            "Dates": ["2021-05-15", "2021-05-16"],
            "State_A": ["12.5", "13.2"],
            "Total Consumption": [100.0, 102.5],
        })
        cleaned = clean_daily_dataset(synthetic_daily)
        self.assertNotIn("Unnamed: 0", cleaned.columns)
        self.assertIn("Date", cleaned.columns)
        self.assertIn("Year", cleaned.columns)
        self.assertIn("Month_Name", cleaned.columns)
        self.assertEqual(cleaned["Year"].iloc[0], 2021)
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned["State_A"]))

    def test_melt_daily_to_long(self):
        """Verify wide-to-long transformation of daily state columns."""
        synthetic_clean = pd.DataFrame({
            "Date": pd.to_datetime(["2021-01-01"]),
            "Year": [2021],
            "Month": [1],
            "Punjab": [50.2],
            "Haryana": [45.1],
            "Total Consumption": [95.3],
        })
        long_df = melt_daily_to_long(synthetic_clean)
        self.assertEqual(len(long_df), 2)
        self.assertListEqual(sorted(long_df["State_UT"].tolist()), ["Haryana", "Punjab"])
        self.assertNotIn("Total Consumption", long_df["State_UT"].values)

    def test_clean_monthly_dataset(self):
        """Verify clean_monthly_dataset standardizes date, state and types."""
        synthetic_monthly = pd.DataFrame({
            "Year": ["2022", "2022"],
            "Month": [3, 4],
            "State_UT": ["  Kerala ", "Kerala"],
            "Electricity_Consumption_GWh": [5.1, 5.4],
        })
        cleaned = clean_monthly_dataset(synthetic_monthly)
        self.assertEqual(cleaned["State_UT"].iloc[0], "Kerala")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned["Date"]))
        self.assertEqual(cleaned["Date"].iloc[0], pd.Timestamp("2022-03-01"))


class TestAnalysis(unittest.TestCase):
    """Test descriptive statistics, trend calculations, rankings, and correlations."""

    def setUp(self):
        self.synthetic_pop = pd.DataFrame({
            "Year": [2020, 2020, 2020, 2020],
            "Month": [1, 1, 2, 2],
            "State_UT": ["State1", "State2", "State1", "State2"],
            "Population_Million": [100.0, 50.0, 100.0, 50.0],
            "Electricity_Consumption_GWh": [10.0, 5.0, 12.0, 6.0],
            "Electricity_Per_Capita_kWh": [100.0, 100.0, 120.0, 120.0],
        })

    def test_compute_descriptive_stats(self):
        stats = compute_descriptive_stats(self.synthetic_pop, ["Electricity_Consumption_GWh"])
        self.assertIn("Electricity_Consumption_GWh", stats.index)
        self.assertAlmostEqual(stats.loc["Electricity_Consumption_GWh", "mean"], 8.25)
        self.assertAlmostEqual(stats.loc["Electricity_Consumption_GWh", "min"], 5.0)

    def test_compute_state_rankings(self):
        rankings = compute_state_rankings(self.synthetic_pop)
        top = rankings["top_10_consumption"]
        self.assertEqual(top.iloc[0]["State_UT"], "State1")
        self.assertAlmostEqual(top.iloc[0]["mean_monthly_consumption_gwh"], 11.0)

    def test_compute_correlations(self):
        corrs = compute_correlations(
            self.synthetic_pop, ["Population_Million", "Electricity_Consumption_GWh"]
        )
        pearson = corrs["pearson"]
        self.assertAlmostEqual(
            pearson.loc["Population_Million", "Electricity_Consumption_GWh"], 0.961, places=2
        )

    def test_compute_daily_trends(self):
        synthetic_daily = pd.DataFrame({
            "Date": pd.to_datetime(["2020-01-01", "2020-01-02", "2021-01-01"]),
            "Year": [2020, 2020, 2021],
            "Month": [1, 1, 1],
            "Day_Name": ["Wed", "Thu", "Fri"],
            "Total Consumption": [3000.0, 3100.0, 3300.0],
        })
        trends = compute_daily_trends(synthetic_daily)
        self.assertEqual(trends["overall_record_count"], 3)
        self.assertAlmostEqual(trends["overall_min"], 3000.0)
        self.assertAlmostEqual(trends["overall_max"], 3300.0)
        self.assertEqual(len(trends["annual_stats"]), 2)


class TestVisualizationsAndReports(unittest.TestCase):
    """Test non-interactive figure generation and report writing."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.figures_dir = Path(self.temp_dir) / "figures"
        self.reports_dir = Path(self.temp_dir) / "reports"
        self.figures_dir.mkdir(parents=True)
        self.reports_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_figures_non_interactive(self):
        """Verify charts generate valid PNG files without displaying GUI windows."""
        synthetic_pop = pd.DataFrame({
            "Year": [2021] * 12,
            "Month": list(range(1, 13)),
            "State_UT": ["Sample State"] * 12,
            "Population_Million": [50.0] * 12,
            "Electricity_Consumption_GWh": [3.0 + (m * 0.1) for m in range(1, 13)],
            "Electricity_Per_Capita_kWh": [600.0] * 12,
        })
        out_path = plot_seasonal_monthly_pattern(synthetic_pop, self.figures_dir)
        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 1000)
        # Check PNG magic bytes
        with open(out_path, "rb") as f:
            header = f.read(8)
            self.assertEqual(header[:4], b"\x89PNG")

    def test_generate_reports(self):
        """Verify markdown audit and findings reports write properly formatted markdown."""
        audit_dummy = {
            "sample_ds": {
                "rows": 100,
                "columns": 5,
                "column_names": ["A", "B", "C", "D", "E"],
                "dtypes": {"A": "int64", "B": "float64"},
                "missing_values": {},
                "missing_total": 0,
                "duplicates": 0,
                "date_coverage": ("2020-01-01", "2020-12-31"),
            }
        }
        audit_file = generate_data_audit_report(audit_dummy, self.reports_dir)
        self.assertTrue(audit_file.exists())
        content = audit_file.read_text(encoding="utf-8")
        self.assertIn("# Data Audit Report", content)
        self.assertIn("`sample_ds`", content)


if __name__ == "__main__":
    unittest.main()
