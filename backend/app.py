from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "urban_mobility"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "1234")
    )

# Endpoint 1: Top pickup zones by trip volume
@app.route('/trips/top-zones', methods=['GET'])
def top_zones():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT z.zone, z.borough, COUNT(*) as trip_count
        FROM trips t
        JOIN zones z ON t.pu_location_id = z.location_id
        GROUP BY z.zone, z.borough
        ORDER BY trip_count DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"zone": row[0], "borough": row[1], "trip_count": row[2]}
        for row in rows
    ])

# Endpoint 2: Trips grouped by time of day
@app.route('/trips/by-time', methods=['GET'])
def trips_by_time():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT tf.time_of_day, COUNT(*) as trip_count
        FROM trip_features tf
        GROUP BY tf.time_of_day
        ORDER BY trip_count DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"time_of_day": row[0], "trip_count": row[1]}
        for row in rows
    ])

# Endpoint 3: Average fare per borough
@app.route('/trips/average-fare', methods=['GET'])
def average_fare():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT z.borough, ROUND(AVG(t.fare_amount)::numeric, 2) as avg_fare
        FROM trips t
        JOIN zones z ON t.pu_location_id = z.location_id
        GROUP BY z.borough
        ORDER BY avg_fare DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"borough": row[0], "avg_fare": float(row[1])}
        for row in rows
    ])

# Endpoint 4: Trip count per borough
@app.route('/trips/by-borough', methods=['GET'])
def trips_by_borough():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT z.borough, COUNT(*) as trip_count
        FROM trips t
        JOIN zones z ON t.pu_location_id = z.location_id
        GROUP BY z.borough
        ORDER BY trip_count DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"borough": row[0], "trip_count": row[1]}
        for row in rows
    ])

if __name__ == "__main__":
    app.run(debug=True)