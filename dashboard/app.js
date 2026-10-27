/**
 * State Electricity Intelligence Dashboard - Client Logic
 */

let DASHBOARD_DATA = null;
let charts = {};
let currentTheme = "dark";
let showingTopStates = true;

// DOM Elements
document.addEventListener("DOMContentLoaded", async () => {
  initTheme();
  setupTabNavigation();
  setupModal();
  setupRefreshButton();
  await loadData();
});

/* ==========================================================================
   1. Theme Management
   ========================================================================== */
function initTheme() {
  const savedTheme = localStorage.getItem("dvp_theme") || "dark";
  setTheme(savedTheme);

  const toggleBtn = document.getElementById("themeToggleBtn");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      setTheme(nextTheme);
      updateChartTheme();
    });
  }
}

function setTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("dvp_theme", theme);
}

function updateChartTheme() {
  const isDark = currentTheme === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)";
  const textColor = isDark ? "#94a3b8" : "#475569";

  Object.values(charts).forEach((chart) => {
    if (chart && chart.options && chart.options.scales) {
      if (chart.options.scales.x) {
        chart.options.scales.x.grid.color = gridColor;
        chart.options.scales.x.ticks.color = textColor;
      }
      if (chart.options.scales.y) {
        chart.options.scales.y.grid.color = gridColor;
        chart.options.scales.y.ticks.color = textColor;
      }
      if (chart.options.scales.y1) {
        chart.options.scales.y1.grid.color = gridColor;
        chart.options.scales.y1.ticks.color = textColor;
      }
      chart.update();
    }
  });
}

/* ==========================================================================
   2. Tab Navigation
   ========================================================================== */
function setupTabNavigation() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTabId = btn.getAttribute("data-tab");

      tabButtons.forEach((b) => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      document.querySelectorAll(".tab-content").forEach((panel) => {
        panel.classList.remove("active");
      });

      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      const targetPanel = document.getElementById(targetTabId);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }

      // Trigger resize on visible charts
      setTimeout(() => {
        Object.values(charts).forEach((c) => c && c.resize && c.resize());
      }, 50);
    });
  });
}

/* ==========================================================================
   3. Data Loading & Initialization
   ========================================================================== */
async function loadData() {
  try {
    const response = await fetch("data.json");
    if (!response.ok) {
      throw new Error(`Failed to load data.json: HTTP ${response.status}`);
    }
    DASHBOARD_DATA = await response.json();
    renderDashboard(DASHBOARD_DATA);
  } catch (error) {
    console.error("Error loading dashboard data:", error);
    // Fallback if opened via file:// protocol
    alert("Could not load data.json directly via file protocol. Please run via local server: python -m dvp_project.serve_dashboard or python -m http.server.");
  }
}

function setupRefreshButton() {
  const btn = document.getElementById("refreshDataBtn");
  if (btn) {
    btn.addEventListener("click", async () => {
      btn.classList.add("loading");
      await loadData();
      btn.classList.remove("loading");
    });
  }
}

function renderDashboard(data) {
  renderKPIs(data.kpis);
  initDailyTimeseriesChart(data.daily_series);
  initAnnualGrowthChart(data.annual_data);
  initSeasonalityChart(data.monthly_data);
  initStateRankingChart(data.states_list);
  initStateSelector(data.states_list, data.state_drilldown);
  renderStatesTable(data.states_list);
  renderWeatherCorrelations(data.weather_table);
  initWeatherScatterChart(data.states_list);
  initUrbanCharts(data.states_list);
  renderGallery(data.figures_catalog);
  renderExecutiveReport();
}

/* ==========================================================================
   4. KPI Rendering
   ========================================================================== */
function renderKPIs(kpis) {
  if (!kpis) return;
  document.getElementById("valMeanDaily").innerText = kpis.overall_mean_daily_gwh.toLocaleString();
  document.getElementById("valPeakDemand").innerText = kpis.overall_peak_daily_gwh.toLocaleString();
  document.getElementById("valPopCorr").innerText = "+" + kpis.pop_correlation_r.toFixed(3);
  document.getElementById("valSummerSurge").innerText = "+" + kpis.summer_surge_pct.toFixed(1) + "%";
}

