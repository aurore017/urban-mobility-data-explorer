
const API_BASE_URL = "http://localhost:5000";

let topZonesChartInstance = null;
let boroughPieChartInstance = null;



async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Request failed: ${url} (${res.status})`);
  }
  return res.json();
}

function setStatus(message, isError = false) {
  const el = document.getElementById("status-message");
  if (!el) return;
  el.textContent = message;
  el.style.color = isError ? "var(--color-error, #b00020)" : "inherit";
}


function renderTopZonesChart(data) {
  const ctx = document.getElementById("topZonesChart");
  if (!ctx) return;

  const labels = data.map((d) => d.zone);
  const counts = data.map((d) => d.trip_count);
  const boroughs = data.map((d) => d.borough);

  if (topZonesChartInstance) topZonesChartInstance.destroy();

  topZonesChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Pickup Trips",
          data: counts,
          backgroundColor: "rgba(54, 162, 235, 0.7)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: { display: false },
        tooltip: {
          callbacks: {
            afterLabel: (context) => `Borough: ${boroughs[context.dataIndex]}`,
          },
        },
      },
      scales: {
        x: {
          ticks: { autoSkip: false, maxRotation: 60, minRotation: 30 },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: "Number of Trips" },
        },
      },
    },
  });
}


function renderBoroughPieChart(data) {
  const ctx = document.getElementById("boroughPieChart");
  if (!ctx) return;

  const labels = data.map((d) => d.borough);
  const counts = data.map((d) => d.trip_count);

  const palette = [
    "#36a2eb", "#ff6384", "#ffce56", "#4bc0c0", "#9966ff", "#ff9f40",
  ];

  if (boroughPieChartInstance) boroughPieChartInstance.destroy();

  boroughPieChartInstance = new Chart(ctx, {
    type: "pie",
    data: {
      labels,
      datasets: [
        {
          label: "Trips by Borough",
          data: counts,
          backgroundColor: labels.map((_, i) => palette[i % palette.length]),
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });
}



async function loadTopZones() {

  const data = await fetchJSON(`${API_BASE_URL}/trips/top-zones`);
  renderTopZonesChart(data);
}

async function loadBoroughTrips() {

  const data = await fetchJSON(`${API_BASE_URL}/trips/by-borough`);
  renderBoroughPieChart(data);
}

async function initCharts() {
  try {
    setStatus("Loading data…");
    await Promise.all([loadTopZones(), loadBoroughTrips()]);
    setStatus("Data loaded.");
  } catch (err) {
    console.error(err);
    setStatus(
      "Could not load chart data. Is the Flask backend running on port 5000?",
      true
    );
  }
}


window.UMDE = window.UMDE || {};
window.UMDE.loadTopZones = loadTopZones;
window.UMDE.loadBoroughTrips = loadBoroughTrips;
window.UMDE.API_BASE_URL = API_BASE_URL;
window.UMDE.fetchJSON = fetchJSON;
window.UMDE.setStatus = setStatus;

document.addEventListener("DOMContentLoaded", initCharts);