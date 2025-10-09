-- MSA Dashboard - PostgreSQL Schema with TimescaleDB
-- Time-series optimized schema for military situational awareness data

-- Enable TimescaleDB extension (if using TimescaleDB)
-- CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enable PostGIS extension for geospatial data (optional)
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- Create ENUM types
CREATE TYPE risk_level AS ENUM ('green', 'amber', 'red');
CREATE TYPE unit_type AS ENUM ('infantry', 'armor', 'artillery', 'recon', 'support', 'command');
CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical', 'emergency');
CREATE TYPE mission_phase AS ENUM ('planning', 'preparation', 'execution', 'consolidation', 'completed');
CREATE TYPE user_role AS ENUM ('commander', 'health_officer', 'operations_analyst');

-- Units table (current state)
CREATE TABLE units (
    unit_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit_type unit_type NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    altitude DOUBLE PRECISION,
    heading DOUBLE PRECISION CHECK (heading >= 0 AND heading <= 360),
    speed DOUBLE PRECISION CHECK (speed >= 0),
    status risk_level DEFAULT 'green',
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for units
CREATE INDEX idx_units_status ON units(status);
CREATE INDEX idx_units_type ON units(unit_type);
CREATE INDEX idx_units_last_seen ON units(last_seen);
CREATE INDEX idx_units_location ON units(latitude, longitude);

-- Health metrics table (time-series)
CREATE TABLE health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id VARCHAR(50) NOT NULL REFERENCES units(unit_id) ON DELETE CASCADE,
    heart_rate INTEGER CHECK (heart_rate >= 30 AND heart_rate <= 220),
    spo2 DOUBLE PRECISION CHECK (spo2 >= 0 AND spo2 <= 100),
    stress_index DOUBLE PRECISION CHECK (stress_index >= 0 AND stress_index <= 100),
    body_temperature DOUBLE PRECISION CHECK (body_temperature >= 30 AND body_temperature <= 45),
    risk_level risk_level DEFAULT 'green',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization (TimescaleDB)
-- SELECT create_hypertable('health_metrics', 'timestamp', chunk_time_interval => INTERVAL '1 hour');

-- Create indexes for health metrics
CREATE INDEX idx_health_unit_time ON health_metrics(unit_id, timestamp DESC);
CREATE INDEX idx_health_risk ON health_metrics(risk_level);
CREATE INDEX idx_health_timestamp ON health_metrics(timestamp DESC);

-- Logistics status table (time-series)
CREATE TABLE logistics_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id VARCHAR(50) NOT NULL REFERENCES units(unit_id) ON DELETE CASCADE,
    ammunition_pct DOUBLE PRECISION NOT NULL CHECK (ammunition_pct >= 0 AND ammunition_pct <= 100),
    fuel_pct DOUBLE PRECISION NOT NULL CHECK (fuel_pct >= 0 AND fuel_pct <= 100),
    medical_supplies_pct DOUBLE PRECISION NOT NULL CHECK (medical_supplies_pct >= 0 AND medical_supplies_pct <= 100),
    food_water_pct DOUBLE PRECISION NOT NULL CHECK (food_water_pct >= 0 AND food_water_pct <= 100),
    risk_level risk_level DEFAULT 'green',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable (TimescaleDB)
-- SELECT create_hypertable('logistics_status', 'timestamp', chunk_time_interval => INTERVAL '1 hour');

-- Create indexes for logistics
CREATE INDEX idx_logistics_unit_time ON logistics_status(unit_id, timestamp DESC);
CREATE INDEX idx_logistics_risk ON logistics_status(risk_level);

-- Weather data table (time-series)
CREATE TABLE weather_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id VARCHAR(50) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    altitude DOUBLE PRECISION,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL CHECK (humidity >= 0 AND humidity <= 100),
    wind_speed DOUBLE PRECISION NOT NULL CHECK (wind_speed >= 0),
    wind_direction DOUBLE PRECISION NOT NULL CHECK (wind_direction >= 0 AND wind_direction <= 360),
    visibility DOUBLE PRECISION NOT NULL CHECK (visibility >= 0),
    pressure DOUBLE PRECISION,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable (TimescaleDB)
-- SELECT create_hypertable('weather_data', 'timestamp', chunk_time_interval => INTERVAL '6 hours');

-- Create indexes for weather data
CREATE INDEX idx_weather_station_time ON weather_data(station_id, timestamp DESC);
CREATE INDEX idx_weather_location ON weather_data(latitude, longitude);

-- Threat detections table
CREATE TABLE threat_detections (
    detection_id VARCHAR(50) PRIMARY KEY,
    source_unit_id VARCHAR(50) NOT NULL,
    threat_type VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    altitude DOUBLE PRECISION,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    severity alert_severity NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for threat detections
CREATE INDEX idx_threat_severity_time ON threat_detections(severity, timestamp DESC);
CREATE INDEX idx_threat_location ON threat_detections(latitude, longitude);
CREATE INDEX idx_threat_source ON threat_detections(source_unit_id);

-- Alerts table
CREATE TABLE alerts (
    alert_id VARCHAR(50) PRIMARY KEY,
    unit_id VARCHAR(50) REFERENCES units(unit_id) ON DELETE SET NULL,
    alert_type VARCHAR(100) NOT NULL,
    severity alert_severity NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for alerts
CREATE INDEX idx_alerts_severity_time ON alerts(severity, timestamp DESC);
CREATE INDEX idx_alerts_unit ON alerts(unit_id);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX idx_alerts_resolved ON alerts(resolved);

-- Missions table
CREATE TABLE missions (
    mission_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    phase mission_phase DEFAULT 'planning',
    progress_pct DOUBLE PRECISION DEFAULT 0.0 CHECK (progress_pct >= 0 AND progress_pct <= 100),
    start_time TIMESTAMPTZ,
    estimated_end_time TIMESTAMPTZ,
    actual_end_time TIMESTAMPTZ,
    assigned_units JSONB, -- Array of unit IDs
    objectives JSONB, -- Array of objectives
    status risk_level DEFAULT 'green',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for missions
CREATE INDEX idx_missions_phase ON missions(phase);
CREATE INDEX idx_missions_status ON missions(status);
CREATE INDEX idx_missions_assigned_units ON missions USING GIN(assigned_units);

-- Mission objectives table
CREATE TABLE mission_objectives (
    objective_id VARCHAR(50) PRIMARY KEY,
    mission_id VARCHAR(50) NOT NULL REFERENCES missions(mission_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Users table for authentication
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    full_name VARCHAR(200),
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Create indexes for users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_units_updated_at BEFORE UPDATE ON units
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_missions_updated_at BEFORE UPDATE ON missions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW units_latest_status AS
SELECT 
    u.*,
    h.heart_rate,
    h.spo2,
    h.stress_index,
    h.risk_level as health_risk,
    l.ammunition_pct,
    l.fuel_pct,
    l.medical_supplies_pct,
    l.risk_level as logistics_risk
FROM units u
LEFT JOIN LATERAL (
    SELECT * FROM health_metrics hm 
    WHERE hm.unit_id = u.unit_id 
    ORDER BY timestamp DESC LIMIT 1
) h ON true
LEFT JOIN LATERAL (
    SELECT * FROM logistics_status ls 
    WHERE ls.unit_id = u.unit_id 
    ORDER BY timestamp DESC LIMIT 1
) l ON true;

-- View for active alerts
CREATE VIEW active_alerts AS
SELECT * FROM alerts 
WHERE resolved = FALSE 
ORDER BY severity DESC, timestamp DESC;

-- View for critical status units
CREATE VIEW critical_units AS
SELECT unit_id, name, unit_type, status, last_seen
FROM units 
WHERE status = 'red' OR last_seen < NOW() - INTERVAL '5 minutes';

-- Continuous aggregates for TimescaleDB (uncomment if using TimescaleDB)
/*
-- Hourly health metrics aggregation
CREATE MATERIALIZED VIEW health_metrics_hourly
WITH (timescaledb.continuous) AS
SELECT 
    unit_id,
    time_bucket('1 hour', timestamp) AS bucket,
    AVG(heart_rate) as avg_heart_rate,
    MAX(heart_rate) as max_heart_rate,
    MIN(heart_rate) as min_heart_rate,
    AVG(spo2) as avg_spo2,
    MIN(spo2) as min_spo2,
    AVG(stress_index) as avg_stress_index,
    MAX(stress_index) as max_stress_index
FROM health_metrics
GROUP BY unit_id, bucket;

-- Add refresh policy
SELECT add_continuous_aggregate_policy('health_metrics_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
*/

-- Data retention policies (TimescaleDB)
/*
-- Keep raw health data for 30 days
SELECT add_retention_policy('health_metrics', INTERVAL '30 days');

-- Keep raw logistics data for 60 days
SELECT add_retention_policy('logistics_status', INTERVAL '60 days');

-- Keep weather data for 90 days
SELECT add_retention_policy('weather_data', INTERVAL '90 days');
*/

-- Insert sample data for testing
INSERT INTO units (unit_id, name, unit_type, latitude, longitude, status) VALUES
('UNIT-001', 'Alpha Squad', 'infantry', 39.9334, 32.8597, 'green'),
('UNIT-002', 'Bravo Team', 'recon', 39.9400, 32.8650, 'green'),
('UNIT-003', 'Charlie Tank', 'armor', 39.9280, 32.8500, 'amber'),
('UNIT-004', 'Delta Support', 'support', 39.9350, 32.8620, 'green');

-- Insert sample missions
INSERT INTO missions (mission_id, name, phase, progress_pct, assigned_units) VALUES
('MISSION-001', 'Operation Thunder', 'execution', 65.0, '["UNIT-001", "UNIT-002"]'),
('MISSION-002', 'Recon Alpha', 'preparation', 25.0, '["UNIT-002"]');

-- Insert sample users
INSERT INTO users (user_id, username, email, hashed_password, full_name, role) VALUES
('USER-001', 'commander1', 'commander@msa.mil', '$2b$12$example_hash', 'Major John Smith', 'commander'),
('USER-002', 'medic1', 'medic@msa.mil', '$2b$12$example_hash', 'Captain Sarah Johnson', 'health_officer'),
('USER-003', 'analyst1', 'analyst@msa.mil', '$2b$12$example_hash', 'Lieutenant Mike Davis', 'operations_analyst');