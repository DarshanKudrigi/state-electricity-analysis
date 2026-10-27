# Data Audit Report: State Electricity Analysis

**Generated:** Automatically by `dvp_project.reports`  
**Scope:** Inspection of all original CSV datasets in `datasets/`  

---

## 1. Executive Inventory Summary

| Dataset Identifier | Rows | Columns | Missing Cells | Duplicates | Date Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `daily_consumption` | 3,707 | 39 | 5,791 | 0 | 2013-01-06 to 2024-09-29 |
| `monthly_population` | 6,048 | 7 | 0 | 0 | 2012-01 to 2025-12 |
| `monthly_urbanization` | 6,048 | 9 | 0 | 0 | 2012-01 to 2025-12 |
| `monthly_weather` | 6,048 | 14 | 0 | 0 | 2012-01 to 2025-12 |

---

## 2. Dataset-by-Dataset Detailed Findings

### `daily_consumption`

- **File Dimensions:** 3,707 rows × 39 columns
- **Duplicate Rows:** 0
- **Missing Value Occurrences:** 5791
- **Columns with Missing Data:**
  - `DD`: 707 missing (19.07%)
  - `DNH`: 712 missing (19.21%)
  - `Essar steel`: 532 missing (14.35%)
  - `Meghalaya`: 14 missing (0.38%)
  - `Pondy`: 2,078 missing (56.06%)
  - `Tripura`: 1,742 missing (46.99%)
  - `Total Consumption`: 6 missing (0.16%)
- **Column Schema & Types:**
  - `Unnamed: 0`: `int64`
  - `Dates`: `str`
  - `Andhra Pradesh`: `float64`
  - `Arunachal Pradesh`: `float64`
  - `Assam`: `float64`
  - `Bihar`: `float64`
  - `Chandigarh`: `float64`
  - `Chhattisgarh`: `float64`
  - `DD`: `float64`
  - `Delhi`: `float64`
  - `DNH`: `float64`
  - `DVC`: `float64`
  - `Essar steel`: `float64`
  - `Goa`: `float64`
  - `Gujarat`: `float64`
  - *... and 24 additional state/UT columns.*

### `monthly_population`

- **File Dimensions:** 6,048 rows × 7 columns
- **Duplicate Rows:** 0
- **Missing Value Occurrences:** 0
- **Data Completeness:** 100% complete across all attributes (0 missing values).
- **Column Schema & Types:**
  - `Year`: `int64`
  - `Month`: `int64`
  - `State_UT`: `str`
  - `Population_Million`: `float64`
  - `Population_Growth_pct`: `float64`
  - `Electricity_Consumption_GWh`: `float64`
  - `Electricity_Per_Capita_kWh`: `float64`

### `monthly_urbanization`

- **File Dimensions:** 6,048 rows × 9 columns
- **Duplicate Rows:** 0
- **Missing Value Occurrences:** 0
- **Data Completeness:** 100% complete across all attributes (0 missing values).
- **Column Schema & Types:**
  - `Year`: `int64`
  - `Month`: `int64`
  - `State_UT`: `str`
  - `Population_Million`: `float64`
  - `Urban_Population_Million`: `float64`
  - `Urbanization_Rate_pct`: `float64`
  - `Urban_Population_Growth_pct`: `float64`
  - `Electricity_Consumption_GWh`: `float64`
  - `Electricity_Per_Capita_kWh`: `float64`

### `monthly_weather`

- **File Dimensions:** 6,048 rows × 14 columns
- **Duplicate Rows:** 0
- **Missing Value Occurrences:** 0
- **Data Completeness:** 100% complete across all attributes (0 missing values).
- **Column Schema & Types:**
  - `Year`: `int64`
  - `Month`: `int64`
  - `State_UT`: `str`
  - `Avg_Temperature_C`: `float64`
  - `Max_Temperature_C`: `float64`
  - `Min_Temperature_C`: `float64`
  - `Humidity_pct`: `float64`
  - `Rainfall_mm`: `float64`
  - `Wind_Speed_kmh`: `float64`
  - `Solar_Radiation_kWh_m2`: `float64`
  - `Population_Million`: `float64`
  - `Population_Growth_pct`: `float64`
  - `Electricity_Consumption_GWh`: `float64`
  - `Electricity_Per_Capita_kWh`: `float64`

---

## 3. Data Integrity and Suitability Assessment

1. **Granularity Differences:**
   - `daily_consumption` (`Indias_Electricity_Consumption_Dataset.csv`) contains daily time-series from **January 2013 to September 2024** across 36 regional grid entities and aggregate `Total Consumption`.
   - The three monthly series (`electricity_vs_population`, `electricity_vs_urbanization`, `electricity_weather_population`) provide state-by-state monthly panels spanning **January 2012 to December 2025** (168 months across 36 states and Union Territories).
2. **Missing Value Characteristics:**
   - In the daily dataset, certain historical territories or entities (e.g., `Pondy`, `Tripura`, `DD`, `DNH`, `Essar steel`) exhibit missing entries in earlier periods. The aggregate `Total Consumption` column has 6 missing days.
   - In contrast, the three monthly panels are fully populated with zero missing cells across all 6,048 observations.
3. **Suitability for Analytical Modeling:**
   - The daily series is ideal for temporal trend decomposition, seasonality analysis, and macro-level shocks (such as the 2020 COVID-19 lockdown).
   - The monthly series are ideal for examining cross-sectional state disparities, population-demand elasticity, urbanization dynamics, and weather-driven seasonal swings.
