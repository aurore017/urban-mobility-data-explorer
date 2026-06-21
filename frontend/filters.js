// Step 1: Fetch boroughs and build the dropdown
async function loadBoroughFilter() {
  const data = [
  { borough: "Manhattan", trip_count: 5000 },
  { borough: "Brooklyn", trip_count: 3000 },
  { borough: "Queens", trip_count: 1500 }
];

  // data looks like: [{ borough: "Manhattan", trip_count: 12345 }, ...]
  const select = document.createElement('select');
  select.id = 'borough-filter';

  const defaultOption = document.createElement('option');
  defaultOption.value = '';
  defaultOption.textContent = 'All Boroughs';
  select.appendChild(defaultOption);

  data.forEach(row => {
    const option = document.createElement('option');
    option.value = row.borough;
    option.textContent = row.borough;
    select.appendChild(option);
  });

  document.getElementById('filter-controls').appendChild(select);
}

loadBoroughFilter();

// Step 2: Fetch time-of-day options and build the dropdown
async function loadTimeOfDayFilter() {
  // Mock data for now — matches what /trips/by-time will eventually return
  const data = [
    { time_of_day: "morning", trip_count: 4000 },
    { time_of_day: "afternoon", trip_count: 3500 },
    { time_of_day: "evening", trip_count: 5000 },
    { time_of_day: "night", trip_count: 1200 }
  ];

  const select = document.createElement('select');
  select.id = 'time-of-day-filter';

  const defaultOption = document.createElement('option');
  defaultOption.value = '';
  defaultOption.textContent = 'All Times of Day';
  select.appendChild(defaultOption);

  data.forEach(row => {
    const option = document.createElement('option');
    option.value = row.time_of_day;
    option.textContent = row.time_of_day;
    select.appendChild(option);
  });

  document.getElementById('filter-controls').appendChild(select);
}

loadTimeOfDayFilter();