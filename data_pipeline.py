import pandas as pd
import numpy as np
import geopandas as gpd

# ── Load Data ──────────────────────────────────────────
trips = pd.read_csv('yellow_tripdata_2019-01.csv')
zones = pd.read_csv('taxi_zone_lookup.csv')
geo_zones = gpd.read_file('taxi_zones.shp')

# ── Quick Inspection ───────────────────────────────────
print("=== TRIPS ===")
print(trips.shape)
print(trips.dtypes)
print(trips.head(3))

print("\n=== ZONES ===")
print(zones.shape)
print(zones.head(3))

print("\n=== GEO ZONES ===")
print(geo_zones.shape)
print(geo_zones.head(3))

# ── Missing Values ─────────────────────────────────────
print("=== MISSING VALUES IN TRIPS ===")
print(trips.isnull().sum())

print("\n=== MISSING VALUES IN ZONES ===")
print(zones.isnull().sum())

# ── Duplicates ─────────────────────────────────────────
print("=== DUPLICATES IN TRIPS ===")
print(trips.duplicated().sum())

print("\n=== DUPLICATES IN ZONES ===")
print(zones.duplicated().sum())

# ── Investigate missing zones ──────────────────────────
print("=== ZONES WITH MISSING VALUES ===")
print(zones[zones.isnull().any(axis=1)])

# ── Clean Zones missing values ─────────────────────────
zones['Borough'] = zones['Borough'].fillna('Unknown')
zones['Zone'] = zones['Zone'].fillna('Unknown')
zones['service_zone'] = zones['service_zone'].fillna('Unknown')

print("=== ZONES AFTER CLEANING ===")
print(zones[zones['LocationID'].isin([264, 265])])

# ── Fix congestion_surcharge missing values ────────────
trips['congestion_surcharge'] = trips['congestion_surcharge'].fillna(0.0)

print("\n=== CONGESTION SURCHARGE MISSING AFTER FIX ===")
print(trips['congestion_surcharge'].isnull().sum())

# ── Convert timestamps ─────────────────────────────────
trips['tpep_pickup_datetime'] = pd.to_datetime(trips['tpep_pickup_datetime'])
trips['tpep_dropoff_datetime'] = pd.to_datetime(trips['tpep_dropoff_datetime'])

print("=== TIMESTAMP TYPES AFTER CONVERSION ===")
print(trips[['tpep_pickup_datetime', 'tpep_dropoff_datetime']].dtypes)

print("\n=== SAMPLE TIMESTAMPS ===")
print(trips[['tpep_pickup_datetime', 'tpep_dropoff_datetime']].head(3))

# ── Outlier Detection & Exclusion Log ─────────────────
exclusion_log = []

# 1. Trips where dropoff is before or equal to pickup
mask1 = trips['tpep_dropoff_datetime'] <= trips['tpep_pickup_datetime']
exclusion_log.append({'reason': 'dropoff <= pickup time', 'count': mask1.sum()})

# 2. Trip distance zero or negative
mask2 = trips['trip_distance'] <= 0
exclusion_log.append({'reason': 'trip_distance <= 0', 'count': mask2.sum()})

# 3. Fare amount zero or negative
mask3 = trips['fare_amount'] <= 0
exclusion_log.append({'reason': 'fare_amount <= 0', 'count': mask3.sum()})

# 4. Passenger count zero or more than 6
mask4 = (trips['passenger_count'] <= 0) | (trips['passenger_count'] > 6)
exclusion_log.append({'reason': 'passenger_count out of range (<=0 or >6)', 'count': mask4.sum()})

# 5. Trips outside January 2019
mask5 = (trips['tpep_pickup_datetime'].dt.year != 2019) | (trips['tpep_pickup_datetime'].dt.month != 1)
exclusion_log.append({'reason': 'pickup date outside January 2019', 'count': mask5.sum()})

# 6. Trip duration more than 24 hours
duration = (trips['tpep_dropoff_datetime'] - trips['tpep_pickup_datetime']).dt.total_seconds() / 3600
mask6 = duration > 24
exclusion_log.append({'reason': 'trip duration > 24 hours', 'count': mask6.sum()})

# Print the log
print("=== EXCLUSION LOG ===")
for entry in exclusion_log:
    print(f"{entry['reason']}: {entry['count']} records")

    # ── Combine all bad records mask ───────────────────────
bad_records = mask1 | mask2 | mask3 | mask4 | mask5 | mask6

print(f"\nTotal records before cleaning: {len(trips)}")
print(f"Total bad records to remove: {bad_records.sum()}")

# ── Remove bad records ─────────────────────────────────
trips = trips[~bad_records].reset_index(drop=True)

print(f"Total records after cleaning: {len(trips)}")

# ── Save exclusion log to CSV ──────────────────────────
exclusion_df = pd.DataFrame(exclusion_log)
exclusion_df.to_csv('exclusion_log.csv', index=False)
print("\nExclusion log saved to exclusion_log.csv ✅")

# ── Join zones for pickup location ─────────────────────
trips = trips.merge(zones, left_on='PULocationID', right_on='LocationID', how='left')
trips = trips.rename(columns={
    'Borough': 'PU_Borough',
    'Zone': 'PU_Zone',
    'service_zone': 'PU_service_zone'
})
trips = trips.drop(columns=['LocationID'])

# ── Join zones for dropoff location ────────────────────
trips = trips.merge(zones, left_on='DOLocationID', right_on='LocationID', how='left')
trips = trips.rename(columns={
    'Borough': 'DO_Borough',
    'Zone': 'DO_Zone',
    'service_zone': 'DO_service_zone'
})
trips = trips.drop(columns=['LocationID'])

print("=== AFTER JOINING ZONES ===")
print(f"Shape: {trips.shape}")
print(trips[['PULocationID', 'PU_Borough', 'PU_Zone', 'DOLocationID', 'DO_Borough', 'DO_Zone']].head(3))

# ── Feature Engineering ────────────────────────────────

# 1. Trip duration in minutes
trips['trip_duration_mins'] = (
    trips['tpep_dropoff_datetime'] - trips['tpep_pickup_datetime']
).dt.total_seconds() / 60

# 2. Speed in mph
trips['speed_mph'] = trips['trip_distance'] / (trips['trip_duration_mins'] / 60)

# 3. Fare per mile
trips['fare_per_mile'] = trips['fare_amount'] / trips['trip_distance']

# 4. Time of day bucket
def time_of_day(hour):
    if 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    elif 18 <= hour < 22:
        return 'Evening'
    else:
        return 'Night'

trips['time_of_day'] = trips['tpep_pickup_datetime'].dt.hour.apply(time_of_day)

# 5. Is weekend
trips['is_weekend'] = trips['tpep_pickup_datetime'].dt.dayofweek.apply(
    lambda x: 1 if x >= 5 else 0
)

print("=== FEATURE ENGINEERING ===")
print(trips[['trip_duration_mins', 'speed_mph', 'fare_per_mile', 'time_of_day', 'is_weekend']].head(5))
print(f"\nNew shape: {trips.shape}")

# ── Save final cleaned dataset ─────────────────────────
trips.to_csv('cleaned_tripdata.csv', index=False)
print("✅ Cleaned dataset saved to cleaned_tripdata.csv")
print(f"Final shape: {trips.shape}")

print("\n=== FINAL COLUMN LIST ===")
for col in trips.columns:
    print(f"  - {col}")