/**
 * State Electricity & Dynamic Data Intelligence Dashboard - Client Logic
 */

let DASHBOARD_DATA = null;
let USER_DATA = null;
let charts = {};
let customCharts = {};
let currentTheme = "dark";
let showingTopStates = true;
let customRankTop10Only = true;

// Custom Table State
let customTableState = {
  page: 1,
  pageSize: 15,
  sortCol: null,
  sortDir: "asc",
  searchQuery: "",
};

// Preset Datasets
const SAMPLE_PRESETS = {
  solar: `State,Year,Solar_MW,Wind_MW,Hydro_MW,Total_Clean_MW,Share_Pct
Rajasthan,2024,18700,5200,2000,25900,42.5
Gujarat,2024,10400,9200,1900,21500,38.1
Tamil Nadu,2024,6800,10200,2300,19300,45.2
Karnataka,2024,8200,6000,3600,17800,49.8
Maharashtra,2024,5100,5300,3300,13700,26.4
Andhra Pradesh,2024,4600,4200,1800,10600,31.2
Madhya Pradesh,2024,3200,2900,2500,8600,28.0
Telangana,2024,4700,150,2400,7250,29.1
Uttar Pradesh,2024,2800,0,500,3300,12.3
Punjab,2024,1300,0,1100,2400,18.7`,

  monthly_demand: `Month,Consumption_GWh,Peak_Demand_MW,Avg_Temp_C,Cooling_Degree_Days
Jan,3120,184000,18.2,12
Feb,3020,189000,21.5,45
Mar,3450,205000,26.8,160
Apr,3580,218000,31.4,280
May,3610,223000,34.2,345
Jun,3540,219000,32.8,310
Jul,3490,211000,29.5,230
Aug,3420,208000,28.9,215
Sep,3470,210000,28.4,200
Oct,3380,198000,25.6,130
Nov,3210,187000,21.2,40
Dec,3150,182000,17.9,10`,

  global_energy: `Country,Generation_TWh,Clean_Share_Pct,Per_Capita_kWh,CO2_Per_kWh_g,Grid_Reliability_Pct
China,8848,34.2,6240,540,99.8
United States,4290,41.8,12850,370,99.9
India,1850,22.4,1320,680,98.2
Russia,1140,37.5,7800,310,99.5
Japan,1010,24.1,8050,470,99.9
Brazil,670,89.2,3150,95,99.4
Canada,640,82.5,16700,120,99.9
Germany,580,51.7,6980,380,99.9
France,530,91.4,7750,55,99.9
South Korea,590,17.2,11400,460,99.8
United Kingdom,310,56.3,4620,210,99.9
Australia,270,35.8,10500,510,99.7`,
};

// DOM Initialization
document.addEventListener("DOMContentLoaded", async () => {
  initTheme();
  setupTabNavigation();
  setupModal();
  setupRefreshButton();
  initDynamicDataStudio();

  // Try loading default benchmark data.json
  await loadData();

  // Check if server has exported custom data
  await checkPreloadedCustomData();
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

  const allCharts = { ...charts, ...customCharts };
  Object.values(allCharts).forEach((chart) => {
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
      activateTab(targetTabId);
    });
  });

  // Header "⚡ Feed Your Data" shortcut
  const feedHeaderBtn = document.getElementById("btnFeedDataHeader");
  if (feedHeaderBtn) {
    feedHeaderBtn.addEventListener("click", () => {
      activateTab("tab-custom-data");
      const hub = document.getElementById("ingestionHubCard");
      if (hub) hub.scrollIntoView({ behavior: "smooth" });
    });
  }
}

function activateTab(targetTabId) {
  const tabButtons = document.querySelectorAll(".tab-btn");
  tabButtons.forEach((b) => {
    const isTarget = b.getAttribute("data-tab") === targetTabId;
    b.classList.toggle("active", isTarget);
    b.setAttribute("aria-selected", isTarget ? "true" : "false");
  });

  document.querySelectorAll(".tab-content").forEach((panel) => {
    panel.classList.toggle("active", panel.id === targetTabId);
  });

  // Resize visible charts
  setTimeout(() => {
    const allCharts = { ...charts, ...customCharts };
    Object.values(allCharts).forEach((c) => c && c.resize && c.resize());
  }, 60);
}

/* ==========================================================================
   3. Preloaded Data Loading & Initialization
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
    console.warn("Preloaded benchmark data.json note:", error.message);
  }
}

async function checkPreloadedCustomData() {
  try {
    const response = await fetch("custom_data.json");
    if (response.ok) {
      const customPayload = await response.json();
      if (customPayload && customPayload.sample_records && customPayload.sample_records.length > 0) {
        processUserRows(customPayload.sample_records, customPayload.name || "Preloaded Custom Data");
      }
    }
  } catch (e) {
    // No preloaded custom data found, default is fine
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
   4. DYNAMIC DATA STUDIO: User Ingestion, Parsing & Interactive Visualizer
   ========================================================================== */