/* ==========================================================================
   5. Chart.js Renderers
   ========================================================================== */
function getCommonChartOptions(titleText, yAxisLabel) {
  const isDark = currentTheme === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)";
  const textColor = isDark ? "#94a3b8" : "#475569";

  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 600 },
    plugins: {
      legend: {
        labels: { color: textColor, font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 500 } }
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.9)",
        titleFont: { family: "'Outfit', sans-serif", size: 13, weight: 700 },
        bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
        padding: 10,
        cornerRadius: 8,
      }
    },
    scales: {
      x: {
        grid: { color: gridColor },
        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } }
      },
      y: {
        title: { display: !!yAxisLabel, text: yAxisLabel, color: textColor, font: { size: 12, weight: 600 } },
        grid: { color: gridColor },
        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } }
      }
    }
  };
}

// 5.1 Daily Time Series
function initDailyTimeseriesChart(series) {
  const ctx = document.getElementById("dailyTimeseriesChart")?.getContext("2d");
  if (!ctx || !series) return;

  const labels = series.map((d) => d.date);
  const rawData = series.map((d) => d.val);
  const trendData = series.map((d) => d.trend);

  if (charts.dailyTimeseries) charts.dailyTimeseries.destroy();

  charts.dailyTimeseries = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Daily Consumption (GWh)",
          data: rawData,
          borderColor: "rgba(14, 165, 233, 0.4)",
          backgroundColor: "transparent",
          borderWidth: 1,
          pointRadius: 0,
        },
        {
          label: "30-Day Moving Average",
          data: trendData,
          borderColor: "#0284c7",
          backgroundColor: "rgba(2, 132, 199, 0.08)",
          borderWidth: 2.5,
          pointRadius: 0,
          fill: true,
          tension: 0.2,
        }
      ]
    },
    options: getCommonChartOptions("", "GWh / Day")
  });
}

// 5.2 Annual Growth Chart
function initAnnualGrowthChart(annualData) {
  const ctx = document.getElementById("annualGrowthChart")?.getContext("2d");
  if (!ctx || !annualData) return;

  const labels = annualData.map((d) => d.year);
  const meanVals = annualData.map((d) => d.mean_daily);
  const growthVals = annualData.map((d) => d.yoy_growth);

  if (charts.annualGrowth) charts.annualGrowth.destroy();

  const options = getCommonChartOptions("", "Mean Daily GWh");
  options.scales.y1 = {
    position: "right",
    title: { display: true, text: "YoY Growth (%)", color: "#f43f5e", font: { size: 12, weight: 600 } },
    grid: { drawOnChartArea: false },
    ticks: { color: "#f43f5e" }
  };

  charts.annualGrowth = new Chart(ctx, {
    data: {
      labels: labels,
      datasets: [
        {
          type: "bar",
          label: "Mean Daily Total (GWh)",
          data: meanVals,
          backgroundColor: "#1e3a8a",
          borderRadius: 6,
          yAxisID: "y",
        },
        {
          type: "line",
          label: "YoY Growth Rate (%)",
          data: growthVals,
          borderColor: "#f43f5e",
          backgroundColor: "#f43f5e",
          borderWidth: 2.5,
          pointRadius: 5,
          yAxisID: "y1",
        }
      ]
    },
    options: options
  });
}

// 5.3 Monthly Seasonality Chart
function initSeasonalityChart(monthlyData) {
  const ctx = document.getElementById("seasonalityChart")?.getContext("2d");
  if (!ctx || !monthlyData) return;

  const labels = monthlyData.map((d) => d.month_name);
  const gwhVals = monthlyData.map((d) => d.mean_gwh);

  if (charts.seasonality) charts.seasonality.destroy();

  charts.seasonality = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Mean State Monthly Consumption (GWh)",
          data: gwhVals,
          borderColor: "#0284c7",
          backgroundColor: "rgba(14, 165, 233, 0.12)",
          borderWidth: 3,
          pointBackgroundColor: "#0284c7",
          pointRadius: 5,
          pointHoverRadius: 8,
          fill: true,
          tension: 0.3,
        }
      ]
    },
    options: getCommonChartOptions("", "Monthly Consumption (GWh)")
  });
}

