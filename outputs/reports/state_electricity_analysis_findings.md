# State Electricity Consumption Analysis and Visualization Using Python

## Executive Summary & Research Report

**Author:** Data Analysis & Software Engineering Team  
**Analysis Framework:** Python (Pandas, NumPy, Matplotlib, Seaborn)  
**Execution Environment:** Reproducible UV-managed workflow  

---

## 1. Project Objective and Scope

The objective of this project is to conduct an empirical, reproducible investigation of electricity consumption across India.
Specifically, the analysis investigates:
1. **Long-Term Temporal Trajectory:** How electricity consumption has evolved annually and daily from 2012 to 2024/2025.
2. **Seasonal and Monthly Variations:** Whether distinct annual cycles emerge due to climatic shifts.
3. **Geographic and State Disparities:** Identifying top-consuming states versus low-consuming states and Union Territories.
4. **Demographic Relationship:** The empirical association between state population size and electricity demand.
5. **Urbanization Association:** How urban population share relates to total and per-capita electricity consumption.
6. **Climatic and Meteorological Drivers:** The influence of temperature, humidity, rainfall, and solar radiation on power consumption.

---

## 2. Dataset Inventory and Data Cleaning Summary

The project analyzes four primary datasets provided in `datasets/`:

| Dataset | Granularity | Period | Key Attributes | Missing Values |
| :--- | :--- | :--- | :--- | :--- |
| `Indias_Electricity_Consumption_Dataset.csv` | Daily (National & State) | 2013-01 to 2024-09 | Dates, 36 State columns, Total Consumption | Handled non-destructively; 6 missing in Total |
| `electricity_vs_population_all_india_monthly_2012_2025.csv` | Monthly (State Panel) | 2012-01 to 2025-12 | Year, Month, State_UT, Population, Consumption_GWh, Per_Capita_kWh | 0 |
| `electricity_vs_urbanization_all_india_monthly_2012_2025.csv` | Monthly (State Panel) | 2012-01 to 2025-12 | Urban_Population, Urbanization_Rate_pct, Consumption_GWh | 0 |
| `electricity_weather_population_all_india_monthly_2012_2025.csv` | Monthly (State Panel) | 2012-01 to 2025-12 | Temp, Humidity, Rainfall, Wind, Solar Rad, Consumption_GWh | 0 |

### Cleaning Methodology:
- **Preservation of Raw Records:** Original CSV files were loaded in read-only mode and left unmodified.
- **Datetime Harmonization:** Daily string dates were parsed to ISO 8601 timestamps; monthly records received standardized `Date` timestamps for chronological panel analysis.
- **Type Normalization:** String artifacts and indices were scrubbed; numeric attributes were cast to rigorous 64-bit floating point representations.
- **Dimensional Reshaping:** Wide daily state columns were formatted for cross-sectional and temporal aggregations without loss of context.

---

## 3. Empirical Findings & Statistical Analysis

### 3.1 Long-Term Electricity Consumption Trajectory (2013 – 2024)

- **Historical Mean Daily Consumption:** 3,555.7 GWh/day across 3,701 recorded operational days.
- **Range:** Minimum recorded daily consumption was 2,460.5 GWh/day (2014-07-13); all-time peak reached 5,460.7 GWh/day (2024-06-18).

#### Annual Average Daily Consumption and Growth Rates:

| Year | Mean Daily Consumption (GWh/day) | Min Daily (GWh) | Max Daily (GWh) | YoY Growth (%) |
| :---: | :---: | :---: | :---: | :---: |
| 2013 | 2,771.4 | 2,568.8 | 3,040.3 | Baseline |
| 2014 | 2,902.6 | 2,460.5 | 3,156.8 | +4.74% |
| 2015 | 3,011.0 | 2,494.4 | 3,363.5 | +3.73% |
| 2016 | 3,128.4 | 2,812.1 | 3,535.7 | +3.90% |
| 2017 | 3,279.6 | 2,805.8 | 3,642.5 | +4.83% |
| 2018 | 3,504.1 | 3,059.6 | 3,926.4 | +6.84% |
| 2019 | 3,547.3 | 2,631.5 | 4,139.7 | +1.23% |
| 2020 | 3,413.4 | 2,589.0 | 3,952.0 | -3.77% |
| 2021 | 3,771.0 | 2,943.0 | 4,503.8 | +10.48% |
| 2022 | 4,081.7 | 3,127.5 | 4,717.3 | +8.24% |
| 2023 | 4,447.4 | 3,466.6 | 5,224.3 | +8.96% |
| 2024 | 4,693.3 | 4,057.6 | 5,460.7 | +5.53% |

> **Key Observation:** India's daily electricity consumption expanded from an average of ~2,771 GWh/day in 2013 to ~4,693 GWh/day in 2024 (+69.3% overall growth).
> A sharp contraction occurred in **2020 (-3.77% YoY)** as a direct result of COVID-19 industrial containment measures, followed by a strong post-pandemic rebound in 2021 (+10.48%) and 2022 (+8.24%).

---

### 3.2 Monthly Seasonality and Peak Load Timing

An analysis of monthly consumption reveals significant seasonal periodicity:
- **Peak Demand Month:** **May** records the highest mean monthly consumption (**3.61 GWh/month** at the state aggregate level), followed by **April (3.41 GWh)** and **June (3.32 GWh)**.
- **Trough Demand Month:** **February (3.02 GWh)** and **January (3.09 GWh)** exhibit the lowest consumption rates.
- **Summer Surge Factor:** May consumption is ~19.7% higher than the winter minimum in February, driven primarily by space cooling and agricultural irrigation demand.

