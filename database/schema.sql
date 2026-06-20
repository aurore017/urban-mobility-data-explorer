CREATE TABLE vendors (
    vendor_id SMALLINT PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL
);

INSERT INTO vendors (vendor_id, vendor_name) VALUES
(1, 'Creative Mobile Technologies, LLC'),
(2, 'Curb Mobility, LLC'),
(6, 'Myle Technologies Inc'),
(7, 'Helix');

CREATE TABLE rate_codes (
    rate_code_id SMALLINT PRIMARY KEY,
    description VARCHAR(50) NOT NULL
);

INSERT INTO rate_codes (rate_code_id, description) VALUES
(1, 'Standard rate'),
(2, 'JFK'),
(3, 'Newark'),
(4, 'Nassau or Westchester'),
(5, 'Negotiated fare'),
(6, 'Group ride'),
(99, 'Null/unknown');

CREATE TABLE payment_types (
    payment_type_id SMALLINT PRIMARY KEY,
    description VARCHAR(50) NOT NULL
);

INSERT INTO payment_types (payment_type_id, description) VALUES
(0, 'Flex Fare trip'),
(1, 'Credit card'),
(2, 'Cash'),
(3, 'No charge'),
(4, 'Dispute'),
(5, 'Unknown'),
(6, 'Voided trip');

CREATE TABLE zones (
    location_id SMALLINT PRIMARY KEY,
    borough VARCHAR(50) NOT NULL,
    zone VARCHAR(150) NOT NULL,
    service_zone VARCHAR(50)
);

CREATE TABLE zone_geometry (
    location_id SMALLINT PRIMARY KEY REFERENCES zones(location_id),
    shape_leng DOUBLE PRECISION,
    shape_area DOUBLE PRECISION,
    geometry JSONB NOT NULL
);

CREATE TABLE trips (
    trip_id BIGSERIAL PRIMARY KEY,
    vendor_id SMALLINT REFERENCES vendors(vendor_id),
    tpep_pickup_datetime TIMESTAMP NOT NULL,
    tpep_dropoff_datetime TIMESTAMP NOT NULL,
    passenger_count SMALLINT,
    trip_distance NUMERIC(8,2),
    rate_code_id SMALLINT REFERENCES rate_codes(rate_code_id),
    store_and_fwd_flag CHAR(1),
    pu_location_id SMALLINT NOT NULL REFERENCES zones(location_id),
    do_location_id SMALLINT NOT NULL REFERENCES zones(location_id),
    payment_type_id SMALLINT REFERENCES payment_types(payment_type_id),
    fare_amount NUMERIC(8,2) NOT NULL,
    extra NUMERIC(6,2),
    mta_tax NUMERIC(6,2),
    tip_amount NUMERIC(8,2),
    tolls_amount NUMERIC(8,2),
    improvement_surcharge NUMERIC(6,2),
    total_amount NUMERIC(8,2) NOT NULL,
    congestion_surcharge NUMERIC(6,2),
    airport_fee NUMERIC(6,2),
    cbd_congestion_fee NUMERIC(6,2),

    CONSTRAINT chk_trip_distance_range CHECK (trip_distance IS NULL OR (trip_distance >= 0 AND trip_distance <= 200)),
    CONSTRAINT chk_fare_amount_non_negative CHECK (fare_amount >= 0),
    CONSTRAINT chk_total_amount_non_negative CHECK (total_amount >= 0),
    CONSTRAINT chk_passenger_count_range CHECK (passenger_count IS NULL OR (passenger_count >= 0 AND passenger_count <= 9)),
    CONSTRAINT chk_dropoff_after_pickup CHECK (tpep_dropoff_datetime >= tpep_pickup_datetime),
    CONSTRAINT chk_store_and_fwd_flag_valid CHECK (store_and_fwd_flag IS NULL OR store_and_fwd_flag IN ('Y','N')),

    CONSTRAINT uq_trip_natural_key UNIQUE (vendor_id, tpep_pickup_datetime, tpep_dropoff_datetime, pu_location_id, do_location_id)
);

CREATE TABLE trip_features (
    trip_id BIGINT PRIMARY KEY REFERENCES trips(trip_id) ON DELETE CASCADE,
    trip_duration_minutes NUMERIC(8,2),
    avg_speed_mph NUMERIC(8,2),
    fare_per_mile NUMERIC(8,2),
    time_of_day VARCHAR(20),
    is_weekend BOOLEAN
);

CREATE TABLE excluded_records_log (
    log_id BIGSERIAL PRIMARY KEY,
    source_row_reference VARCHAR(100),
    reason VARCHAR(255) NOT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trips_pickup_datetime ON trips(tpep_pickup_datetime);
CREATE INDEX idx_trips_pu_location ON trips(pu_location_id);
CREATE INDEX idx_trips_do_location ON trips(do_location_id);
CREATE INDEX idx_trips_payment_type ON trips(payment_type_id);
CREATE INDEX idx_zones_borough ON zones(borough);

CREATE INDEX idx_trips_pu_do_pair ON trips(pu_location_id, do_location_id);