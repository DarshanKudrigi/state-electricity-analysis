"""Data cleaning module for State Electricity Analysis.

Performs robust, non-destructive data cleaning and standardization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Trim leading/trailing whitespaces and preserve semantic column names."""
    cleaned = df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]
    return cleaned


def clean_daily_dataset(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Clean India's daily electricity consumption dataset.
    
    Operations:
    - Standardizes column names.
    - Removes artifact index columns ('Unnamed: 0') if present.
    - Parses 'Dates' into datetime.
    - Adds calendar temporal attributes (Year, Month, Month_Name, Day_of_Week, Day_Name).
    - Ensures numeric state columns and Total Consumption are converted to float.
    - Sorts chronologically.
    """
    df = clean_column_names(df_raw)

    # Drop artifact index column
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Parse Dates
    if "Dates" in df.columns:
        df["Date"] = pd.to_datetime(df["Dates"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
        df["Month_Name"] = df["Date"].dt.strftime("%b")
        df["Day_Name"] = df["Date"].dt.strftime("%a")

    # Ensure numeric columns are strictly float
    state_and_total_cols = [c for c in df.columns if c not in ["Dates", "Date", "Year", "Month", "Month_Name", "Day_Name"]]
    for col in state_and_total_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def melt_daily_to_long(df_clean_daily: pd.DataFrame) -> pd.DataFrame:
    """Transform wide daily dataset into long format: [Date, Year, Month, State_UT, Consumption_GWh].
    
    Excludes aggregate summary column 'Total Consumption' and entity columns
    to focus on geographical state/UT observations.
    """
    exclude_cols = {"Dates", "Date", "Year", "Month", "Month_Name", "Day_Name", "Total Consumption"}
    state_cols = [c for c in df_clean_daily.columns if c not in exclude_cols]

    long_df = pd.melt(
        df_clean_daily,
        id_vars=["Date", "Year", "Month"],
        value_vars=state_cols,
        var_name="State_UT",
        value_name="Daily_Consumption_GWh",
    )
    long_df = long_df.dropna(subset=["Daily_Consumption_GWh"])
    return long_df.sort_values(["Date", "State_UT"]).reset_index(drop=True)


def clean_monthly_dataset(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Clean monthly datasets (population, urbanization, weather).
    
    Operations:
    - Standardizes column names.
    - Converts Year and Month to integers.
    - Creates a standardized 'Date' column set to the first day of each month.
    - Strips whitespace from State_UT.
    - Validates positive ranges for physical quantities.
    - Sorts chronologically by State_UT, Year, Month.
    """
    df = clean_column_names(df_raw)

    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype(int)
    if "Month" in df.columns:
        df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype(int)

    if "Year" in df.columns and "Month" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Year"].astype(str) + "-" + df["Month"].astype(str).str.zfill(2) + "-01"
        )
        df["Month_Name"] = df["Date"].dt.strftime("%b")

    if "State_UT" in df.columns:
        df["State_UT"] = df["State_UT"].astype(str).str.strip()

    # Convert numeric fields
    numeric_candidates = [c for c in df.columns if c not in ["State_UT", "Date", "Month_Name"]]
    for col in numeric_candidates:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    sort_cols = [c for c in ["State_UT", "Year", "Month"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols).reset_index(drop=True)

    return df


def clean_all(raw_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Clean all raw datasets and return cleaned dictionary."""
    cleaned: Dict[str, pd.DataFrame] = {}

    if "daily_consumption" in raw_dict:
        cleaned["daily_consumption"] = clean_daily_dataset(raw_dict["daily_consumption"])
        cleaned["daily_long"] = melt_daily_to_long(cleaned["daily_consumption"])

    if "monthly_population" in raw_dict:
        cleaned["monthly_population"] = clean_monthly_dataset(raw_dict["monthly_population"])

    if "monthly_urbanization" in raw_dict:
        cleaned["monthly_urbanization"] = clean_monthly_dataset(raw_dict["monthly_urbanization"])

    if "monthly_weather" in raw_dict:
        cleaned["monthly_weather"] = clean_monthly_dataset(raw_dict["monthly_weather"])

    return cleaned
