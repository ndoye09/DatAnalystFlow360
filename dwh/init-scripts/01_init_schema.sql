-- Script d'initialisation du Data Warehouse
-- Création des schémas et tables

-- ========================================
-- SCHÉMAS
-- ========================================

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dim;
CREATE SCHEMA IF NOT EXISTS fact;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS metadata;

COMMENT ON SCHEMA staging IS 'Zone de staging pour les données brutes depuis le Data Lake';
COMMENT ON SCHEMA dim IS 'Tables de dimensions';
COMMENT ON SCHEMA fact IS 'Tables de faits';
COMMENT ON SCHEMA analytics IS 'Vues et agrégats pour l''analyse';
COMMENT ON SCHEMA metadata IS 'Métadonnées et traçabilité';

-- ========================================
-- TABLES DE MÉTADONNÉES
-- ========================================

CREATE TABLE IF NOT EXISTS metadata.etl_load_log (
    load_id SERIAL PRIMARY KEY,
    source_system VARCHAR(100),
    source_table VARCHAR(200),
    target_schema VARCHAR(100),
    target_table VARCHAR(200),
    load_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    load_end_time TIMESTAMP,
    rows_loaded INTEGER,
    load_status VARCHAR(50),
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS metadata.data_lineage (
    lineage_id SERIAL PRIMARY KEY,
    source_path VARCHAR(500),
    target_table VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS metadata.quality_checks (
    check_id SERIAL PRIMARY KEY,
    table_name VARCHAR(200),
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_type VARCHAR(100),
    check_result VARCHAR(50),
    details JSONB
);

-- ========================================
-- DIMENSION DATE
-- ========================================

CREATE TABLE IF NOT EXISTS dim.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    day_of_month INTEGER,
    day_of_year INTEGER,
    week_of_year INTEGER,
    month INTEGER,
    month_name VARCHAR(10),
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Fonction pour peupler la dimension date
CREATE OR REPLACE FUNCTION dim.populate_dim_date(start_date DATE, end_date DATE)
RETURNS void AS $$
DECLARE
    curr_date DATE := start_date;
BEGIN
    WHILE curr_date <= end_date LOOP
        INSERT INTO dim.dim_date (
            date_key,
            full_date,
            day_of_week,
            day_name,
            day_of_month,
            day_of_year,
            week_of_year,
            month,
            month_name,
            quarter,
            year,
            is_weekend
        ) VALUES (
            TO_CHAR(curr_date, 'YYYYMMDD')::INTEGER,
            curr_date,
            EXTRACT(DOW FROM curr_date)::INTEGER,
            TO_CHAR(curr_date, 'Day'),
            EXTRACT(DAY FROM curr_date)::INTEGER,
            EXTRACT(DOY FROM curr_date)::INTEGER,
            EXTRACT(WEEK FROM curr_date)::INTEGER,
            EXTRACT(MONTH FROM curr_date)::INTEGER,
            TO_CHAR(curr_date, 'Month'),
            EXTRACT(QUARTER FROM curr_date)::INTEGER,
            EXTRACT(YEAR FROM curr_date)::INTEGER,
            CASE WHEN EXTRACT(DOW FROM curr_date) IN (0, 6) THEN TRUE ELSE FALSE END
        ) ON CONFLICT (date_key) DO NOTHING;
        
        curr_date := curr_date + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Peupler la dimension date (2020-2030)
SELECT dim.populate_dim_date('2020-01-01'::DATE, '2030-12-31'::DATE);

-- ========================================
-- INDEX
-- ========================================

CREATE INDEX idx_dim_date_full_date ON dim.dim_date(full_date);
CREATE INDEX idx_dim_date_year_month ON dim.dim_date(year, month);
CREATE INDEX idx_etl_log_source ON metadata.etl_load_log(source_system, source_table);
CREATE INDEX idx_etl_log_timestamp ON metadata.etl_load_log(load_start_time);

-- ========================================
-- VUES
-- ========================================

CREATE OR REPLACE VIEW metadata.v_recent_loads AS
SELECT 
    source_system,
    source_table,
    target_table,
    load_start_time,
    load_end_time,
    EXTRACT(EPOCH FROM (load_end_time - load_start_time)) as duration_seconds,
    rows_loaded,
    load_status
FROM metadata.etl_load_log
ORDER BY load_start_time DESC
LIMIT 100;

CREATE OR REPLACE VIEW metadata.v_quality_summary AS
SELECT 
    table_name,
    COUNT(*) as total_checks,
    SUM(CASE WHEN check_result = 'PASS' THEN 1 ELSE 0 END) as passed_checks,
    SUM(CASE WHEN check_result = 'FAIL' THEN 1 ELSE 0 END) as failed_checks,
    MAX(check_date) as last_check_date
FROM metadata.quality_checks
GROUP BY table_name;

-- ========================================
-- GRANTS
-- ========================================

GRANT USAGE ON SCHEMA staging TO dwh_user;
GRANT USAGE ON SCHEMA dim TO dwh_user;
GRANT USAGE ON SCHEMA fact TO dwh_user;
GRANT USAGE ON SCHEMA analytics TO dwh_user;
GRANT USAGE ON SCHEMA metadata TO dwh_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging TO dwh_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dim TO dwh_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA fact TO dwh_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO dwh_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA metadata TO dwh_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA metadata TO dwh_user;