"""Statistical analysis and EDA computation module for State Electricity Analysis.

Computes descriptive statistics, temporal trends, demographic correlations,
weather associations, and state-level rankings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def compute_descriptive_stats(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Compute count, mean, std, min, 25%, median, 75%, max for selected numeric columns."""
    if columns is not None:
        valid_cols = [c for c in columns if c in df.columns]
        target_df = df[valid_cols]
    else:
        target_df = df.select_dtypes(include=["number"])

    desc = target_df.describe().T
    desc["median"] = target_df.median()
    desc = desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    return desc


def compute_daily_trends(df_daily: pd.DataFrame) -> Dict[str, Any]:
    """Analyze long-term daily consumption trends and annual changes from 2013 to 2024."""
    if "Total Consumption" not in df_daily.columns or "Year" not in df_daily.columns:
        return {}

    annual_stats = (
        df_daily.groupby("Year")["Total Consumption"]
        .agg(
            mean_daily_gwh="mean",
            min_daily_gwh="min",
            max_daily_gwh="max",
            std_daily_gwh="std",
            days_recorded="count",
        )
        .reset_index()
    )

    # Year-over-Year percentage change
    annual_stats["yoy_growth_pct"] = annual_stats["mean_daily_gwh"].pct_change() * 100.0

    # Day of week patterns
    dow_stats = (
        df_daily.groupby("Day_Name")["Total Consumption"]
        .agg(["mean", "std", "count"])
        .reindex(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    )

    # Monthly seasonality from daily data
    monthly_daily_stats = (
        df_daily.groupby("Month")["Total Consumption"]
        .agg(mean_daily_gwh="mean", std_daily_gwh="std")
        .reset_index()
    )

    return {
        "annual_stats": annual_stats,
        "dow_stats": dow_stats,
        "monthly_daily_stats": monthly_daily_stats,
        "overall_mean": float(df_daily["Total Consumption"].mean()),
        "overall_min": float(df_daily["Total Consumption"].min()),
        "overall_max": float(df_daily["Total Consumption"].max()),
        "overall_record_count": int(df_daily["Total Consumption"].count()),
    }


def compute_state_rankings(df_pop: pd.DataFrame) -> Dict[str, Any]:
    """Rank states and Union Territories by average monthly electricity consumption and per capita use."""
    state_agg = (
        df_pop.groupby("State_UT")
        .agg(
            mean_monthly_consumption_gwh=("Electricity_Consumption_GWh", "mean"),
            std_monthly_consumption_gwh=("Electricity_Consumption_GWh", "std"),
            mean_per_capita_kwh=("Electricity_Per_Capita_kWh", "mean"),
            mean_population_million=("Population_Million", "mean"),
        )
        .reset_index()
    )

    top_10_consumption = state_agg.sort_values(
        "mean_monthly_consumption_gwh", ascending=False
    ).head(10)
    bottom_10_consumption = state_agg.sort_values(
        "mean_monthly_consumption_gwh", ascending=True
    ).head(10)

    top_10_per_capita = state_agg.sort_values(
        "mean_per_capita_kwh", ascending=False
    ).head(10)
    bottom_10_per_capita = state_agg.sort_values(
        "mean_per_capita_kwh", ascending=True
    ).head(10)

    return {
        "state_agg": state_agg,
        "top_10_consumption": top_10_consumption,
        "bottom_10_consumption": bottom_10_consumption,
        "top_10_per_capita": top_10_per_capita,
        "bottom_10_per_capita": bottom_10_per_capita,
    }


def compute_monthly_seasonality(df_pop: pd.DataFrame) -> pd.DataFrame:
    """Analyze monthly consumption seasonality across states."""
    seasonality = (
        df_pop.groupby("Month")
        .agg(
            mean_consumption_gwh=("Electricity_Consumption_GWh", "mean"),
            median_consumption_gwh=("Electricity_Consumption_GWh", "median"),
            std_consumption_gwh=("Electricity_Consumption_GWh", "std"),
            mean_per_capita_kwh=("Electricity_Per_Capita_kWh", "mean"),
        )
        .reset_index()
    )
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    seasonality["Month_Name"] = seasonality["Month"].apply(lambda m: month_names[m - 1])
    return seasonality


def compute_correlations(df: pd.DataFrame, columns: List[str]) -> Dict[str, pd.DataFrame]:
    """Compute Pearson and Spearman correlation matrices for specified numeric columns."""
    valid_cols = [c for c in columns if c in df.columns]
    subset = df[valid_cols].dropna()

    pearson_corr = subset.corr(method="pearson")
    spearman_corr = subset.corr(method="spearman")

    return {
        "pearson": pearson_corr,
        "spearman": spearman_corr,
        "n_samples": len(subset),
    }


def run_full_analysis(cleaned_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Run comprehensive statistical analysis across all cleaned datasets."""
    analysis: Dict[str, Any] = {}

    # 1. Daily trends analysis
    if "daily_consumption" in cleaned_dict:
        analysis["daily_trends"] = compute_daily_trends(cleaned_dict["daily_consumption"])
        analysis["daily_desc"] = compute_descriptive_stats(
            cleaned_dict["daily_consumption"], columns=["Total Consumption"]
        )

    # 2. State-level rankings and monthly seasonality
    if "monthly_population" in cleaned_dict:
        df_pop = cleaned_dict["monthly_population"]
        analysis["state_rankings"] = compute_state_rankings(df_pop)
        analysis["seasonality"] = compute_monthly_seasonality(df_pop)
        analysis["population_corr"] = compute_correlations(
            df_pop,
            [
                "Population_Million",
                "Population_Growth_pct",
                "Electricity_Consumption_GWh",
                "Electricity_Per_Capita_kWh",
            ],
        )
        analysis["pop_desc"] = compute_descriptive_stats(
            df_pop,
            [
                "Population_Million",
                "Population_Growth_pct",
                "Electricity_Consumption_GWh",
                "Electricity_Per_Capita_kWh",
            ],
        )

    # 3. Urbanization analysis
    if "monthly_urbanization" in cleaned_dict:
        df_urb = cleaned_dict["monthly_urbanization"]
        analysis["urbanization_corr"] = compute_correlations(
            df_urb,
            [
                "Population_Million",
                "Urban_Population_Million",
                "Urbanization_Rate_pct",
                "Urban_Population_Growth_pct",
                "Electricity_Consumption_GWh",
                "Electricity_Per_Capita_kWh",
            ],
        )
        analysis["urb_desc"] = compute_descriptive_stats(
            df_urb,
            [
                "Urban_Population_Million",
                "Urbanization_Rate_pct",
                "Urban_Population_Growth_pct",
            ],
        )

    # 4. Weather analysis
    if "monthly_weather" in cleaned_dict:
        df_wx = cleaned_dict["monthly_weather"]
        wx_variables = [
            "Avg_Temperature_C",
            "Max_Temperature_C",
            "Min_Temperature_C",
            "Humidity_pct",
            "Rainfall_mm",
            "Wind_Speed_kmh",
            "Solar_Radiation_kWh_m2",
            "Electricity_Consumption_GWh",
            "Electricity_Per_Capita_kWh",
        ]
        analysis["weather_corr"] = compute_correlations(df_wx, wx_variables)
        analysis["wx_desc"] = compute_descriptive_stats(
            df_wx,
            [
                "Avg_Temperature_C",
                "Max_Temperature_C",
                "Min_Temperature_C",
                "Humidity_pct",
                "Rainfall_mm",
                "Wind_Speed_kmh",
                "Solar_Radiation_kWh_m2",
            ],
        )

    return analysis