// 5.4 State Ranking Bar Chart
function initStateRankingChart(states) {
  const ctx = document.getElementById("stateRankingChart")?.getContext("2d");
  if (!ctx || !states) return;

  const btnTop = document.getElementById("btnShowTop");
  const btnBottom = document.getElementById("btnShowBottom");

  function updateRankingData(showTop) {
    showingTopStates = showTop;
    btnTop?.classList.toggle("active", showTop);
    btnBottom?.classList.toggle("active", !showTop);

    const slice = showTop ? states.slice(0, 10) : states.slice(-10).reverse();
    const labels = slice.map((s) => s.name);
    const dataVals = slice.map((s) => s.mean_consumption_gwh);

    if (charts.stateRanking) charts.stateRanking.destroy();

    charts.stateRanking = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Mean Monthly (GWh)",
            data: dataVals,
            backgroundColor: showTop ? "#0ea5e9" : "#6366f1",
            borderRadius: 6,
          }
        ]
      },
      options: {
        indexAxis: "y",
        ...getCommonChartOptions("", "GWh")
      }
    });
  }

  btnTop?.addEventListener("click", () => updateRankingData(true));
  btnBottom?.addEventListener("click", () => updateRankingData(false));

  updateRankingData(true);
}

// 5.5 State Historical Drill-down
function initStateSelector(states, drilldown) {
  const selector = document.getElementById("stateSelector");
  if (!selector || !states) return;

  // Populate options
  selector.innerHTML = states
    .map((s) => `<option value="${s.name}">${s.name} (${s.mean_consumption_gwh.toFixed(2)} GWh)</option>`)
    .join("");

  function onStateChange(stName) {
    const stObj = states.find((s) => s.name === stName);
    const stHist = drilldown ? drilldown[stName] : null;

    // Update Quick Stats Pill
    const statsDiv = document.getElementById("stateQuickStats");
    if (statsDiv && stObj) {
      statsDiv.innerHTML = `
        <span class="stat-pill">Mean: <strong>${stObj.mean_consumption_gwh.toFixed(2)} GWh</strong></span>
        <span class="stat-pill">Per Capita: <strong>${stObj.mean_per_capita_kwh.toFixed(0)} kWh</strong></span>
        <span class="stat-pill">Pop: <strong>${stObj.population_million.toFixed(1)}M</strong></span>
        <span class="stat-pill">Urban: <strong>${stObj.urbanization_rate_pct.toFixed(1)}%</strong></span>
      `;
    }

    const titleEl = document.getElementById("stateDrilldownTitle");
    if (titleEl) titleEl.innerText = `${stName}: Annual Progression`;

    // Render Chart
    const ctx = document.getElementById("stateHistoryChart")?.getContext("2d");
    if (!ctx || !stHist) return;

    if (charts.stateHistory) charts.stateHistory.destroy();

    charts.stateHistory = new Chart(ctx, {
      type: "line",
      data: {
        labels: stHist.annual.map((d) => d.year),
        datasets: [
          {
            label: `${stName} (GWh)`,
            data: stHist.annual.map((d) => d.val),
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.12)",
            borderWidth: 2.5,
            pointRadius: 4,
            fill: true,
            tension: 0.2,
          }
        ]
      },
      options: getCommonChartOptions("", "Monthly Mean (GWh)")
    });
  }

  selector.addEventListener("change", (e) => onStateChange(e.target.value));

  // Init with first state
  if (states.length > 0) {
    onStateChange(states[0].name);
  }
}

