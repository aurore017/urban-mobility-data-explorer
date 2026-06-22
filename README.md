# urban-mobility-data-explorer
# Urban Mobility Data Explorer

A fullstack web application for exploring NYC Taxi & Limousine Commission (TLC) trip data. Built as part of a data engineering and visualization assignment, this project allows users to interactively explore urban mobility patterns across New York City's five boroughs.

---

## Team

| Name | GitHub | Role |
|------|--------|------|
| Aurore | @aurore017 | Team Lead / Data cleaning and intergration |
|Nziza|@nziza21| Backend|
|Lorris| @LorrisHira| Database|
| Bruce | @bmanzi-glitch | Frontend — Dashboard layout, bar chart, pie chart |
| Huguette | | Frontend — Filters, time-of-day chart |

---

## Project Structure

```
urban-mobility-data-explorer/
├── backend/
│   ├── app.py                  # Flask API server (4 endpoints)
│   └── ranking_algorithm.py    # Custom DSA implementation
├── database/
│   ├── schema.sql              # Creates all tables and indexes
│   ├── zone_seed_data.sql      # Seeds 265 NYC taxi zones
│   └── load_data.py            # Loads cleaned trip data into Postgres
├── frontend/
│   ├── index.html              # Main dashboard page
│   ├── charts.js               # Bar chart (top zones) + pie chart (boroughs)
│   ├── filters.js              # Dropdowns + time-of-day chart
│   └── styles.css              # Dark taxi-meter theme
├── docs/
│   └── architecture_diagram.png
├── data_pipeline.py            # Cleans raw CSV → cleaned_tripdata.csv
├── feature_engineering.py      # Derives trip features (time of day, etc.)
├── exclusion_log.csv           # Log of records excluded during cleaning
├── .gitignore
└── README.md
```

---

## Prerequisites

Make sure you have the following installed before starting:

- Python 3.10 or higher
- PostgreSQL 15 or higher (running on port 5432)
- Git

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/aurore017/urban-mobility-data-explorer.git
cd urban-mobility-data-explorer
```

### 2. Install Python dependencies

```bash
pip install flask flask-cors psycopg2-binary pandas pyarrow geopandas
```

### 3. Get the raw data file

The raw trip data file (`yellow_tripdata_small.csv`) is not included in the repository because it is too large for GitHub. You must obtain it from a team member or download a sample from the [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) page.

Place it in the repo root:
```
urban-mobility-data-explorer/
└── yellow_tripdata_small.csv   ← place here
```

### 4. Run the data pipeline

This cleans the raw data and produces `cleaned_tripdata.csv`:

```bash
python data_pipeline.py
```

### 5. Set up the PostgreSQL database

Make sure PostgreSQL is running, then:

```bash
# On Windows (adjust path to match your Postgres version)
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE urban_mobility;"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d urban_mobility -f database/schema.sql
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d urban_mobility -f database/zone_seed_data.sql

# On Mac/Linux
psql -U postgres -c "CREATE DATABASE urban_mobility;"
psql -U postgres -d urban_mobility -f database/schema.sql
psql -U postgres -d urban_mobility -f database/zone_seed_data.sql
```

Default credentials (set during Postgres install):
- **User:** postgres
- **Password:** 1234
- **Port:** 5432
- **Database:** urban_mobility

To use different credentials, set these environment variables before running the backend:

```bash
# Windows PowerShell
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "urban_mobility"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "your_password"
```

### 6. Load the trip data

```bash
python database/load_data.py cleaned_tripdata.csv
```

This may take a few minutes depending on dataset size.

### 7. Verify the database

```bash
# Windows
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d urban_mobility -c "SELECT COUNT(*) FROM trips;"

# Mac/Linux
psql -U postgres -d urban_mobility -c "SELECT COUNT(*) FROM trips;"
```

You should see a non-zero row count.

---

## Running the Application

### Start the backend (Terminal 1)

```bash
python backend/app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

Leave this terminal running.

### Start the frontend (Terminal 2)

```bash
cd frontend
python -m http.server 8000
```

