"""Dynamic Data Analyzer for User-Provided Datasets.

Enables the system to accept arbitrary user datasets (CSV, JSON, TSV),
automatically detect schemas (dates, categories, metrics), perform statistical
analysis, and produce structured data for interactive visualizations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


def load_user_data(
    source: Union[str, Path, pd.DataFrame],
    file_type: Optional[str] = None,
) -> pd.DataFrame:
    """Load arbitrary user data from file path, raw string, or DataFrame."""
    if isinstance(source, pd.DataFrame):
        return source.copy()

    path_obj = Path(source) if isinstance(source, (str, Path)) and "\n" not in str(source) and Path(str(source)).exists() else None

    if path_obj is not None:
        suffix = path_obj.suffix.lower()
        if suffix in [".csv", ".txt"]:
            try:
                return pd.read_csv(path_obj)
            except Exception:
                return pd.read_csv(path_obj, sep=None, engine="python")
        elif suffix == ".tsv":
            return pd.read_csv(path_obj, sep="\t")
        elif suffix == ".json":
            return pd.read_json(path_obj)
        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(path_obj)
        else:
            return pd.read_csv(path_obj)

    # String input (raw text pasted by user)
    raw_str = str(source).strip()
    if raw_str.startswith("[") or raw_str.startswith("{"):
        import io
        return pd.read_json(io.StringIO(raw_str))
    
    # Try comma-separated, fallback to tab or auto
    import io
    try:
        return pd.read_csv(io.StringIO(raw_str))
    except Exception:
        return pd.read_csv(io.StringIO(raw_str), sep=None, engine="python")


def detect_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Detect date, numeric, categorical, and identifier columns from DataFrame."""
    date_cols: List[str] = []
    numeric_cols: List[str] = []
    categorical_cols: List[str] = []

    for col in df.columns:
        col_series = df[col]
        col_lower = str(col).lower()

        # Check numeric
        if pd.api.types.is_numeric_dtype(col_series):
            # If named year or month, could also serve as date/category, but primarily numeric
            numeric_cols.append(col)
            continue

        # Check datetime
        if pd.api.types.is_datetime64_any_dtype(col_series):
            date_cols.append(col)
            continue

        # Check if text column can be parsed as datetime
        if any(keyword in col_lower for keyword in ["date", "time", "timestamp", "month_year", "period"]):
            try:
                sample = col_series.dropna().head(20)
                if not sample.empty:
                    parsed = pd.to_datetime(sample, errors="coerce")
                    if parsed.notna().sum() >= len(sample) * 0.7:
                        date_cols.append(col)
                        continue
            except Exception:
                pass

        # Try converting numeric string
        try:
            sample = col_series.dropna().head(50)
            if not sample.empty:
                numeric_try = pd.to_numeric(sample.astype(str).str.replace(",", "").str.strip(), errors="coerce")
                if numeric_try.notna().sum() >= len(sample) * 0.9:
                    numeric_cols.append(col)
                    continue
        except Exception:
            pass

        # Otherwise categorical
        categorical_cols.append(col)

    return {
        "date_cols": date_cols,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
    }