---

### 3.3 State-Wise Consumption Disparities

Cross-sectional state analysis highlights extreme geographic concentration:

#### Top 5 Electricity Consuming States (Mean Monthly):
1. **Uttar Pradesh:** 19.93 GWh/month (Mean Population: ~230.5M)
2. **Maharashtra:** 10.56 GWh/month (Mean Population: ~120.4M)
3. **Bihar:** 10.45 GWh/month (Mean Population: ~121.4M)
4. **West Bengal:** 8.08 GWh/month (Mean Population: ~93.6M)
5. **Madhya Pradesh:** 7.27 GWh/month (Mean Population: ~83.9M)

#### Bottom 5 Electricity Consuming States/UTs:
1. **Lakshadweep:** 0.010 GWh/month
2. **Ladakh:** 0.029 GWh/month
3. **Andaman and Nicobar Islands:** 0.038 GWh/month
4. **Sikkim:** 0.057 GWh/month
5. **Dadra & Nagar Haveli and Daman & Diu:** 0.063 GWh/month

---

### 3.4 Demographic Relationship (Population vs Electricity)

- **Pearson Correlation Coefficient ($r$):** **+0.987** ($p < 0.001$)
- **Coefficient of Determination ($R^2$):** **0.974**
- **Interpretation:** State population scale accounts for approximately 97.4% of the variance in aggregate state electricity consumption. Population scale is the dominant structural determinant of overall power requirements.

---

### 3.5 Urbanization Dynamics

- **Total Urban Population vs Consumption:** Strong positive correlation ($r = +0.931$).
- **Urbanization Rate (%) vs Total Consumption:** Mild negative correlation ($r = -0.147$).
- **Urbanization Rate (%) vs Per Capita Consumption:** Negative correlation ($r = -0.040$).
> **Contextual Nuance:** The slight negative association between urbanization percentage and total state consumption is an artifact of high-urbanization, low-population Union Territories (e.g., Chandigarh at >97% urbanization and Delhi) possessing smaller aggregate geographical footprints than agricultural megastates.

---

### 3.6 Weather Variables and Electricity Associations

Correlation analysis between meteorological variables and monthly electricity consumption yields:

| Weather Indicator | Pearson $r$ with Electricity (GWh) | Direction | Nature of Association |
| :--- | :---: | :---: | :--- |
| **Average Temperature (°C)** | **+0.291** | Positive | Increased cooling load during hot periods |
| **Maximum Temperature (°C)** | **+0.288** | Positive | Daytime peak air-conditioning surge |
| **Minimum Temperature (°C)** | **+0.287** | Positive | Elevated night-time cooling requirements |
| **Relative Humidity (%)** | **-0.220** | Negative | Overlaps with monsoon cooler intervals |
| **Rainfall (mm)** | **-0.138** | Negative | Rain episodes suppress outdoor temperatures |
| **Solar Radiation (kWh/m²)** | **-0.010** | Negligible | Near-zero linear association with grid draw |
| **Wind Speed (km/h)** | **-0.004** | Negligible | Negligible direct correlation |

> **Methodological Warning:** Correlations reflect empirical association and do not constitute proof of causation. Unobserved macroeconomic variables (e.g., industrial production, tariffs, transmission capacity) also influence electricity consumption.

---

## 4. Key Visualizations Generated

The automated visualization engine generated 8 publication-grade charts under `outputs/figures/`:

1. `01_total_consumption_timeseries.png`: Long-term daily consumption trend (2013-2024) highlighting the 2020 COVID shock and peak records.
2. `02_seasonal_monthly_pattern.png`: Calendar month seasonal curve with standard deviation variance bands.
3. `03_state_wise_consumption_ranking.png`: Comparative horizontal rankings of Top 10 and Bottom 10 consuming states.
4. `04_electricity_vs_population.png`: Population vs Electricity scatter plot with regression fit ($R^2 = 0.974$).
5. `05_electricity_vs_urbanization.png`: Dual-panel scatter plot evaluating urbanization rate against aggregate and per-capita metrics.
6. `06_weather_vs_electricity_relationships.png`: Four-panel regression grid evaluating temperature, humidity, rainfall, and solar radiation.
7. `07_correlation_heatmap.png`: High-density annotated correlation heatmap covering all demographic, meteorological, and electrical variables.
8. `08_annual_consumption_growth.png`: Dual-axis annual trajectory and YoY percentage change bar-line plot.

---

## 5. Limitations and Recommendations for Future Research

1. **Observational Nature:** All analyses are observational. Causality cannot be inferred without causal inference methods (e.g., instrumental variables or panel fixed effects).
2. **Granularity Harmonization:** Daily data is provided at the all-India and wide-column state level, while weather and urbanization variables are provided as monthly panels. Merging these at a daily resolution would require daily weather station inputs.
3. **Missing Values in Historic UTs:** The daily dataset contains sparse historical coverage for DNH, Daman & Diu, and Pondicherry prior to 2018.
4. **Per Capita Metric Units:** Per-capita consumption columns exhibit scaling differences between the urbanization and weather files (e.g., annual vs monthly kWh scaling), requiring careful unit documentation.
