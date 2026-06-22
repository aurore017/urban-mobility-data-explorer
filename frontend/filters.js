async function loadBoroughFilter() {
  const data = await window.UMDE.fetchJSON(`${window.UMDE.API_BASE_URL}/trips/by-borough`);

  const select = document.getElementById('borough-filter');

  data.forEach(row => {
    const option = document.createElement('option');
    option.value = row.borough;
    option.textContent = row.borough;
    select.appendChild(option);
  });
}

async function loadTimeOfDayFilter() {
  const data = await window.UMDE.fetchJSON(`${window.UMDE.API_BASE_URL}/trips/by-time`);

  const select = document.getElementById('time-of-day-filter');

  data.forEach(row => {
    const option = document.createElement('option');
    option.value = row.time_of_day;
    option.textContent = row.time_of_day;
    select.appendChild(option);
  });

  renderTimeOfDayChart(data);
}

function renderTimeOfDayChart(data) {
  const ctx = document.getElementById("fareByTimeChart");
  if (!ctx) return;

  const labels = data.map(d => d.time_of_day);
  const counts = data.map(d => d.trip_count);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Trips by Time of Day",
        data: counts,
        backgroundColor: "rgba(255, 159, 64, 0.7)",
        borderColor: "rgba(255, 159, 64, 1)",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: "Number of Trips" }
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadBoroughFilter();
  await loadTimeOfDayFilter();
});