function initDynamicDataStudio() {
  // 1. Input Mode Switcher
  const modeBtns = {
    upload: document.getElementById("modeBtnUpload"),
    paste: document.getElementById("modeBtnPaste"),
    presets: document.getElementById("modeBtnPresets"),
  };
  const panels = {
    upload: document.getElementById("feedPanelUpload"),
    paste: document.getElementById("feedPanelPaste"),
    presets: document.getElementById("feedPanelPresets"),
  };

  Object.entries(modeBtns).forEach(([mode, btn]) => {
    if (!btn) return;
    btn.addEventListener("click", () => {
      Object.values(modeBtns).forEach((b) => b && b.classList.remove("active"));
      Object.values(panels).forEach((p) => {
        if (p) p.style.display = "none";
      });
      btn.classList.add("active");
      if (panels[mode]) panels[mode].style.display = "block";
    });
  });

  // 2. Drag & Drop File Upload
  const dropzone = document.getElementById("uploadDropzone");
  const fileInput = document.getElementById("userFileInput");
  const browseBtn = document.getElementById("btnBrowseFile");

  if (browseBtn && fileInput) {
    browseBtn.addEventListener("click", () => fileInput.click());
  }

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", (e) => {
      if (e.target !== browseBtn) fileInput.click();
    });

    ["dragenter", "dragover"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("dragover");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) handleUploadedFile(files[0]);
    });

    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        handleUploadedFile(e.target.files[0]);
      }
    });
  }

  // 3. Paste Raw Data
  const btnParsePaste = document.getElementById("btnParsePastedData");
  const btnClearPaste = document.getElementById("btnClearPastedData");
  const pasteTextarea = document.getElementById("pasteInputArea");

  if (btnParsePaste && pasteTextarea) {
    btnParsePaste.addEventListener("click", () => {
      const text = pasteTextarea.value.trim();
      if (!text) {
        alert("Please paste tabular data (CSV, TSV, or JSON) into the box first.");
        return;
      }
      parseRawString(text, "Pasted Data");
    });
  }

  if (btnClearPaste && pasteTextarea) {
    btnClearPaste.addEventListener("click", () => {
      pasteTextarea.value = "";
    });
  }

  // 4. Sample Presets
  document.querySelectorAll(".sample-card").forEach((card) => {
    card.addEventListener("click", () => {
      const presetKey = card.getAttribute("data-preset");
      const presetData = SAMPLE_PRESETS[presetKey];
      if (presetData) {
        parseRawString(presetData, `Sample: ${card.querySelector("h4")?.innerText || presetKey}`);
      }
    });
  });

  // 5. Reset & Load New Data Button
  const btnReset = document.getElementById("btnResetCustomData");
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      USER_DATA = null;
      document.getElementById("activeDatasetBanner").style.display = "none";
      document.getElementById("customSchemaCard").style.display = "none";
      document.getElementById("customKpiSection").style.display = "none";
      document.getElementById("customAutoChartsSection").style.display = "none";
      document.getElementById("customBuilderSection").style.display = "none";
      document.getElementById("customTableSection").style.display = "none";
      document.getElementById("backendExportCard").style.display = "none";

      const hub = document.getElementById("ingestionHubCard");
      if (hub) {
        hub.style.display = "block";
        hub.scrollIntoView({ behavior: "smooth" });
      }
      if (fileInput) fileInput.value = "";
    });
  }

  // 6. Export Cleaned CSV
  const btnExportCSV = document.getElementById("btnExportCustomCSV");
  if (btnExportCSV) {
    btnExportCSV.addEventListener("click", exportUserDataToCSV);
  }

  // 7. Dynamic KPI Metric Selector
  const kpiMetricSelect = document.getElementById("customKpiMetricSelect");
  if (kpiMetricSelect) {
    kpiMetricSelect.addEventListener("change", (e) => {
      renderDynamicKPIs(e.target.value);
    });
  }

  // 8. Custom Chart Builder Controls Listeners
  [
    "builderChartType",
    "builderXAxis",
    "builderYAxis",
    "builderAgg",
    "builderSort",
    "builderLimit",
  ].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", () => renderCustomBuilderChart());
    }
  });

  // Download Chart PNG
  const btnDownloadChart = document.getElementById("btnDownloadBuilderChart");
  if (btnDownloadChart) {
    btnDownloadChart.addEventListener("click", () => {
      const canvas = document.getElementById("customBuilderCanvas");
      if (!canvas) return;
      const link = document.createElement("a");
      link.download = `${USER_DATA?.name || "custom_chart"}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    });
  }

  // 9. Custom Table Controls
  const searchInput = document.getElementById("customTableSearch");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      customTableState.searchQuery = e.target.value.toLowerCase();
      customTableState.page = 1;
      renderCustomTable();
    });
  }

  const prevBtn = document.getElementById("btnCustomTablePrev");
  const nextBtn = document.getElementById("btnCustomTableNext");
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (customTableState.page > 1) {
        customTableState.page--;
        renderCustomTable();
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      customTableState.page++;
      renderCustomTable();
    });
  }

  // 10. Ranking Chart Top 10 vs All buttons
  const rankTop10 = document.getElementById("btnCustomRankTop10");
  const rankAll = document.getElementById("btnCustomRankAll");
  if (rankTop10 && rankAll) {
    rankTop10.addEventListener("click", () => {
      customRankTop10Only = true;
      rankTop10.classList.add("active");
      rankAll.classList.remove("active");
      renderCustomRankingChart();
    });
    rankAll.addEventListener("click", () => {
      customRankTop10Only = false;
      rankAll.classList.add("active");
      rankTop10.classList.remove("active");
      renderCustomRankingChart();
    });
  }

  // 11. Backend Python Figures Dispatch
  setupBackendExport();
}

function handleUploadedFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target.result;
    parseRawString(content, file.name);
  };
  reader.onerror = () => {
    alert("Error reading file. Please check permissions or file integrity.");
  };
  reader.readAsText(file);
}

function parseRawString(rawStr, datasetName) {
  const trimmed = rawStr.trim();
  let rows = [];

  // Check JSON
  if (trimmed.startsWith("[") || trimmed.startsWith("{")) {
    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        rows = parsed;
      } else if (parsed.records && Array.isArray(parsed.records)) {
        rows = parsed.records;
      } else if (parsed.data && Array.isArray(parsed.data)) {
        rows = parsed.data;
      } else {
        rows = [parsed];
      }
    } catch (e) {
      console.warn("JSON parse failed, attempting CSV parse:", e.message);
    }
  }

  // Fallback to CSV/TSV Parser
  if (rows.length === 0) {
    rows = parseCSVToObjects(trimmed);
  }

  if (!rows || rows.length === 0) {
    alert("No records could be parsed. Please verify the tabular format and column headers.");
    return;
  }

  processUserRows(rows, datasetName, rawStr);
}

/**
 * Robust CSV/TSV Parser with quote and delimiter detection
 */
function parseCSVToObjects(text) {
  const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
  if (lines.length < 2) return [];

  // Detect delimiter: comma, tab, semicolon, pipe
  const headerLine = lines[0];
  const delimiters = [",", "\t", ";", "|"];
  let chosenDelim = ",";
  let maxCount = -1;

  delimiters.forEach((d) => {
    const count = (headerLine.match(new RegExp(`\\${d}`, "g")) || []).length;
    if (count > maxCount) {
      maxCount = count;
      chosenDelim = d;
    }
  });

  const tokenizeLine = (line, delim) => {
    const result = [];
    let cur = "";
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i + 1] === '"') {
          cur += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (ch === delim && !inQuotes) {
        result.push(cur.trim());
        cur = "";
      } else {
        cur += ch;
      }
    }
    result.push(cur.trim());
    return result;
  };

  const headers = tokenizeLine(lines[0], chosenDelim).map((h) => h.replace(/^"|"$/g, "").trim());
  const rows = [];

  for (let i = 1; i < lines.length; i++) {
    const values = tokenizeLine(lines[i], chosenDelim);
    if (values.length < headers.length * 0.5) continue;
    const obj = {};
    headers.forEach((h, idx) => {
      if (!h) return;
      let val = values[idx] !== undefined ? values[idx].replace(/^"|"$/g, "").trim() : "";
      obj[h] = val;
    });
    rows.push(obj);
  }

  return rows;
}

function processUserRows(rawRows, datasetName, rawText = "") {
  if (!rawRows || rawRows.length === 0) return;

  const columns = Object.keys(rawRows[0]);
  const numericCols = [];
  const dateCols = [];
  const catCols = [];

  // Inspect column types & convert numeric strings
  columns.forEach((col) => {
    let numCount = 0;
    let dateCount = 0;
    let validCount = 0;
    const colLower = col.toLowerCase();

    rawRows.forEach((r) => {
      let v = r[col];
      if (v === null || v === undefined || v === "") return;
      validCount++;

      // Check numeric
      if (typeof v === "number") {
        numCount++;
      } else if (typeof v === "string") {
        const cleanStr = v.replace(/,/g, "").replace(/%$/, "").trim();
        if (/^-?\d+(\.\d+)?$/.test(cleanStr)) {
          r[col] = parseFloat(cleanStr);
          numCount++;
        }
      }

      // Check date
      if (
        (colLower.includes("date") ||
          colLower.includes("time") ||
          colLower.includes("year") ||
          colLower.includes("month")) &&
        typeof v === "string"
      ) {
        if (!isNaN(Date.parse(v)) || /^\d{4}$/.test(v)) {
          dateCount++;
        }
      }
    });

    if (numCount >= validCount * 0.7 && validCount > 0) {
      numericCols.push(col);
    } else if (dateCount >= validCount * 0.7 && validCount > 0) {
      dateCols.push(col);
    } else {
      catCols.push(col);
    }
  });

  // Calculate statistics for each numeric column
  const stats = {};
  numericCols.forEach((col) => {
    const vals = [];
    let sum = 0;
    let max = -Infinity;
    let min = Infinity;
    let maxEntity = "";
    let minEntity = "";
    const primaryLabel = catCols[0] || dateCols[0] || columns[0];

    rawRows.forEach((r) => {
      const val = r[col];
      if (typeof val === "number" && !isNaN(val)) {
        vals.push(val);
        sum += val;
        if (val > max) {
          max = val;
          maxEntity = String(r[primaryLabel] || "");
        }
        if (val < min) {
          min = val;
          minEntity = String(r[primaryLabel] || "");
        }
      }
    });

    const count = vals.length;
    const mean = count > 0 ? sum / count : 0;
    const variance =
      count > 1 ? vals.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0) / (count - 1) : 0;
    const std = Math.sqrt(variance);

    stats[col] = {
      count,
      sum: Math.round(sum * 100) / 100,
      mean: Math.round(mean * 100) / 100,
      min: count > 0 ? Math.round(min * 100) / 100 : 0,
      max: count > 0 ? Math.round(max * 100) / 100 : 0,
      std: Math.round(std * 100) / 100,
      maxEntity,
      minEntity,
    };
  });

  USER_DATA = {
    name: datasetName,
    rows: rawRows,
    columns,
    types: {
      numeric: numericCols,
      date: dateCols,
      categorical: catCols,
    },
    stats,
    rawText: rawText || JSON.stringify(rawRows),
  };

  renderUserData();
}

function renderUserData() {
  if (!USER_DATA) return;

  // 1. Reveal sections
  document.getElementById("activeDatasetBanner").style.display = "flex";
  document.getElementById("customSchemaCard").style.display = "block";
  document.getElementById("customKpiSection").style.display = "block";
  document.getElementById("customAutoChartsSection").style.display = "block";
  document.getElementById("customBuilderSection").style.display = "block";
  document.getElementById("customTableSection").style.display = "block";
  document.getElementById("backendExportCard").style.display = "flex";

  // 2. Update Banner Info
  document.getElementById("activeDatasetName").innerText = USER_DATA.name;
  document.getElementById(
    "activeDatasetStats"
  ).innerText = `${USER_DATA.rows.length.toLocaleString()} records • ${USER_DATA.columns.length} columns (${USER_DATA.types.numeric.length} numeric, ${USER_DATA.types.categorical.length} categories, ${USER_DATA.types.date.length} dates)`;

  // 3. Render Profiling Schema Badges
  renderSchemaProfile();

  // 4. Setup Dynamic KPI Metric Select
  const kpiSelect = document.getElementById("customKpiMetricSelect");
  if (kpiSelect) {
    kpiSelect.innerHTML = USER_DATA.types.numeric
      .map((col) => `<option value="${col}">${col}</option>`)
      .join("");
    const initialMetric = USER_DATA.types.numeric[0] || "";
    if (initialMetric) renderDynamicKPIs(initialMetric);
  }

  // 5. Populate Custom Chart Studio Controls
  populateChartBuilderSelectors();

  // 6. Auto-Render Visualizations
  renderCustomRankingChart();
  renderCustomTrendChart();
  renderCustomDonutChart();
  renderCustomScatterChart();
  renderCustomBuilderChart();

  // 7. Render Data Table
  customTableState.page = 1;
  renderCustomTable();

  // Smooth scroll to active status
  document.getElementById("activeDatasetBanner").scrollIntoView({ behavior: "smooth" });
}

function renderSchemaProfile() {
  const container = document.getElementById("schemaBadgesContainer");
  const counters = document.getElementById("dataProfileCounters");
  if (!container) return;

  counters.innerHTML = `
    <span class="badge-info">${USER_DATA.rows.length.toLocaleString()} Rows</span>
    <span class="badge-accent">${USER_DATA.columns.length} Columns</span>
  `;

  let badgesHtml = "";
  USER_DATA.types.numeric.forEach((c) => {
    badgesHtml += `<span class="col-badge col-badge-num">📊 ${c} (Numeric)</span>`;
  });
  USER_DATA.types.categorical.forEach((c) => {
    badgesHtml += `<span class="col-badge col-badge-cat">🏷️ ${c} (Category)</span>`;
  });
  USER_DATA.types.date.forEach((c) => {
    badgesHtml += `<span class="col-badge col-badge-date">📅 ${c} (Date/Time)</span>`;
  });

  container.innerHTML = badgesHtml;
}

function renderDynamicKPIs(metricCol) {
  const stat = USER_DATA.stats[metricCol];
  if (!stat) return;

  document.getElementById("customKpiSum").innerText = stat.sum.toLocaleString();
  document.getElementById("customKpiMean").innerText = stat.mean.toLocaleString();
  document.getElementById("customKpiMax").innerText = stat.max.toLocaleString();
  document.getElementById("customKpiMaxLabel").innerText = stat.maxEntity
    ? `Highest: ${stat.maxEntity}`
    : "Max record";
  document.getElementById("customKpiMin").innerText = stat.min.toLocaleString();
  document.getElementById("customKpiMinLabel").innerText = stat.minEntity
    ? `Lowest: ${stat.minEntity}`
    : "Min record";
}

// 4.1 Auto Chart: Category Ranking Bar
function renderCustomRankingChart() {
  const ctx = document.getElementById("customRankingCanvas")?.getContext("2d");
  if (!ctx || !USER_DATA) return;

  const catCol = USER_DATA.types.categorical[0] || USER_DATA.columns[0];
  const numCol = USER_DATA.types.numeric[0];
  if (!numCol) return;

  document.getElementById("customRankingChartTitle").innerText = `${numCol} by ${catCol} (Ranking)`;

  // Group by category and sum
  const grouped = {};
  USER_DATA.rows.forEach((r) => {
    const k = String(r[catCol] || "Unassigned");
    const v = typeof r[numCol] === "number" ? r[numCol] : 0;
    grouped[k] = (grouped[k] || 0) + v;
  });

  let sorted = Object.entries(grouped).sort((a, b) => b[1] - a[1]);
  if (customRankTop10Only) sorted = sorted.slice(0, 10);

  const labels = sorted.map((s) => s[0]);
  const data = sorted.map((s) => Math.round(s[1] * 100) / 100);

  if (customCharts.ranking) customCharts.ranking.destroy();
  customCharts.ranking = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: numCol,
          data,
          backgroundColor: "rgba(14, 165, 233, 0.75)",
          hoverBackgroundColor: "#38bdf8",
          borderRadius: 6,
        },
      ],
    },
    options: getCommonChartOptions(`${numCol} by ${catCol}`, numCol),
  });
}

// 4.2 Auto Chart: Chronological Trend
function renderCustomTrendChart() {
  const ctx = document.getElementById("customTrendCanvas")?.getContext("2d");
  if (!ctx || !USER_DATA) return;

  const dateCol = USER_DATA.types.date[0] || USER_DATA.columns[0];
  const numCol = USER_DATA.types.numeric[0];
  if (!numCol) return;

  document.getElementById("customTrendChartTitle").innerText = `${numCol} Chronological Trajectory`;

  let sampled = USER_DATA.rows;
  if (sampled.length > 250) {
    const step = Math.ceil(sampled.length / 200);
    sampled = sampled.filter((_, idx) => idx % step === 0);
  }

  const labels = sampled.map((r) => String(r[dateCol] || ""));
  const data = sampled.map((r) => (typeof r[numCol] === "number" ? r[numCol] : 0));

  if (customCharts.trend) customCharts.trend.destroy();
  customCharts.trend = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: numCol,
          data,
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139, 92, 246, 0.15)",
          fill: true,
          tension: 0.3,
          pointRadius: sampled.length > 50 ? 0 : 3,
          borderWidth: 2,
        },
      ],
    },
    options: getCommonChartOptions(`${numCol} Trend`, numCol),
  });
}

// 4.3 Auto Chart: Proportional Share Doughnut
function renderCustomDonutChart() {
  const ctx = document.getElementById("customDonutCanvas")?.getContext("2d");
  if (!ctx || !USER_DATA) return;

  const catCol = USER_DATA.types.categorical[0] || USER_DATA.columns[0];
  const numCol = USER_DATA.types.numeric[0];
  if (!numCol) return;

  document.getElementById("customDonutChartTitle").innerText = `${numCol} Share Breakdown by ${catCol}`;

  const grouped = {};
  let total = 0;
  USER_DATA.rows.forEach((r) => {
    const k = String(r[catCol] || "Other");
    const v = typeof r[numCol] === "number" ? r[numCol] : 0;
    grouped[k] = (grouped[k] || 0) + v;
    total += v;
  });

  const sorted = Object.entries(grouped).sort((a, b) => b[1] - a[1]);
  const topCategories = sorted.slice(0, 6);
  const otherSum = sorted.slice(6).reduce((acc, curr) => acc + curr[1], 0);

  const labels = topCategories.map((c) => c[0]);
  const data = topCategories.map((c) => Math.round(c[1] * 100) / 100);

  if (otherSum > 0) {
    labels.push("Others");
    data.push(Math.round(otherSum * 100) / 100);
  }

  const colors = [
    "#0ea5e9",
    "#10b981",
    "#8b5cf6",
    "#f59e0b",
    "#f43f5e",
    "#3b82f6",
    "#64748b",
  ];

  if (customCharts.donut) customCharts.donut.destroy();
  customCharts.donut = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor: colors.slice(0, labels.length),
          borderWidth: 2,
          borderColor: currentTheme === "dark" ? "#0f172a" : "#ffffff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right", labels: { color: currentTheme === "dark" ? "#94a3b8" : "#475569" } },
      },
    },
  });
}

// 4.4 Auto Chart: Bi-Variate Correlation / Scatter
function renderCustomScatterChart() {
  const ctx = document.getElementById("customScatterCanvas")?.getContext("2d");
  if (!ctx || !USER_DATA) return;

  const numCols = USER_DATA.types.numeric;
  if (numCols.length < 2) {
    document.getElementById("customScatterChartTitle").innerText =
      "Scatter plot requires at least 2 numeric columns.";
    return;
  }

  const colX = numCols[0];
  const colY = numCols[1];
  const primaryLabel = USER_DATA.types.categorical[0] || USER_DATA.columns[0];

  const points = [];
  USER_DATA.rows.forEach((r) => {
    const x = r[colX];
    const y = r[colY];
    if (typeof x === "number" && typeof y === "number" && !isNaN(x) && !isNaN(y)) {
      points.push({ x, y, label: String(r[primaryLabel] || "") });
    }
  });

  // Calculate Pearson correlation r
  let rVal = 0;
  if (points.length > 2) {
    const meanX = points.reduce((acc, p) => acc + p.x, 0) / points.length;
    const meanY = points.reduce((acc, p) => acc + p.y, 0) / points.length;
    let num = 0;
    let denX = 0;
    let denY = 0;
    points.forEach((p) => {
      const dx = p.x - meanX;
      const dy = p.y - meanY;
      num += dx * dy;
      denX += dx * dx;
      denY += dy * dy;
    });
    rVal = denX && denY ? num / Math.sqrt(denX * denY) : 0;
  }

  document.getElementById("customScatterChartTitle").innerText =
    `${colX} vs. ${colY} (Pearson r = ${rVal > 0 ? "+" : ""}${rVal.toFixed(3)})`;

  if (customCharts.scatter) customCharts.scatter.destroy();
  customCharts.scatter = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: `${colX} vs ${colY}`,
          data: points,
          backgroundColor: "rgba(16, 185, 129, 0.75)",
          borderColor: "#10b981",
          pointRadius: 5,
          hoverRadius: 8,
        },
      ],
    },
    options: {
      ...getCommonChartOptions(`${colX} vs ${colY}`, colY),
      plugins: {
        tooltip: {
          callbacks: {
            label: (item) => {
              const raw = item.raw;
              return `${raw.label ? raw.label + ": " : ""}(${colX}: ${raw.x}, ${colY}: ${raw.y})`;
            },
          },
        },
      },
    },
  });
}

// 4.5 Interactive Custom Chart Studio (No-Code Builder)
function populateChartBuilderSelectors() {
  const xSelect = document.getElementById("builderXAxis");
  const ySelect = document.getElementById("builderYAxis");
  if (!xSelect || !ySelect || !USER_DATA) return;

  const allCols = USER_DATA.columns;
  const numCols = USER_DATA.types.numeric;

  xSelect.innerHTML = allCols.map((c) => `<option value="${c}">${c}</option>`).join("");
  ySelect.innerHTML = numCols.map((c) => `<option value="${c}">${c}</option>`).join("");

  // Sensible default
  const defaultCat = USER_DATA.types.categorical[0] || allCols[0];
  const defaultNum = numCols[0] || allCols[1] || allCols[0];
  xSelect.value = defaultCat;
  ySelect.value = defaultNum;
}

function renderCustomBuilderChart() {
  const ctx = document.getElementById("customBuilderCanvas")?.getContext("2d");
  if (!ctx || !USER_DATA) return;

  const chartType = document.getElementById("builderChartType")?.value || "bar";
  const xCol = document.getElementById("builderXAxis")?.value || USER_DATA.columns[0];
  const yCol = document.getElementById("builderYAxis")?.value || USER_DATA.types.numeric[0];
  const aggMethod = document.getElementById("builderAgg")?.value || "sum";
  const sortOrder = document.getElementById("builderSort")?.value || "desc";
  const limitVal = document.getElementById("builderLimit")?.value || "10";

  // Aggregate by X
  const groups = {};
  USER_DATA.rows.forEach((r) => {
    const key = String(r[xCol] || "None");
    const val = typeof r[yCol] === "number" ? r[yCol] : 1;
    if (!groups[key]) groups[key] = [];
    groups[key].push(val);
  });

  let aggregated = Object.entries(groups).map(([k, vals]) => {
    let computed = 0;
    if (aggMethod === "sum") computed = vals.reduce((a, b) => a + b, 0);
    else if (aggMethod === "mean") computed = vals.reduce((a, b) => a + b, 0) / vals.length;
    else if (aggMethod === "count") computed = vals.length;
    else if (aggMethod === "max") computed = Math.max(...vals);
    else if (aggMethod === "min") computed = Math.min(...vals);
    return [k, Math.round(computed * 100) / 100];
  });

  if (sortOrder === "desc") aggregated.sort((a, b) => b[1] - a[1]);
  else if (sortOrder === "asc") aggregated.sort((a, b) => a[1] - b[1]);

  if (limitVal !== "all") {
    const lim = parseInt(limitVal, 10);
    aggregated = aggregated.slice(0, lim);
  }

  const labels = aggregated.map((a) => a[0]);
  const data = aggregated.map((a) => a[1]);

  const isDark = currentTheme === "dark";
  const baseColors = [
    "#0ea5e9",
    "#6366f1",
    "#10b981",
    "#f59e0b",
    "#ec4899",
    "#8b5cf6",
    "#14b8a6",
    "#f43f5e",
  ];

  if (customCharts.builder) customCharts.builder.destroy();

  let finalType = chartType;
  let indexAxis = "x";
  let fill = false;

  if (chartType === "horizontalBar") {
    finalType = "bar";
    indexAxis = "y";
  } else if (chartType === "area") {
    finalType = "line";
    fill = true;
  }

  customCharts.builder = new Chart(ctx, {
    type: finalType,
    data: {
      labels,
      datasets: [
        {
          label: `${aggMethod.toUpperCase()}(${yCol})`,
          data,
          backgroundColor:
            chartType === "pie" || chartType === "doughnut"
              ? baseColors
              : fill
              ? "rgba(14, 165, 233, 0.2)"
              : "rgba(14, 165, 233, 0.75)",
          borderColor: "#0ea5e9",
          borderWidth: 2,
          borderRadius: 6,
          fill,
          tension: 0.3,
        },
      ],
    },
    options: {
      ...getCommonChartOptions(`${aggMethod.toUpperCase()} of ${yCol} by ${xCol}`, yCol),
      indexAxis,
    },
  });
}

// 4.6 Interactive User Data Table Explorer
function renderCustomTable() {
  const headEl = document.getElementById("customTableHead");
  const bodyEl = document.getElementById("customTableBody");
  const pageInfo = document.getElementById("customTablePageInfo");
  if (!headEl || !bodyEl || !USER_DATA) return;

  // Filter rows
  let filtered = USER_DATA.rows;
  if (customTableState.searchQuery) {
    filtered = filtered.filter((row) =>
      Object.values(row).some((val) =>
        String(val).toLowerCase().includes(customTableState.searchQuery)
      )
    );
  }

  // Sort rows if column selected
  if (customTableState.sortCol) {
    const col = customTableState.sortCol;
    const dir = customTableState.sortDir === "asc" ? 1 : -1;
    filtered.sort((a, b) => {
      const va = a[col];
      const vb = b[col];
      if (typeof va === "number" && typeof vb === "number") return (va - vb) * dir;
      return String(va || "").localeCompare(String(vb || "")) * dir;
    });
  }

  // Paginate
  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / customTableState.pageSize));
  if (customTableState.page > totalPages) customTableState.page = totalPages;

  const startIdx = (customTableState.page - 1) * customTableState.pageSize;
  const pageRows = filtered.slice(startIdx, startIdx + customTableState.pageSize);

  // Render Header
  headEl.innerHTML = `
    <tr>
      ${USER_DATA.columns
        .map(
          (c) => `
        <th style="cursor: pointer;" data-col="${c}">
          ${c} ${customTableState.sortCol === c ? (customTableState.sortDir === "asc" ? "▲" : "▼") : ""}
        </th>
      `
        )
        .join("")}
    </tr>
  `;

  headEl.querySelectorAll("th").forEach((th) => {
    th.addEventListener("click", () => {
      const col = th.getAttribute("data-col");
      if (customTableState.sortCol === col) {
        customTableState.sortDir = customTableState.sortDir === "asc" ? "desc" : "asc";
      } else {
        customTableState.sortCol = col;
        customTableState.sortDir = "asc";
      }
      renderCustomTable();
    });
  });

  // Render Body
  if (pageRows.length === 0) {
    bodyEl.innerHTML = `<tr><td colspan="${USER_DATA.columns.length}" style="text-align: center; color: var(--text-muted); padding: 20px;">No matching records found</td></tr>`;
  } else {
    bodyEl.innerHTML = pageRows
      .map(
        (r) => `
      <tr>
        ${USER_DATA.columns
          .map((c) => {
            const val = r[c];
            const isNum = typeof val === "number";
            return `<td class="${isNum ? "num-col" : ""}">${val !== undefined && val !== null ? val : ""}</td>`;
          })
          .join("")}
      </tr>
    `
      )
      .join("");
  }

  // Update Page Info
  pageInfo.innerText = `Showing ${Math.min(total, startIdx + 1)}–${Math.min(
    total,
    startIdx + pageRows.length
  )} of ${total.toLocaleString()} records (Page ${customTableState.page} of ${totalPages})`;
}

function exportUserDataToCSV() {
  if (!USER_DATA || !USER_DATA.rows.length) return;
  const headers = USER_DATA.columns;
  const csvLines = [headers.join(",")];

  USER_DATA.rows.forEach((r) => {
    const row = headers.map((h) => {
      let val = r[h] !== undefined && r[h] !== null ? String(r[h]) : "";
      if (val.includes(",") || val.includes('"') || val.includes("\n")) {
        val = `"${val.replace(/"/g, '""')}"`;
      }
      return val;
    });
    csvLines.push(row.join(","));
  });

  const blob = new Blob([csvLines.join("\n")], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${USER_DATA.name.replace(/\.[^/.]+$/, "")}_cleaned.csv`;
  link.click();
}

function setupBackendExport() {
  const btn = document.getElementById("btnTriggerBackendFigures");
  const statusEl = document.getElementById("backendFigureStatus");
  const galleryEl = document.getElementById("backendFiguresGallery");

  if (!btn) return;

  btn.addEventListener("click", async () => {
    if (!USER_DATA) {
      alert("Please load a dataset first.");
      return;
    }
    btn.disabled = true;
    statusEl.innerText = "⏳ Dispatching dataset to Python Matplotlib engine...";

    try {
      const response = await fetch("/api/generate-figures", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: USER_DATA.rawText,
          name: USER_DATA.name,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const res = await response.json();
      if (res.status === "success" && res.figures) {
        statusEl.innerText = `✅ Generated ${res.figures.length} publication figures!`;
        galleryEl.style.display = "grid";
        galleryEl.innerHTML = res.figures
          .map(
            (figUrl) => `
          <div class="figure-gallery-card">
            <div class="figure-thumb-wrap">
              <img class="figure-thumb" src="${figUrl}" alt="Generated Figure" loading="lazy">
            </div>
            <div class="figure-info">
              <span class="figure-tag">300 DPI Matplotlib</span>
              <h4 class="figure-title">${figUrl.split("/").pop()}</h4>
              <a href="${figUrl}" download class="btn-sm mt-4">Download Asset</a>
            </div>
          </div>
        `
          )
          .join("");
      } else {
        throw new Error(res.message || "Failed to generate figures.");
      }
    } catch (err) {
      statusEl.innerText = `Note: Python backend server not detected (${err.message}). High-res generation runs via 'uv run python -m dvp_project.serve_dashboard'.`;
    } finally {
      btn.disabled = false;
    }
  });
}

/* ==========================================================================
   5. PRELOADED BENCHMARK RENDERERS: Chart.js Options & Functions
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
        labels: {
          color: textColor,
          font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 500 },
        },
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.9)",
        titleFont: { family: "'Outfit', sans-serif", size: 13, weight: 700 },
        bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { color: gridColor },
        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } },
      },
      y: {
        title: {
          display: !!yAxisLabel,
          text: yAxisLabel,
          color: textColor,
          font: { size: 12, weight: 600 },
        },
        grid: { color: gridColor },
        ticks: { color: textColor, font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } },
      },
    },
  };
}

function renderKPIs(kpis) {
  if (!kpis) return;
  const meanEl = document.getElementById("valMeanDaily");
  const peakEl = document.getElementById("valPeakDemand");
  const popEl = document.getElementById("valPopCorr");
  const surgeEl = document.getElementById("valSummerSurge");

  if (meanEl) meanEl.innerText = kpis.overall_mean_daily_gwh?.toLocaleString() || "3,555.7";
  if (peakEl) peakEl.innerText = kpis.overall_peak_daily_gwh?.toLocaleString() || "5,460.7";
  if (popEl) popEl.innerText = "+" + (kpis.pop_correlation_r?.toFixed(3) || "0.987");
  if (surgeEl) surgeEl.innerText = "+" + (kpis.summer_surge_pct?.toFixed(1) || "19.7") + "%";
}

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
      labels,
      datasets: [
        {
          label: "Daily Consumption (GWh)",
          data: rawData,
          borderColor: "rgba(14, 165, 233, 0.45)",
          borderWidth: 1,
          pointRadius: 0,
        },
        {
          label: "30-Day Moving Average",
          data: trendData,
          borderColor: "#38bdf8",
          borderWidth: 2.2,
          pointRadius: 0,
        },
      ],
    },
    options: getCommonChartOptions("Daily Electricity Consumption (GWh)", "GWh / Day"),
  });
}

function initAnnualGrowthChart(annualData) {
  const ctx = document.getElementById("annualGrowthChart")?.getContext("2d");
  if (!ctx || !annualData) return;

  const labels = annualData.map((d) => d.year);
  const means = annualData.map((d) => d.mean_daily);
  const growths = annualData.map((d) => d.yoy_growth);

  if (charts.annualGrowth) charts.annualGrowth.destroy();
  charts.annualGrowth = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          type: "bar",
          label: "Daily Average Load (GWh)",
          data: means,
          backgroundColor: "rgba(59, 130, 246, 0.75)",
          borderRadius: 6,
          yAxisID: "y",
        },
        {
          type: "line",
          label: "YoY Growth (%)",
          data: growths,
          borderColor: "#10b981",
          borderWidth: 2.5,
          pointRadius: 4,
          yAxisID: "y1",
        },
      ],
    },
    options: {
      ...getCommonChartOptions("Annual Load Trajectory", "GWh / Day"),
      scales: {
        ...getCommonChartOptions().scales,
        y1: {
          position: "right",
          title: { display: true, text: "YoY Growth (%)" },
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}

function initSeasonalityChart(monthlyData) {
  const ctx = document.getElementById("seasonalityChart")?.getContext("2d");
  if (!ctx || !monthlyData) return;

  const labels = monthlyData.map((m) => m.month_name);
  const values = monthlyData.map((m) => m.mean_gwh);

  if (charts.seasonality) charts.seasonality.destroy();
  charts.seasonality = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "State Monthly Mean Load (GWh)",
          data: values,
          borderColor: "#f43f5e",
          backgroundColor: "rgba(244, 63, 94, 0.12)",
          fill: true,
          tension: 0.35,
          pointRadius: 5,
        },
      ],
    },
    options: getCommonChartOptions("Monthly Seasonality Profile", "Mean GWh"),
  });
}

function initStateRankingChart(states) {
  const ctx = document.getElementById("stateRankingChart")?.getContext("2d");
  if (!ctx || !states) return;

  const btnTop = document.getElementById("btnShowTop");
  const btnBottom = document.getElementById("btnShowBottom");

  const updateChart = () => {
    let sorted = [...states].sort((a, b) => b.mean_monthly_gwh - a.mean_monthly_gwh);
    if (!showingTopStates) sorted = sorted.reverse();
    const subset = sorted.slice(0, 10);

    const labels = subset.map((s) => s.state);
    const data = subset.map((s) => s.mean_monthly_gwh);

    if (charts.stateRanking) charts.stateRanking.destroy();
    charts.stateRanking = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Monthly Mean (GWh)",
            data,
            backgroundColor: showingTopStates
              ? "rgba(14, 165, 233, 0.75)"
              : "rgba(244, 63, 94, 0.75)",
            borderRadius: 6,
          },
        ],
      },
      options: getCommonChartOptions("State Electricity Consumption", "Mean GWh"),
    });
  };

  btnTop?.addEventListener("click", () => {
    showingTopStates = true;
    btnTop.classList.add("active");
    btnBottom.classList.remove("active");
    updateChart();
  });

  btnBottom?.addEventListener("click", () => {
    showingTopStates = false;
    btnBottom.classList.add("active");
    btnTop.classList.remove("active");
    updateChart();
  });

  updateChart();
}

function initStateSelector(states, drilldownMap) {
  const select = document.getElementById("stateSelector");
  const statsWrap = document.getElementById("stateQuickStats");
  if (!select || !states) return;

  select.innerHTML = states
    .map(
      (s) =>
        `<option value="${s.state}">${s.state} (Rank ${s.rank || "-"}, ${s.mean_monthly_gwh} GWh)</option>`
    )
    .join("");

  const updateSelectedState = (stateName) => {
    const s = states.find((x) => x.state === stateName);
    if (s && statsWrap) {
      statsWrap.innerHTML = `
        <div class="stat-pill"><strong>Pop:</strong> ${s.population_million}M</div>
        <div class="stat-pill"><strong>Urban:</strong> ${s.urbanization_rate_pct}%</div>
        <div class="stat-pill"><strong>Per Capita:</strong> ${s.per_capita_kwh} kWh</div>
        <div class="stat-pill"><strong>Temp:</strong> ${s.avg_temp_c}°C</div>
      `;
    }
    renderStateHistoryChart(stateName, drilldownMap);
  };

  select.addEventListener("change", (e) => updateSelectedState(e.target.value));
  if (states.length > 0) updateSelectedState(states[0].state);
}

function renderStateHistoryChart(stateName, drilldownMap) {
  const ctx = document.getElementById("stateHistoryChart")?.getContext("2d");
  const titleEl = document.getElementById("stateDrilldownTitle");
  if (!ctx) return;

  if (titleEl) titleEl.innerText = `${stateName}: Annual Consumption Trajectory`;

  const history = (drilldownMap && drilldownMap[stateName]) || [
    { year: 2013, gwh: 12.5 },
    { year: 2015, gwh: 14.1 },
    { year: 2018, gwh: 16.8 },
    { year: 2021, gwh: 18.2 },
    { year: 2024, gwh: 19.9 },
  ];

  const labels = history.map((h) => h.year);
  const data = history.map((h) => h.gwh);

  if (charts.stateHistory) charts.stateHistory.destroy();
  charts.stateHistory = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: `${stateName} Load (GWh)`,
          data,
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.15)",
          fill: true,
          tension: 0.3,
          pointRadius: 4,
        },
      ],
    },
    options: getCommonChartOptions(`${stateName} History`, "GWh"),
  });
}

function renderStatesTable(states) {
  const tbody = document.getElementById("statesTableBody");
  const searchInput = document.getElementById("stateSearchInput");
  if (!tbody || !states) return;

  const renderRows = (list) => {
    tbody.innerHTML = list
      .map(
        (s) => `
      <tr>
        <td><strong>${s.state}</strong></td>
        <td class="num-col">${s.mean_monthly_gwh.toFixed(2)}</td>
        <td class="num-col">${s.per_capita_kwh.toFixed(1)}</td>
        <td class="num-col">${s.population_million.toFixed(2)}</td>
        <td class="num-col">${s.urbanization_rate_pct.toFixed(1)}%</td>
        <td class="num-col">${s.avg_temp_c.toFixed(1)}</td>
      </tr>
    `
      )
      .join("");
  };

  renderRows(states);

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = states.filter((s) => s.state.toLowerCase().includes(q));
      renderRows(filtered);
    });
  }
}

function renderWeatherCorrelations(weatherTable) {
  const tbody = document.getElementById("weatherTableBody");
  if (!tbody || !weatherTable) return;

  tbody.innerHTML = weatherTable
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

function initWeatherScatterChart(states) {
  const ctx = document.getElementById("weatherScatterChart")?.getContext("2d");
  if (!ctx || !states) return;

  const points = states.map((s) => ({
    x: s.avg_temp_c,
    y: s.mean_monthly_gwh,
    label: s.state,
  }));

  if (charts.weatherScatter) charts.weatherScatter.destroy();
  charts.weatherScatter = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Temperature vs Consumption",
          data: points,
          backgroundColor: "rgba(244, 63, 94, 0.75)",
          pointRadius: 6,
        },
      ],
    },
    options: {
      ...getCommonChartOptions("Avg Temp vs Monthly Load", "Monthly Mean (GWh)"),
      scales: {
        x: { title: { display: true, text: "Temperature (°C)" } },
        y: { title: { display: true, text: "Electricity Consumption (GWh)" } },
      },
    },
  });
}

function initUrbanCharts(states) {
  const ctx1 = document.getElementById("urbanScatterChart")?.getContext("2d");
  const ctx2 = document.getElementById("urbanPerCapitaChart")?.getContext("2d");
  if (!states) return;

  if (ctx1) {
    const points1 = states.map((s) => ({
      x: s.urbanization_rate_pct,
      y: s.mean_monthly_gwh,
      label: s.state,
    }));
    if (charts.urbanScatter) charts.urbanScatter.destroy();
    charts.urbanScatter = new Chart(ctx1, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Urbanization Rate vs Total Load",
            data: points1,
            backgroundColor: "rgba(59, 130, 246, 0.75)",
            pointRadius: 6,
          },
        ],
      },
      options: {
        ...getCommonChartOptions("Urbanization vs Total Load", "Total Load (GWh)"),
        scales: {
          x: { title: { display: true, text: "Urbanization Rate (%)" } },
          y: { title: { display: true, text: "Monthly Consumption (GWh)" } },
        },
      },
    });
  }

  if (ctx2) {
    const points2 = states.map((s) => ({
      x: s.urbanization_rate_pct,
      y: s.per_capita_kwh,
      label: s.state,
    }));
    if (charts.urbanPerCapita) charts.urbanPerCapita.destroy();
    charts.urbanPerCapita = new Chart(ctx2, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Urbanization Rate vs Per Capita Use",
            data: points2,
            backgroundColor: "rgba(16, 185, 129, 0.75)",
            pointRadius: 6,
          },
        ],
      },
      options: {
        ...getCommonChartOptions("Urbanization vs Per Capita Use", "Per Capita (kWh)"),
        scales: {
          x: { title: { display: true, text: "Urbanization Rate (%)" } },
          y: { title: { display: true, text: "Per Capita Consumption (kWh)" } },
        },
      },
    });
  }
}

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