// 5.6 Climate Scatter Chart
function initWeatherScatterChart(states) {
  const ctx = document.getElementById("weatherScatterChart")?.getContext("2d");
  if (!ctx || !states) return;

  const points = states.map((s) => ({ x: s.avg_temp_c, y: s.mean_consumption_gwh, label: s.name }));

  if (charts.weatherScatter) charts.weatherScatter.destroy();

  charts.weatherScatter = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "States / UTs",
          data: points,
          backgroundColor: "#f43f5e",
          pointRadius: 6,
          pointHoverRadius: 9,
        }
      ]
    },
    options: {
      ...getCommonChartOptions("", "Consumption (GWh)"),
      scales: {
        x: {
          title: { display: true, text: "Average Temperature (°C)" }
        },
        y: {
          title: { display: true, text: "Monthly Consumption (GWh)" }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.raw.label}: ${ctx.raw.x}°C, ${ctx.raw.y} GWh`
          }
        }
      }
    }
  });
}

// 5.7 Urbanization Charts
function initUrbanCharts(states) {
  const ctx1 = document.getElementById("urbanScatterChart")?.getContext("2d");
  const ctx2 = document.getElementById("urbanPerCapitaChart")?.getContext("2d");
  if (!states) return;

  const pointsCons = states.map((s) => ({ x: s.urbanization_rate_pct, y: s.mean_consumption_gwh, label: s.name }));
  const pointsPerCapita = states.map((s) => ({ x: s.urbanization_rate_pct, y: s.mean_per_capita_kwh, label: s.name }));

  if (ctx1) {
    if (charts.urbanScatter) charts.urbanScatter.destroy();
    charts.urbanScatter = new Chart(ctx1, {
      type: "scatter",
      data: {
        datasets: [{ label: "Urban Rate vs GWh", data: pointsCons, backgroundColor: "#0284c7", pointRadius: 5 }]
      },
      options: {
        ...getCommonChartOptions("", "Consumption (GWh)"),
        scales: {
          x: { title: { display: true, text: "Urbanization Rate (%)" } },
          y: { title: { display: true, text: "Monthly GWh" } }
        },
        plugins: {
          tooltip: { callbacks: { label: (c) => `${c.raw.label}: ${c.raw.x}%, ${c.raw.y} GWh` } }
        }
      }
    });
  }

  if (ctx2) {
    if (charts.urbanPerCapita) charts.urbanPerCapita.destroy();
    charts.urbanPerCapita = new Chart(ctx2, {
      type: "scatter",
      data: {
        datasets: [{ label: "Urban Rate vs Per Capita (kWh)", data: pointsPerCapita, backgroundColor: "#10b981", pointRadius: 5 }]
      },
      options: {
        ...getCommonChartOptions("", "Per Capita (kWh)"),
        scales: {
          x: { title: { display: true, text: "Urbanization Rate (%)" } },
          y: { title: { display: true, text: "Per Capita (kWh)" } }
        },
        plugins: {
          tooltip: { callbacks: { label: (c) => `${c.raw.label}: ${c.raw.x}%, ${c.raw.y} kWh` } }
        }
      }
    });
  }
}

/* ==========================================================================
   6. Table Renderers
   ========================================================================== */
function renderStatesTable(states) {
  const tbody = document.getElementById("statesTableBody");
  const searchInput = document.getElementById("stateSearchInput");
  if (!tbody || !states) return;

  function buildRows(filtered) {
    tbody.innerHTML = filtered
      .map(
        (s) => `
      <tr>
        <td><strong>${s.name}</strong></td>
        <td class="num-col">${s.mean_consumption_gwh.toFixed(3)}</td>
        <td class="num-col">${s.mean_per_capita_kwh.toFixed(1)}</td>
        <td class="num-col">${s.population_million.toFixed(2)}</td>
        <td class="num-col">${s.urbanization_rate_pct.toFixed(2)}%</td>
        <td class="num-col">${s.avg_temp_c.toFixed(1)}°C</td>
      </tr>
    `
      )
      .join("");
  }

  buildRows(states);

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = states.filter((s) => s.name.toLowerCase().includes(q));
      buildRows(filtered);
    });
  }
}

function renderWeatherCorrelations(tableData) {
  const tbody = document.getElementById("weatherTableBody");
  if (!tbody || !tableData) return;

  tbody.innerHTML = tableData
    .map(
      (r) => `
    <tr>
      <td><strong>${r.variable}</strong></td>
      <td class="num-col"><strong>${r.corr > 0 ? "+" : ""}${r.corr.toFixed(3)}</strong></td>
      <td><span class="badge-${r.corr > 0.1 ? "accent" : r.corr < -0.1 ? "info" : "neutral"}">${r.direction}</span></td>
      <td>${r.effect}</td>
    </tr>
  `
    )
    .join("");
}

/* ==========================================================================
   7. Publication Figures Gallery & Modal
   ========================================================================== */
function renderGallery(catalog) {
  const container = document.getElementById("figuresGallery");
  if (!container || !catalog) return;

  container.innerHTML = catalog
    .map(
      (f) => `
    <div class="figure-gallery-card" data-src="figures/${f.filename}" data-title="${f.title}" data-desc="${f.description}">
      <div class="figure-thumb-wrap">
        <img class="figure-thumb" src="figures/${f.filename}" alt="${f.title}" loading="lazy">
      </div>
      <div class="figure-info">
        <span class="figure-tag">${f.tag}</span>
        <h3 class="figure-title">${f.title}</h3>
        <p class="figure-desc">${f.description}</p>
      </div>
    </div>
  `
    )
    .join("");

  document.querySelectorAll(".figure-gallery-card").forEach((card) => {
    card.addEventListener("click", () => {
      const src = card.getAttribute("data-src");
      const title = card.getAttribute("data-title");
      const desc = card.getAttribute("data-desc");
      openModal(src, title, desc);
    });
  });
}

function setupModal() {
  const modal = document.getElementById("imageModal");
  const closeBtn = document.getElementById("modalCloseBtn");
  const backdrop = document.getElementById("modalBackdrop");

  const closeModal = () => {
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
  };

  closeBtn?.addEventListener("click", closeModal);
  backdrop?.addEventListener("click", closeModal);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("active")) {
      closeModal();
    }
  });
}

function openModal(src, title, desc) {
  const modal = document.getElementById("imageModal");
  const img = document.getElementById("modalImage");
  const cap = document.getElementById("modalCaption");

  img.src = src;
  cap.innerHTML = `<strong>${title}</strong><br>${desc}`;
  modal.classList.add("active");
  modal.setAttribute("aria-hidden", "false");
}

/* ==========================================================================
   8. Executive Report Viewer
   ========================================================================== */
function renderExecutiveReport() {
  const area = document.getElementById("reportContentArea");
  if (!area) return;

  area.innerHTML = `
    <h3>Executive Summary: Indian Electricity Dynamics</h3>
    <p>This empirical study analyzes electricity consumption patterns across Indian states and Union Territories based on daily national records (2013–2024) and monthly state-level panels (2012–2025).</p>
    
    <blockquote>
      "India's daily electricity consumption expanded from 2,771 GWh/day in 2013 to 4,693 GWh/day in 2024 (+69.3%), with a sharp COVID-19 lockdown contraction (-3.77% YoY in 2020) and rapid post-pandemic rebound (+10.48% in 2021)."
    </blockquote>

    <h4>Key Empirical Pillars</h4>
    <ul>
      <li><strong>Scale Determinant:</strong> State population scale explains <strong>97.4% of total consumption variance</strong> (Pearson r = +0.987, R² = 0.974).</li>
      <li><strong>Thermal Stress & Seasonality:</strong> Electricity demand peaks annually in <strong>May (3.61 GWh/state mean)</strong>, an increase of <strong>+19.7%</strong> over the February winter low. Ambient temperature correlates positively (r = +0.291) with electricity consumption.</li>
      <li><strong>Monsoon Precipitation:</strong> High relative humidity (r = -0.220) and rainfall (r = -0.138) suppress cooling loads as monsoon rain cools outdoor ambient temperatures.</li>
      <li><strong>Regional Disparities:</strong> Uttar Pradesh (19.93 GWh/month) and Maharashtra (10.56 GWh/month) represent the largest aggregate loads, while small island territories (Lakshadweep: 0.010 GWh) represent the lowest.</li>
    </ul>
  `;
}
