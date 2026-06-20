import psycopg2
import csv
import os
from psycopg2.extras import execute_values

import sys

if len(sys.argv) != 2:
    print("usage: python3 load_data.py cleaned_tripdata.csv")
    sys.exit(1)
BATCH_SIZE = 5000
csv_path = sys.argv[1]
host = os.environ.get("DB_HOST", "localhost")
port = os.environ.get("DB_PORT", "5432")
dbname = os.environ.get("DB_NAME", "urban_mobility")
user = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "1234")

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password,
)
cur = conn.cursor()

trips_cols = [
    "vendor_id", "tpep_pickup_datetime", "tpep_dropoff_datetime",
    "passenger_count", "trip_distance", "rate_code_id",
    "store_and_fwd_flag", "pu_location_id", "do_location_id",
    "payment_type_id", "fare_amount", "extra", "mta_tax",
    "tip_amount", "tolls_amount", "improvement_surcharge",
    "total_amount", "congestion_surcharge", "airport_fee",
    "cbd_congestion_fee",
]

csv_cols_for_trips = [
    "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
    "passenger_count", "trip_distance", "RatecodeID",
    "store_and_fwd_flag", "PULocationID", "DOLocationID",
    "payment_type", "fare_amount", "extra", "mta_tax",
    "tip_amount", "tolls_amount", "improvement_surcharge",
    "total_amount", "congestion_surcharge", "airport_fee",
    "cbd_congestion_fee",
]

features_cols = [
    "trip_duration_minutes", "avg_speed_mph", "fare_per_mile",
    "time_of_day", "is_weekend",
]

csv_cols_for_features = [
    "trip_duration_mins", "speed_mph", "fare_per_mile",
    "time_of_day", "is_weekend",
]

def clean(value):
    if value in (None, "", "NaN", "nan"):
        return None
    return value

trips_insert_sql = (
    "INSERT INTO trips (" + ", ".join(trips_cols) + ") VALUES %s RETURNING trip_id"
)

features_insert_sql = (
    "INSERT INTO trip_features (trip_id, " + ", ".join(features_cols) + ") VALUES %s"
)

inserted = 0
skipped = 0

def process_batch(rows):
    global inserted, skipped

    trip_rows = []
    feature_rows = []

    for row in rows:
        trip_rows.append(tuple(clean(row.get(col)) for col in csv_cols_for_trips))
        feature_rows.append(tuple(clean(row.get(col)) for col in csv_cols_for_features))
    fixed_feature_rows = []
    for fr in feature_rows:
        fr = list(fr)
        if fr[-1] is not None:
            fr[-1] = fr[-1] in ("1", "True", "true")
        fixed_feature_rows.append(tuple(fr))
    feature_rows = fixed_feature_rows
    try:
        returned_ids = execute_values(cur, trips_insert_sql, trip_rows, fetch=True)
        trip_ids = [item[0] for item in returned_ids]

        feature_data = [(tid,) + fr for tid, fr in zip(trip_ids, feature_rows)]
        execute_values(cur, features_insert_sql, feature_data)

        conn.commit()
        inserted += len(rows)
    except Exception:
        conn.rollback()

        for index, row in enumerate(rows):
            try:
                result = execute_values(cur, trips_insert_sql, [trip_rows[index]], fetch=True)
                trip_id = result[0][0]
                execute_values(cur, features_insert_sql, [(trip_id,) + feature_rows[index]])
                conn.commit()
                inserted += 1
            except Exception as err:
                conn.rollback()
                skipped += 1
                cur.execute(
                    "INSERT INTO excluded_records_log (source_row_reference, reason) VALUES (%s, %s)",
                    (str(row)[:100], str(err)[:200])
                )
                conn.commit()
batch = []

with open(csv_path, newline="", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
        batch.append(row)

        if len(batch) >= BATCH_SIZE:
            process_batch(batch)
            print(f"{inserted} inserted, {skipped} skipped so far")
            batch = []

    if batch:
        process_batch(batch)                

cur.close()
conn.close()

print(f"done: {inserted} inserted, {skipped} skipped, check excluded_records_log for details")