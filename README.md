# State Electricity Consumption Analysis and Visualization Using Python

An empirical, reproducible data analysis and visualization system investigating electricity consumption dynamics across Indian states and Union Territories, evaluating long-term temporal trajectories, seasonal patterns, and associations with population scale, urbanization, and weather factors.

---

## 1. Project Overview & Objectives

Electricity consumption serves as a vital barometer for economic vitality, regional development, and demographic shifts. This project conducts an end-to-end exploratory and statistical investigation using historical Indian electricity datasets spanning daily records (2013–2024) and monthly state-level panels (2012–2025).

### Primary Research Questions
1. **Long-Term Trajectory:** How has total electricity consumption evolved across India between 2013 and 2024, and what was the impact of macroeconomic shocks such as the 2020 COVID-19 lockdown?
2. **Seasonal Load Dynamics:** Are there pronounced monthly and seasonal fluctuations in electricity demand, and when do annual peak loads occur?
3. **Geographical Concentration:** Which states and Union Territories exhibit the highest and lowest electricity consumption, and what explains these cross-sectional disparities?
4. **Demographic Influence:** To what degree does state population explain variations in aggregate electricity consumption?
5. **Urbanization Association:** How does the urbanization rate (%) relate to total electricity consumption and per capita energy usage?
6. **Meteorological Drivers:** How strongly are ambient temperature, relative humidity, rainfall, and solar radiation correlated with electricity demand?

---

## 2. Technology Stack & Dependencies