### Open the dashboard

Go to: **http://localhost:8000**

> ⚠️ Do NOT open `index.html` by double-clicking it. Always use `http://localhost:8000` — opening as a `file://` URL causes CORS errors that prevent the charts from loading.

---

## API Endpoints

All endpoints are served by Flask on `http://localhost:5000`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trips/top-zones` | Top 10 pickup zones by trip volume |
| GET | `/trips/by-borough` | Trip count grouped by borough |
| GET | `/trips/by-time` | Trip count grouped by time of day |
| GET | `/trips/average-fare` | Average fare amount per borough |

### Example response — `/trips/by-borough`

```json
[
  { "borough": "Manhattan", "trip_count": 45231 },
  { "borough": "Queens", "trip_count": 12847 },
  { "borough": "Brooklyn", "trip_count": 8934 }
]
```

---

## Features

- **Top Pickup Zones** — horizontal bar chart of the 10 busiest pickup zones, with borough shown on hover
- **Trips by Borough** — pie chart showing the distribution of trips across NYC's five boroughs
- **Trips by Time of Day** — bar chart breaking down trip volume by morning, afternoon, evening, and night
- **Filters** — borough and time-of-day dropdowns (frontend controls ready; backend filter params to be added)
- **Dark taxi-meter theme** — amber accent colors on a dark instrument-panel background, inspired by NYC medallion cabs

---

## Database Schema

| Table | Description |
|-------|-------------|
| `trips` | Core fact table — one row per trip, with fares, distances, timestamps, location IDs |
| `zones` | Dimension table — 265 NYC taxi zones with borough and service zone |
| `trip_features` | Derived features — time of day bucket, trip duration, speed, etc. |

---

## Data Cleaning Summary

Raw data issues identified and resolved:

- Removed trips with negative or zero fare amounts
- Removed trips with impossible distances (> 200 miles or exactly 0)
- Removed trips with duration under 1 minute or over 24 hours
- Standardized all timestamps to UTC
- Dropped duplicate trip records
- Excluded records with missing pickup or dropoff location IDs

All excluded records are logged in `exclusion_log.csv` with the reason for exclusion.

---

## Derived Features (Feature Engineering)

| Feature | Description | Source columns |
|---------|-------------|----------------|
| `time_of_day` | Morning / Afternoon / Evening / Night bucket | `tpep_pickup_datetime` |
| `trip_duration_min` | Duration in minutes | pickup and dropoff timestamps |
| `avg_speed_mph` | Average speed calculated from distance and duration | `trip_distance`, duration |

---

## Custom Algorithm

A custom ranking algorithm (`backend/ranking_algorithm.py`) is implemented without built-in sort libraries to rank pickup zones by trip volume. It uses an insertion-sort-based approach on trip count values.

**Time complexity:** O(n²) — acceptable for the top-10 use case where n is small  
**Space complexity:** O(n)

---

## Troubleshooting

**"Could not load chart data. Is the Flask backend running on port 5000?"**
- Make sure `python backend/app.py` is running in a separate terminal
- Visit `http://localhost:5000/trips/by-borough` directly — if you see a Flask error, the database isn't loaded yet
- Make sure you're opening the frontend via `http://localhost:8000`, not as a file

**`psycopg2.OperationalError: database "urban_mobility" does not exist`**
- Run Step 5 above to create and populate the database

**`psql` not recognized on Windows**
- Use the full path: `& "C:\Program Files\PostgreSQL\18\bin\psql.exe"`
- Or add `C:\Program Files\PostgreSQL\18\bin` to your system PATH

**Merge conflicts when pulling**
- Always run `git stash` before `git pull origin main`, then `git stash pop` after
- Never commit the `venv/` folder — it is gitignored

---

## Video Walkthrough

[Link to be added before submission]

---

## Architecture

See `docs/architecture_diagram.png` for the full system diagram.

**Stack:**
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Backend:** Python, Flask, flask-cors
- **Database:** PostgreSQL with psycopg2
- **Data pipeline:** pandas, geopandas, pyarrow
