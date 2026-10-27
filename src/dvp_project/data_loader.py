"""Data loader module for State Electricity Analysis.

Provides robust functions to locate, inspect, and load datasets
without modifying original CSV files.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import pandas as pd


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "datasets"

DATASET_FILES = {
    "daily_consumption": "Indias_Electricity_Consumption_Dataset.csv",
    "monthly_population": "electricity_vs_population_all_india_monthly_2012_2025.csv",
    "monthly_urbanization": "electricity_vs_urbanization_all_india_monthly_2012_2025.csv",
    "monthly_weather": "electricity_weather_population_all_india_monthly_2012_2025.csv",
}


def resolve_data_path(filename: str, data_dir: Optional[Path | str] = None) -> Path:
    """Resolve full path to a dataset file and ensure it exists."""
    base_dir = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    target = base_dir / filename
    if not target.exists():
        # Fallback to local datasets/ relative to current working directory
        cwd_target = Path.cwd() / "datasets" / filename
        if cwd_target.exists():
            return cwd_target
        raise FileNotFoundError(
            f"Dataset file '{filename}' was not found in '{base_dir}' or '{Path.cwd() / 'datasets'}'."
        )
    return target


def load_daily_consumption(
    filepath: Optional[Path | str] = None, data_dir: Optional[Path | str] = None
) -> pd.DataFrame:
    """Load India's daily state-wise electricity consumption dataset."""
    path = Path(filepath) if filepath else resolve_data_path(DATASET_FILES["daily_consumption"], data_dir)
    return pd.read_csv(path)


def load_population_monthly(
    filepath: Optional[Path | str] = None, data_dir: Optional[Path | str] = None
) -> pd.DataFrame:
    """Load monthly electricity vs population dataset (2012-2025)."""
    path = Path(filepath) if filepath else resolve_data_path(DATASET_FILES["monthly_population"], data_dir)
    return pd.read_csv(path)


def load_urbanization_monthly(
    filepath: Optional[Path | str] = None, data_dir: Optional[Path | str] = None
) -> pd.DataFrame:
    """Load monthly electricity vs urbanization dataset (2012-2025)."""
    path = Path(filepath) if filepath else resolve_data_path(DATASET_FILES["monthly_urbanization"], data_dir)
    return pd.read_csv(path)


def load_weather_monthly(
    filepath: Optional[Path | str] = None, data_dir: Optional[Path | str] = None
) -> pd.DataFrame:
    """Load monthly electricity, weather, and population dataset (2012-2025)."""
    path = Path(filepath) if filepath else resolve_data_path(DATASET_FILES["monthly_weather"], data_dir)
    return pd.read_csv(path)


def load_all_datasets(data_dir: Optional[Path | str] = None) -> Dict[str, pd.DataFrame]:
    """Load all 4 project datasets into a dictionary."""
    return {
        "daily_consumption": load_daily_consumption(data_dir=data_dir),
        "monthly_population": load_population_monthly(data_dir=data_dir),
        "monthly_urbanization": load_urbanization_monthly(data_dir=data_dir),
        "monthly_weather": load_weather_monthly(data_dir=data_dir),
    }


def audit_datasets(data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Audit shapes, columns, data types, missing values, duplicates, and date ranges."""
    audit_results: Dict[str, Any] = {}

    for key, df in data_dict.items():
        missing_counts = df.isna().sum()
        missing_dict = missing_counts[missing_counts > 0].to_dict()
        num_duplicates = int(df.duplicated().sum())

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

        date_coverage: Optional[Tuple[str, str]] = None
        if "Dates" in df.columns:
            dt_series = pd.to_datetime(df["Dates"], errors="coerce")
            valid_dt = dt_series.dropna()
            if not valid_dt.empty:
                date_coverage = (str(valid_dt.min().date()), str(valid_dt.max().date()))
        elif "Year" in df.columns and "Month" in df.columns:
            min_yr, max_yr = int(df["Year"].min()), int(df["Year"].max())
            date_coverage = (f"{min_yr}-01", f"{max_yr}-12")

        audit_results[key] = {
            "shape": df.shape,
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": list(df.columns),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
            "missing_values": missing_dict,
            "missing_total": int(missing_counts.sum()),
            "duplicates": num_duplicates,
            "numeric_columns": numeric_cols,
            "categorical_columns": non_numeric_cols,
            "date_coverage": date_coverage,
        }

    return audit_results
