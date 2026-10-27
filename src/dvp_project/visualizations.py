"""Visualization module for State Electricity Analysis.

Generates publication-quality charts using Matplotlib and Seaborn
with non-interactive backend configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns


DEFAULT_FIGURES_DIR = Path(__file__).resolve().parents[2] / "outputs" / "figures"

# Custom aesthetic styling parameters
PALETTE_PRIMARY = "#1e3a8a"      # Deep Royal Blue
PALETTE_SECONDARY = "#0284c7"    # Cyan / Sky
PALETTE_ACCENT = "#e11d48"       # Crimson / Coral
PALETTE_SUCCESS = "#059669"      # Emerald
PALETTE_WARNING = "#d97706"      # Amber
PALETTE_MUTED = "#64748b"        # Slate Gray
BACKGROUND_COLOR = "#ffffff"
GRID_COLOR = "#f1f5f9"


def setup_plot_style() -> None:
    """Set global Matplotlib and Seaborn style tokens."""
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({
        "figure.facecolor": BACKGROUND_COLOR,
        "axes.facecolor": BACKGROUND_COLOR,
        "axes.edgecolor": "#cbd5e1",
        "axes.grid": True,
        "grid.color": GRID_COLOR,
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "axes.labelsize": 11,
        "axes.labelweight": "bold",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.titlesize": 15,
        "figure.titleweight": "bold",
        "figure.autolayout": False,
    })


def ensure_dir(target_dir: Path) -> Path:
    """Ensure directory exists and return Path object."""
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def plot_total_consumption_timeseries(
    df_daily: pd.DataFrame, figures_dir: Path
) -> Path:
    """Plot daily all-India electricity consumption with 30-day moving average (2013-2024)."""
    fig, ax = plt.subplots(figsize=(14, 6), dpi=300)

    daily_valid = df_daily.dropna(subset=["Date", "Total Consumption"]).sort_values("Date")
    daily_valid["rolling_30"] = daily_valid["Total Consumption"].rolling(window=30, center=True).mean()

    # Raw daily line (light/muted)
    ax.plot(
        daily_valid["Date"],
        daily_valid["Total Consumption"],
        color=PALETTE_SECONDARY,
        alpha=0.35,
        linewidth=0.8,
        label="Daily Total Consumption (GWh/day)",
    )

    # 30-day rolling trend (bold)
    ax.plot(
        daily_valid["Date"],
        daily_valid["rolling_30"],
        color=PALETTE_PRIMARY,
        linewidth=2.2,
        label="30-Day Centered Moving Average",
    )

    # Annotate COVID-19 Dip
    covid_date = pd.to_datetime("2020-04-01")
    if daily_valid["Date"].min() <= covid_date <= daily_valid["Date"].max():
        ax.annotate(
            "COVID-19 Lockdown Dip\n(April 2020: ~2,589 GWh)",
            xy=(pd.to_datetime("2020-04-15"), 2600),
            xytext=(pd.to_datetime("2018-06-01"), 2300),
            arrowprops=dict(facecolor=PALETTE_ACCENT, shrink=0.08, width=1.5, headwidth=6),
            fontsize=9,
            fontweight="semibold",
            color=PALETTE_ACCENT,
            bbox=dict(boxstyle="round,pad=0.3", fc="#ffe4e6", ec=PALETTE_ACCENT, alpha=0.9),
        )

    # Annotate Peak
    max_idx = daily_valid["Total Consumption"].idxmax()
    peak_row = daily_valid.loc[max_idx]
    ax.annotate(
        f"All-Time Peak\n({peak_row['Date'].strftime('%d %b %Y')}: {peak_row['Total Consumption']:.1f} GWh)",
        xy=(peak_row["Date"], peak_row["Total Consumption"]),
        xytext=(peak_row["Date"] - pd.DateOffset(months=30), peak_row["Total Consumption"] + 150),
        arrowprops=dict(facecolor=PALETTE_SUCCESS, shrink=0.08, width=1.5, headwidth=6),
        fontsize=9,
        fontweight="semibold",
        color=PALETTE_SUCCESS,
        bbox=dict(boxstyle="round,pad=0.3", fc="#d1fae5", ec=PALETTE_SUCCESS, alpha=0.9),
    )

    ax.set_title("All-India Daily Electricity Consumption Trend (2013 – 2024)", pad=15)
    ax.set_xlabel("Year")
    ax.set_ylabel("Daily Electricity Consumption (GWh / Million Units)")
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(daily_valid["Date"].min(), daily_valid["Date"].max())
    ax.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)

    plt.tight_layout()
    output_path = figures_dir / "01_total_consumption_timeseries.png"
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_seasonal_monthly_pattern(
    df_pop: pd.DataFrame, figures_dir: Path
) -> Path:
    """Plot monthly seasonal consumption curve with variance band across all recorded years."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    seasonality = df_pop.groupby("Month")["Electricity_Consumption_GWh"].agg(["mean", "std", "min", "max"]).reset_index()
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Shaded ribbon of +/- 1 standard deviation
    ax.fill_between(
        seasonality["Month"],
        seasonality["mean"] - seasonality["std"],
        seasonality["mean"] + seasonality["std"],
        color=PALETTE_SECONDARY,
        alpha=0.2,
        label="± 1 Standard Deviation",
    )

    # Main seasonal curve
    ax.plot(
        seasonality["Month"],
        seasonality["mean"],
        marker="o",
        markersize=7,
        linewidth=2.5,
        color=PALETTE_PRIMARY,
        label="Mean State Monthly Consumption (GWh)",
    )

    # Annotate Summer Surge Peak
    peak_month = seasonality.loc[seasonality["mean"].idxmax()]
    ax.annotate(
        f"Peak Summer Demand (May)\nMean: {peak_month['mean']:.2f} GWh",
        xy=(peak_month["Month"], peak_month["mean"]),
        xytext=(peak_month["Month"] + 0.5, peak_month["mean"] + 0.15),
        arrowprops=dict(facecolor=PALETTE_ACCENT, shrink=0.08, width=1.5, headwidth=6),
        fontsize=9,
        fontweight="semibold",
        color=PALETTE_ACCENT,
        bbox=dict(boxstyle="round,pad=0.3", fc="#ffe4e6", ec=PALETTE_ACCENT, alpha=0.9),
    )

    ax.set_title("Seasonal Electricity Demand Profile Across Calendar Months", pad=15)
    ax.set_xlabel("Month of Year")
    ax.set_ylabel("Monthly Electricity Consumption (GWh)")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_labels)
    ax.legend(loc="lower right", frameon=True, facecolor="white")

    plt.tight_layout()
    output_path = figures_dir / "02_seasonal_monthly_pattern.png"
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_state_wise_consumption_ranking(
    state_rankings: Dict[str, Any], figures_dir: Path
) -> Path:
    """Horizontal bar chart comparing Top 10 and Bottom 10 states by average electricity consumption."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300, sharex=False)

    top_10 = state_rankings["top_10_consumption"].sort_values("mean_monthly_consumption_gwh", ascending=True)
    bottom_10 = state_rankings["bottom_10_consumption"].sort_values("mean_monthly_consumption_gwh", ascending=True)

    # Top 10 Bar Plot
    bars1 = ax1.barh(
        top_10["State_UT"],
        top_10["mean_monthly_consumption_gwh"],
        color=PALETTE_PRIMARY,
        edgecolor="#0f172a",
        height=0.65,
    )
    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{w:.1f} GWh", va="center", fontsize=9)
    ax1.set_title("Top 10 Consumers (Mean Monthly GWh)", fontsize=12)
    ax1.set_xlabel("Average Monthly Consumption (GWh)")
    ax1.set_xlim(0, top_10["mean_monthly_consumption_gwh"].max() * 1.18)

    # Bottom 10 Bar Plot
    bars2 = ax2.barh(
        bottom_10["State_UT"],
        bottom_10["mean_monthly_consumption_gwh"],
        color=PALETTE_SECONDARY,
        edgecolor="#0369a1",
        height=0.65,
    )
    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 0.003, bar.get_y() + bar.get_height() / 2, f"{w:.3f} GWh", va="center", fontsize=9)
    ax2.set_title("Bottom 10 Consumers / UTs (Mean Monthly GWh)", fontsize=12)
    ax2.set_xlabel("Average Monthly Consumption (GWh)")
    ax2.set_xlim(0, bottom_10["mean_monthly_consumption_gwh"].max() * 1.25)

    fig.suptitle("State and Union Territory Electricity Consumption Disparities (2012 – 2025)", y=1.02)
    plt.tight_layout()
    output_path = figures_dir / "03_state_wise_consumption_ranking.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_electricity_vs_population(
    df_pop: pd.DataFrame, figures_dir: Path
) -> Path:
    """Scatter plot with OLS trendline showing Electricity Consumption vs Population."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # State aggregated mean points for clean visualization
    state_means = (
        df_pop.groupby("State_UT")
        .agg(
            mean_pop=("Population_Million", "mean"),
            mean_cons=("Electricity_Consumption_GWh", "mean"),
        )
        .reset_index()
    )

    sns.regplot(
        data=state_means,
        x="mean_pop",
        y="mean_cons",
        ax=ax,
        scatter_kws={"color": PALETTE_PRIMARY, "alpha": 0.85, "s": 65, "edgecolor": "white"},
        line_kws={"color": PALETTE_ACCENT, "linewidth": 2.2, "label": "OLS Regression Trendline"},
    )

    # Label top states
    top_labels = state_means.sort_values("mean_pop", ascending=False).head(6)
    for _, row in top_labels.iterrows():
        ax.annotate(
            row["State_UT"],
            xy=(row["mean_pop"], row["mean_cons"]),
            xytext=(row["mean_pop"] + 3, row["mean_cons"] - 0.2),
            fontsize=8.5,
            fontweight="semibold",
            color="#1e293b",
        )

    # Compute correlation
    r = state_means["mean_pop"].corr(state_means["mean_cons"])
    r_sq = r ** 2

    stats_text = f"Pearson r = {r:.3f}\nR² = {r_sq:.3f}\nN = {len(state_means)} States/UTs"
    ax.text(
        0.05,
        0.92,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="medium",
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", fc="#f8fafc", ec="#cbd5e1", alpha=0.95),
    )

    ax.set_title("Relationship Between State Population and Electricity Consumption", pad=15)
    ax.set_xlabel("State Population (Millions)")
    ax.set_ylabel("Monthly Electricity Consumption (GWh)")
    ax.legend(loc="lower right", frameon=True, facecolor="white")

    plt.tight_layout()
    output_path = figures_dir / "04_electricity_vs_population.png"
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_electricity_vs_urbanization(
    df_urb: pd.DataFrame, figures_dir: Path
) -> Path:
    """Dual-panel chart examining Urbanization Rate against Consumption and Per Capita Use."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    state_urb = (
        df_urb.groupby("State_UT")
        .agg(
            mean_urb_rate=("Urbanization_Rate_pct", "mean"),
            mean_cons=("Electricity_Consumption_GWh", "mean"),
            mean_per_capita=("Electricity_Per_Capita_kWh", "mean"),
            mean_pop=("Population_Million", "mean"),
        )
        .reset_index()
    )

    # Panel 1: Urbanization Rate vs Monthly Consumption
    sns.regplot(
        data=state_urb,
        x="mean_urb_rate",
        y="mean_cons",
        ax=ax1,
        scatter_kws={"color": PALETTE_PRIMARY, "alpha": 0.8, "s": 60},
        line_kws={"color": PALETTE_ACCENT, "linewidth": 2},
    )
    r1 = state_urb["mean_urb_rate"].corr(state_urb["mean_cons"])
    ax1.set_title("Urbanization Rate vs State Total Electricity Consumption", fontsize=12)
    ax1.set_xlabel("Urbanization Rate (%)")
    ax1.set_ylabel("Monthly Electricity Consumption (GWh)")
    ax1.text(
        0.05, 0.92, f"Pearson r = {r1:.3f}",
        transform=ax1.transAxes,
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#cbd5e1"),
    )

    # Panel 2: Urbanization Rate vs Per Capita Use
    sns.regplot(
        data=state_urb,
        x="mean_urb_rate",
        y="mean_per_capita",
        ax=ax2,
        scatter_kws={"color": PALETTE_SECONDARY, "alpha": 0.8, "s": 60},
        line_kws={"color": PALETTE_SUCCESS, "linewidth": 2},
    )
    r2 = state_urb["mean_urb_rate"].corr(state_urb["mean_per_capita"])
    ax2.set_title("Urbanization Rate vs Per Capita Electricity Consumption", fontsize=12)
    ax2.set_xlabel("Urbanization Rate (%)")
    ax2.set_ylabel("Electricity Per Capita (kWh)")
    ax2.text(
        0.05, 0.92, f"Pearson r = {r2:.3f}",
        transform=ax2.transAxes,
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#cbd5e1"),
    )

    fig.suptitle("Impact of Urbanization on Electricity Dynamics (State Aggregates)", y=1.02)
    plt.tight_layout()
    output_path = figures_dir / "05_electricity_vs_urbanization.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_weather_vs_electricity(
    df_wx: pd.DataFrame, figures_dir: Path
) -> Path:
    """Four-panel scatter grid showing Weather indicators vs Electricity Consumption."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)

    weather_pairs = [
        ("Avg_Temperature_C", "Average Temperature (°C)", PALETTE_ACCENT, axes[0, 0]),
        ("Humidity_pct", "Relative Humidity (%)", PALETTE_SECONDARY, axes[0, 1]),
        ("Rainfall_mm", "Monthly Rainfall (mm)", PALETTE_PRIMARY, axes[1, 0]),
        ("Solar_Radiation_kWh_m2", "Solar Radiation (kWh/m²)", PALETTE_WARNING, axes[1, 1]),
    ]

    for col, label, color, ax in weather_pairs:
        sns.regplot(
            data=df_wx,
            x=col,
            y="Electricity_Consumption_GWh",
            ax=ax,
            scatter_kws={"color": color, "alpha": 0.25, "s": 15},
            line_kws={"color": "#0f172a", "linewidth": 2},
        )
        r = df_wx[col].corr(df_wx["Electricity_Consumption_GWh"])
        ax.set_title(f"{label} vs Consumption (r = {r:+.3f})", fontsize=11)
        ax.set_xlabel(label)
        ax.set_ylabel("Monthly Consumption (GWh)")

    fig.suptitle("Influence of Weather Parameters on Electricity Consumption", y=1.01)
    plt.tight_layout()
    output_path = figures_dir / "06_weather_vs_electricity_relationships.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_correlation_heatmap(
    df_wx: pd.DataFrame, figures_dir: Path
) -> Path:
    """High-resolution correlation heatmap across weather, demographic, and electricity variables."""
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)

    target_cols = [
        "Electricity_Consumption_GWh",
        "Electricity_Per_Capita_kWh",
        "Population_Million",
        "Population_Growth_pct",
        "Avg_Temperature_C",
        "Max_Temperature_C",
        "Min_Temperature_C",
        "Humidity_pct",
        "Rainfall_mm",
        "Wind_Speed_kmh",
        "Solar_Radiation_kWh_m2",
    ]
    valid_cols = [c for c in target_cols if c in df_wx.columns]
    corr_matrix = df_wx[valid_cols].corr()

    # Pretty column labels
    label_map = {
        "Electricity_Consumption_GWh": "Electricity (GWh)",
        "Electricity_Per_Capita_kWh": "Per Capita (kWh)",
        "Population_Million": "Population (M)",
        "Population_Growth_pct": "Pop Growth (%)",
        "Avg_Temperature_C": "Avg Temp (°C)",
        "Max_Temperature_C": "Max Temp (°C)",
        "Min_Temperature_C": "Min Temp (°C)",
        "Humidity_pct": "Humidity (%)",
        "Rainfall_mm": "Rainfall (mm)",
        "Wind_Speed_kmh": "Wind Speed (km/h)",
        "Solar_Radiation_kWh_m2": "Solar Rad (kWh/m²)",
    }
    renamed_corr = corr_matrix.rename(index=label_map, columns=label_map)

    mask = np.triu(np.ones_like(renamed_corr, dtype=bool))

    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(
        renamed_corr,
        mask=mask,
        cmap=cmap,
        vmax=1.0,
        vmin=-1.0,
        center=0,
        annot=True,
        fmt=".2f",
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation Coefficient (r)"},
        ax=ax,
    )

    ax.set_title("Correlation Heatmap: Demographic, Weather, and Electricity Metrics", pad=15)
    plt.tight_layout()
    output_path = figures_dir / "07_correlation_heatmap.png"
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def plot_annual_consumption_growth(
    daily_trends: Dict[str, Any], figures_dir: Path
) -> Path:
    """Dual-axis chart: Annual average daily consumption and Year-over-Year growth percentage."""
    fig, ax1 = plt.subplots(figsize=(12, 5.5), dpi=300)

    annual_stats = daily_trends.get("annual_stats")
    if annual_stats is None or annual_stats.empty:
        plt.close(fig)
        return figures_dir / "08_annual_consumption_growth.png"

    years = annual_stats["Year"].astype(int)
    mean_daily = annual_stats["mean_daily_gwh"]
    yoy_growth = annual_stats["yoy_growth_pct"]

    # Bar chart for consumption level
    color_bar = PALETTE_PRIMARY
    bars = ax1.bar(
        years,
        mean_daily,
        color=color_bar,
        alpha=0.85,
        width=0.55,
        edgecolor="#0f172a",
        label="Mean Daily Total Consumption (GWh/day)",
    )
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 50, f"{h:.0f}", ha="center", fontsize=8.5, fontweight="semibold")

    ax1.set_xlabel("Year")
    ax1.set_ylabel("Mean Daily Consumption (GWh / MU)", color=color_bar)
    ax1.tick_params(axis="y", labelcolor=color_bar)
    ax1.set_ylim(0, mean_daily.max() * 1.25)
    ax1.set_xticks(years)

    # Line chart for YoY Growth (%) on secondary axis
    ax2 = ax1.twinx()
    color_line = PALETTE_ACCENT
    ax2.plot(
        years,
        yoy_growth,
        color=color_line,
        marker="s",
        markersize=6,
        linewidth=2.2,
        label="YoY Growth Rate (%)",
    )
    for yr, g in zip(years, yoy_growth):
        if not np.isnan(g):
            ax2.text(yr, g + 0.6, f"{g:+.1f}%", ha="center", fontsize=8, color=color_line, fontweight="bold")

    ax2.axhline(0, color="#94a3b8", linestyle=":", linewidth=1.2)
    ax2.set_ylabel("Year-over-Year Growth Rate (%)", color=color_line)
    ax2.tick_params(axis="y", labelcolor=color_line)
    ax2.grid(False)  # Avoid overlapping grids

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, facecolor="white")

    ax1.set_title("Annual Electricity Consumption Growth and Trajectory (India: 2013 – 2024)", pad=15)
    plt.tight_layout()
    output_path = figures_dir / "08_annual_consumption_growth.png"
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def generate_all_visualizations(
    cleaned_dict: Dict[str, pd.DataFrame],
    analysis_dict: Dict[str, Any],
    figures_dir: Optional[Path | str] = None,
) -> List[Path]:
    """Generate and save all 8 publication-grade charts to the figures directory."""
    setup_plot_style()
    target_dir = ensure_dir(Path(figures_dir) if figures_dir else DEFAULT_FIGURES_DIR)
    generated_paths: List[Path] = []

    if "daily_consumption" in cleaned_dict:
        p1 = plot_total_consumption_timeseries(cleaned_dict["daily_consumption"], target_dir)
        generated_paths.append(p1)

    if "monthly_population" in cleaned_dict:
        p2 = plot_seasonal_monthly_pattern(cleaned_dict["monthly_population"], target_dir)
        generated_paths.append(p2)

        if "state_rankings" in analysis_dict:
            p3 = plot_state_wise_consumption_ranking(analysis_dict["state_rankings"], target_dir)
            generated_paths.append(p3)

        p4 = plot_electricity_vs_population(cleaned_dict["monthly_population"], target_dir)
        generated_paths.append(p4)

    if "monthly_urbanization" in cleaned_dict:
        p5 = plot_electricity_vs_urbanization(cleaned_dict["monthly_urbanization"], target_dir)
        generated_paths.append(p5)

    if "monthly_weather" in cleaned_dict:
        p6 = plot_weather_vs_electricity(cleaned_dict["monthly_weather"], target_dir)
        generated_paths.append(p6)

        p7 = plot_correlation_heatmap(cleaned_dict["monthly_weather"], target_dir)
        generated_paths.append(p7)

    if "daily_trends" in analysis_dict:
        p8 = plot_annual_consumption_growth(analysis_dict["daily_trends"], target_dir)
        generated_paths.append(p8)

    return generated_paths