def analyze_user_dataset(
    df: pd.DataFrame,
    dataset_name: str = "User Uploaded Data",
) -> Dict[str, Any]:
    """Perform exploratory, statistical, and aggregation analysis on user data."""
    if df.empty:
        return {
            "name": dataset_name,
            "row_count": 0,
            "column_count": 0,
            "columns": [],
            "error": "Dataset is empty.",
        }

    # Clean column names for easier web and python manipulation
    df = df.copy()
    col_types = detect_column_types(df)
    numeric_cols = col_types["numeric_cols"]
    date_cols = col_types["date_cols"]
    cat_cols = col_types["categorical_cols"]

    # Convert detected numeric columns that might be object strings
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").str.strip(), errors="coerce")

    # Convert detected date columns
    for col in date_cols:
        if not pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 1. Summary Statistics for Numeric Columns
    stats_dict: Dict[str, Dict[str, float]] = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if not series.empty:
            stats_dict[col] = {
                "count": int(series.count()),
                "sum": round(float(series.sum()), 2),
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2) if series.count() > 1 else 0.0,
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "median": round(float(series.median()), 2),
            }

    # 2. Correlation Matrix (if >= 2 numeric columns)
    correlations: Dict[str, Dict[str, float]] = {}
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr(method="pearson").round(3)
        correlations = corr_matrix.fillna(0.0).to_dict()

    # 3. Categorical Aggregations (Top Categories)
    cat_summaries: Dict[str, List[Dict[str, Any]]] = {}
    primary_cat = cat_cols[0] if cat_cols else None
    primary_num = numeric_cols[0] if numeric_cols else None

    for col in cat_cols[:3]:  # Top 3 categorical columns
        val_counts = df[col].value_counts().head(15)
        if primary_num and primary_num in df.columns:
            # Group by category and compute sum & mean
            grouped = df.groupby(col, observed=True)[primary_num].agg(["sum", "mean", "count"]).round(2)
            grouped = grouped.sort_values(by="sum", ascending=False).head(15)
            cat_summaries[col] = [
                {
                    "label": str(idx),
                    "sum": float(row["sum"]),
                    "mean": float(row["mean"]),
                    "count": int(row["count"]),
                }
                for idx, row in grouped.iterrows()
            ]
        else:
            cat_summaries[col] = [
                {"label": str(k), "count": int(v)} for k, v in val_counts.items()
            ]

    # 4. Time Series Trend (if date column exists)
    time_series_data: List[Dict[str, Any]] = []
    primary_date = date_cols[0] if date_cols else None
    if primary_date and primary_num:
        ts_df = df.dropna(subset=[primary_date, primary_num]).sort_values(by=primary_date)
        if len(ts_df) > 300:
            # Downsample evenly for high performance web display
            step = max(1, len(ts_df) // 250)
            ts_df = ts_df.iloc[::step]

        time_series_data = [
            {
                "date": row[primary_date].strftime("%Y-%m-%d") if hasattr(row[primary_date], "strftime") else str(row[primary_date]),
                "value": round(float(row[primary_num]), 2),
            }
            for _, row in ts_df.iterrows()
        ]

    # 5. Missing Values Audit
    missing_counts = {str(k): int(v) for k, v in df.isna().sum().items() if v > 0}

    # 6. Sample records for instant table preview (first 100 rows)
    records_sample = df.head(100).fillna("").to_dict(orient="records")
    # Convert datetimes to string in sample
    for row in records_sample:
        for k, v in row.items():
            if isinstance(v, (pd.Timestamp, np.datetime64)):
                row[k] = str(v)

    return {
        "name": dataset_name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": [str(c) for c in df.columns],
        "column_types": col_types,
        "numeric_summary": stats_dict,
        "correlations": correlations,
        "category_summaries": cat_summaries,
        "time_series": time_series_data,
        "primary_metric": primary_num,
        "primary_category": primary_cat,
        "primary_date": primary_date,
        "missing_values": missing_counts,
        "sample_records": records_sample,
    }


def generate_custom_figures(
    df: pd.DataFrame,
    analysis: Dict[str, Any],
    output_dir: Path | str,
) -> List[Path]:
    """Generate publication-ready Matplotlib/Seaborn figures for user data."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    generated_figures: List[Path] = []

    sns.set_theme(style="whitegrid", palette="deep")
    num_cols = analysis.get("column_types", {}).get("numeric_cols", [])
    cat_cols = analysis.get("column_types", {}).get("categorical_cols", [])
    date_cols = analysis.get("column_types", {}).get("date_cols", [])

    # 1. Category Bar Chart (Ranking)
    if cat_cols and num_cols:
        cat_col = cat_cols[0]
        num_col = num_cols[0]
        grouped = df.groupby(cat_col, observed=True)[num_col].sum().sort_values(ascending=False).head(12)
        if not grouped.empty:
            fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
            bars = ax.barh(grouped.index.astype(str), grouped.values, color="#0ea5e9", edgecolor="#0284c7")
            ax.invert_yaxis()
            ax.set_title(f"User Data: {num_col} by {cat_col} (Top 12)", fontsize=13, weight="bold", pad=12)
            ax.set_xlabel(num_col, fontsize=11)
            ax.set_ylabel(cat_col, fontsize=11)
            plt.tight_layout()
            fig_path = out_path / "custom_category_ranking.png"
            fig.savefig(fig_path)
            plt.close(fig)
            generated_figures.append(fig_path)

    # 2. Time-series Plot
    if date_cols and num_cols:
        date_col = date_cols[0]
        num_col = num_cols[0]
        ts_df = df.dropna(subset=[date_col, num_col]).sort_values(by=date_col)
        if not ts_df.empty:
            fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
            ax.plot(ts_df[date_col], ts_df[num_col], color="#6366f1", linewidth=1.8, label=num_col)
            ax.set_title(f"User Data: Temporal Trajectory ({num_col})", fontsize=13, weight="bold", pad=12)
            ax.set_xlabel(date_col, fontsize=11)
            ax.set_ylabel(num_col, fontsize=11)
            ax.legend()
            plt.tight_layout()
            fig_path = out_path / "custom_time_series.png"
            fig.savefig(fig_path)
            plt.close(fig)
            generated_figures.append(fig_path)

    # 3. Numeric Distribution Histogram
    if num_cols:
        num_col = num_cols[0]
        clean_num = df[num_col].dropna()
        if len(clean_num) > 1:
            fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
            sns.histplot(clean_num, kde=True, color="#10b981", ax=ax)
            ax.set_title(f"User Data: Distribution of {num_col}", fontsize=13, weight="bold", pad=12)
            ax.set_xlabel(num_col, fontsize=11)
            ax.set_ylabel("Frequency", fontsize=11)
            plt.tight_layout()
            fig_path = out_path / "custom_metric_distribution.png"
            fig.savefig(fig_path)
            plt.close(fig)
            generated_figures.append(fig_path)

    # 4. Correlation Heatmap
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, cbar=True, square=True)
        ax.set_title("User Data: Correlation Matrix", fontsize=13, weight="bold", pad=12)
        plt.tight_layout()
        fig_path = out_path / "custom_correlation_heatmap.png"
        fig.savefig(fig_path)
        plt.close(fig)
        generated_figures.append(fig_path)

    return generated_figures