- **Language:** Python `>= 3.14`
- **Data Manipulation & Computation:** [Pandas](https://pandas.pydata.org/) (`>= 3.0.6`), [NumPy](https://numpy.org/) (`>= 2.5.3`)
- **Data Visualization:** [Matplotlib](https://matplotlib.org/) (configured with non-interactive `Agg` backend), [Seaborn](https://seaborn.pydata.org/)
- **Package & Environment Management:** [uv](https://github.com/astral-sh/uv)
- **Interactive Exploration:** Jupyter Notebook format (`notebooks/*.ipynb`)
- **Quality Assurance & Testing:** Python `unittest` framework

---

## 3. Dataset Inventory

The project analyzes four CSV files located in `datasets/`, preserved in their original form without modification:

| File Name | Temporal Coverage | Dimensions | Granularity | Key Measured Indicators | Missing Values |
| :--- | :---: | :---: | :--- | :--- | :---: |
| `Indias_Electricity_Consumption_Dataset.csv` | Jan 2013 – Sep 2024 | 3,707 × 39 | Daily (National & State) | Daily electricity consumption across 36 regional grid entities and aggregate `Total Consumption` (GWh / MU) | Handled non-destructively; 6 missing days in Total |
| `electricity_vs_population_all_india_monthly_2012_2025.csv` | Jan 2012 – Dec 2025 | 6,048 × 7 | Monthly (36 States/UTs) | `Year`, `Month`, `State_UT`, `Population_Million`, `Population_Growth_pct`, `Electricity_Consumption_GWh`, `Electricity_Per_Capita_kWh` | 0 |
| `electricity_vs_urbanization_all_india_monthly_2012_2025.csv` | Jan 2012 – Dec 2025 | 6,048 × 9 | Monthly (36 States/UTs) | `Urban_Population_Million`, `Urbanization_Rate_pct`, `Urban_Population_Growth_pct`, `Electricity_Consumption_GWh` | 0 |
| `electricity_weather_population_all_india_monthly_2012_2025.csv` | Jan 2012 – Dec 2025 | 6,048 × 14 | Monthly (36 States/UTs) | `Avg_Temperature_C`, `Max_Temperature_C`, `Min_Temperature_C`, `Humidity_pct`, `Rainfall_mm`, `Wind_Speed_kmh`, `Solar_Radiation_kWh_m2` | 0 |

---

## 4. Project Directory Structure

```text
state-electricity-analysis/
├── datasets/                                 # Original read-only datasets
│   ├── Indias_Electricity_Consumption_Dataset.csv
│   ├── electricity_vs_population_all_india_monthly_2012_2025.csv
│   ├── electricity_vs_urbanization_all_india_monthly_2012_2025.csv
│   └── electricity_weather_population_all_india_monthly_2012_2025.csv
├── dashboard/                                # Ultra-premium interactive web dashboard
│   ├── index.html                            # Semantic HTML5 glassmorphic dashboard
│   ├── styles.css                            # Modern stylesheet with Dark/Light mode tokens
│   ├── app.js                                # Chart.js integrations & interactive controllers
│   ├── data.json                             # Compact serialized analytics dataset
│   └── figures/                              # Synced high-resolution publication PNGs
├── notebooks/                                # Interactive exploratory notebooks
│   ├── 01_data_audit.ipynb
│   ├── 02_data_cleaning.ipynb
│   └── 03_exploratory_analysis.ipynb
├── outputs/                                  # Automatically generated artifacts
│   ├── figures/                              # High-resolution PNG charts (300 DPI)
│   │   ├── 01_total_consumption_timeseries.png
│   │   ├── 02_seasonal_monthly_pattern.png
│   │   ├── 03_state_wise_consumption_ranking.png
│   │   ├── 04_electricity_vs_population.png
│   │   ├── 05_electricity_vs_urbanization.png
│   │   ├── 06_weather_vs_electricity_relationships.png
│   │   ├── 07_correlation_heatmap.png
│   │   └── 08_annual_consumption_growth.png
│   └── reports/                              # Automated markdown audit & findings reports
│       ├── data_audit_report.md
│       └── state_electricity_analysis_findings.md
├── src/
│   └── dvp_project/                          # Core analytical package modules
│       ├── __init__.py                       # Package exports and CLI entry mapping
│       ├── main.py                           # CLI pipeline runner (supports --dashboard)
│       ├── data_loader.py                    # Dataset resolution, loading, and audit
│       ├── cleaning.py                       # Non-destructive cleaning and reshaping
│       ├── analysis.py                       # Statistical calculations and correlations
│       ├── visualizations.py                 # Matplotlib & Seaborn chart rendering
│       ├── reports.py                        # Markdown audit & findings report generator
│       ├── dashboard_data.py                 # Dashboard data serialization engine
│       └── serve_dashboard.py                # Local dashboard web server launcher
├── tests/
│   └── test_data_checks.py                   # Automated unit and integration tests
├── pyproject.toml                            # Build system and project metadata
├── uv.lock                                   # Dependency lockfile
├── .python-version                           # Target Python specification (3.14)
├── .gitignore                                # Version control exclusions
└── README.md                                 # Project documentation
```

---

## 5. Setup & Installation Instructions

Ensure you have [uv](https://github.com/astral-sh/uv) installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/kanishkambk43/state-electricity-analysis.git
cd state-electricity-analysis
```

### 2. Synchronize environment & dependencies
```bash
uv sync
```

Alternatively, install the package in editable mode:
```bash
uv pip install -e . --no-deps
```

---

## 6. Execution Commands

### Run the Complete End-to-End Pipeline
Execute the full data loading, auditing, cleaning, statistical analysis, figure generation, and findings reporting workflow:
```bash
uv run dvp-project
```

Or execute directly through Python:
```bash
python -m dvp_project.main
```

### Launch the Interactive Web Dashboard
Start the local server and automatically open the interactive intelligence dashboard in your browser:
```bash
uv run dvp-project --dashboard
```
Or run directly with the Python server launcher:
```bash
uv run python -m dvp_project.serve_dashboard
```
Or open [`dashboard/index.html`](file:///c:/Users/Kanishka%20MBK/OneDrive/Desktop/dvp%20project/dashboard/index.html) directly.

### Run the Test Suite
Execute the 12 automated unit and integration tests covering data loading, error handling, date parsing, cleaning, calculations, and chart generation:
```bash
python -m unittest tests/test_data_checks.py
```

---

## 7. Generated Visualizations

All figures are automatically rendered in `outputs/figures/` with 300 DPI resolution using a publication-grade aesthetic palette:

| Figure File | Description | Core Insight Illustrated |
| :--- | :--- | :--- |
| `01_total_consumption_timeseries.png` | Daily all-India electricity consumption (2013–2024) with 30-day centered moving average. | Visualizes the secular upward consumption trend, the steep COVID-19 dip in April 2020 (~2,589 GWh), and the all-time peak of 5,460.7 GWh in June 2024. |
| `02_seasonal_monthly_pattern.png` | Monthly seasonal demand curve with standard deviation error band. | Highlights the summer peak in **May (3.61 GWh)** driven by extreme heat cooling demand, contrasting with winter lows in **February (3.02 GWh)**. |
| `03_state_wise_consumption_ranking.png` | Dual horizontal bar chart comparing Top 10 vs Bottom 10 states by average monthly consumption. | Demonstrates severe regional concentration: Uttar Pradesh (19.93 GWh) and Maharashtra (10.56 GWh) consume orders of magnitude more than small UTs like Lakshadweep (0.010 GWh). |
| `04_electricity_vs_population.png` | Scatter plot of State Population vs Electricity Consumption with OLS regression fit. | Demonstrates a near-perfect linear association ($r = +0.987, R^2 = 0.974$) confirming population scale as the primary driver of state power demand. |
| `05_electricity_vs_urbanization.png` | Dual-panel scatter plot evaluating Urbanization Rate (%) against total consumption and per capita usage. | Clarifies that small Union Territories (e.g. Chandigarh, Delhi) have high urbanization rates (>80-97%) but modest aggregate demand due to land area constraints. |
| `06_weather_vs_electricity_relationships.png` | Four-panel regression grid evaluating Temperature, Humidity, Rainfall, and Solar Radiation. | Confirms positive correlation with ambient temperature ($r = +0.291$) and negative correlation with humidity ($r = -0.220$) and rainfall ($r = -0.138$). |
| `07_correlation_heatmap.png` | Annotated correlation matrix across demographic, meteorological, and power indicators. | Provides an integrated correlation view across all continuous indicators with divergent color mapping. |
| `08_annual_consumption_growth.png` | Dual-axis chart of annual mean daily consumption (GWh/day) and Year-over-Year percentage change. | Displays uninterrupted long-term growth (+69.3% from 2013 to 2024), interrupted only by the 2020 pandemic contraction (-3.77%). |

---

## 8. Key Empirical Findings

From the statistical analyses computed directly on the real datasets:

1. **National Demand Trajectory (2013–2024):**
   - India's average daily electricity consumption expanded from **2,771.4 GWh/day** in 2013 to **4,693.3 GWh/day** in 2024 (+69.3% overall growth).
   - In 2020, daily consumption contracted by **-3.77% YoY** due to industrial lockdown mandates during COVID-19, followed by an aggressive rebound of **+10.48% YoY in 2021** and **+8.24% YoY in 2022**.
   - Peak daily national consumption reached **5,460.7 GWh/day** on June 18, 2024.

2. **Seasonal and Monthly Seasonality:**
   - Consumption reaches its annual maximum in **May (mean: 3.61 GWh/state)** and **April (3.41 GWh/state)**, corresponding to peak summer thermal loads and air conditioning demand.
   - The winter trough occurs in **February (3.02 GWh/state)** and **January (3.09 GWh/state)**.
   - Peak summer load represents a **~19.7% surge** over the winter baseline.

3. **State Disparities & Geographic Concentration:**
   - **Top 5 Consuming States:** Uttar Pradesh (19.93 GWh/month), Maharashtra (10.56 GWh/month), Bihar (10.45 GWh/month), West Bengal (8.08 GWh/month), and Madhya Pradesh (7.27 GWh/month).
   - **Bottom 5 Consumers / UTs:** Lakshadweep (0.010 GWh), Ladakh (0.029 GWh), Andaman & Nicobar Islands (0.038 GWh), Sikkim (0.057 GWh), and Dadra & Nagar Haveli and Daman & Diu (0.063 GWh).

4. **Demographics & Population Elasticity:**
   - State population is correlated with aggregate electricity consumption at **$r = +0.987$ ($R^2 = 0.974, p < 0.001$)**, confirming that population scale is the dominant predictor of state aggregate power requirements.

5. **Urbanization Observations:**
   - Total urban population exhibits strong positive correlation with electricity use ($r = +0.931$).
   - Urbanization rate (%) has a slightly negative correlation ($r = -0.147$) with total state consumption, as small Union Territories with high urbanization percentages (e.g. Chandigarh, Delhi) possess small land and aggregate demand bases relative to agricultural/industrial megastates.

6. **Meteorological Associations:**
   - **Temperature:** Statistically significant positive association with average temperature ($r = +0.291$), maximum temperature ($r = +0.288$), and minimum temperature ($r = +0.287$).
   - **Moisture & Precipitation:** Negative correlation with relative humidity ($r = -0.220$) and monthly rainfall ($r = -0.138$), as monsoon precipitation lowers ambient temperature and suppresses air conditioning demand.
   - **Solar Radiation and Wind:** Weak linear correlation ($r \approx -0.010$ and $r \approx -0.004$).

---

## 9. Limitations & Methodological Context

- **Observational Correlation vs. Causation:** Statistical correlations observed between electricity demand, weather, and urbanization indicate empirical association, not direct proof of causation. Unmeasured variables such as tariffs, transmission infrastructure, and industrial capacity also influence consumption.
- **Temporal Granularity:** Weather, urbanization, and population datasets are aggregated at monthly state intervals, whereas total national consumption is available daily.
- **Historical Data Sparsity:** In the daily dataset, several Union Territories (Puducherry, Tripura, Dadra & Nagar Haveli) lack complete reporting prior to 2018.

---

## 10. License & Attribution

This project is licensed under the MIT License. Developed for data visualization and exploratory analysis of India's state electricity consumption.
