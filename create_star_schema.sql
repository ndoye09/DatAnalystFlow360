-- ===== DIMENSION PATIENT =====
DROP TABLE IF EXISTS dim.dim_patient CASCADE;
CREATE TABLE dim.dim_patient AS
SELECT 
  patient_id as patient_key,
  patient_id,
  first_name,
  last_name,
  age,
  gender,
  blood_type,
  CURRENT_TIMESTAMP as created_at
FROM staging.stg_patients;

ALTER TABLE dim.dim_patient ADD PRIMARY KEY (patient_key);
CREATE INDEX idx_patient_id ON dim.dim_patient(patient_id);

-- ===== DIMENSION DOCTOR =====
DROP TABLE IF EXISTS dim.dim_doctor CASCADE;
CREATE TABLE dim.dim_doctor AS
SELECT 
  ROW_NUMBER() OVER (ORDER BY doctor_name) as doctor_key,
  doctor_name,
  specialty,
  CURRENT_TIMESTAMP as created_at
FROM (SELECT DISTINCT doctor_name, specialty FROM staging.stg_appointments) t;

ALTER TABLE dim.dim_doctor ADD PRIMARY KEY (doctor_key);

-- ===== FACT MEDICAL TESTS =====
DROP TABLE IF EXISTS fact.fact_medical_tests CASCADE;
CREATE TABLE fact.fact_medical_tests AS
SELECT 
  ROW_NUMBER() OVER (ORDER BY mt.test_id) as test_key,
  mt.test_id,
  p.patient_key,
  d.date_key,
  mt.cholesterol,
  mt.glucose,
  mt.systolic_bp,
  mt.diastolic_bp,
  mt.heart_rate,
  mt.test_type,
  CURRENT_TIMESTAMP as created_at
FROM staging.stg_medical_tests mt
JOIN dim.dim_patient p ON mt.patient_id = p.patient_id
JOIN dim.dim_date d ON mt.test_date = d.full_date;

ALTER TABLE fact.fact_medical_tests ADD PRIMARY KEY (test_key);
ALTER TABLE fact.fact_medical_tests ADD FOREIGN KEY (patient_key) REFERENCES dim.dim_patient(patient_key);
ALTER TABLE fact.fact_medical_tests ADD FOREIGN KEY (date_key) REFERENCES dim.dim_date(date_key);

-- ===== FACT APPOINTMENTS =====
DROP TABLE IF EXISTS fact.fact_appointments CASCADE;
CREATE TABLE fact.fact_appointments AS
SELECT 
  ROW_NUMBER() OVER (ORDER BY a.appointment_date) as appointment_key,
  p.patient_key,
  doc.doctor_key,
  d.date_key,
  a.status,
  a.duration_minutes,
  a.follow_up_required,
  CURRENT_TIMESTAMP as created_at
FROM staging.stg_appointments a
JOIN dim.dim_patient p ON a.patient_id = p.patient_id
JOIN dim.dim_doctor doc ON a.doctor_name = doc.doctor_name
JOIN dim.dim_date d ON a.appointment_date::date = d.full_date;

ALTER TABLE fact.fact_appointments ADD PRIMARY KEY (appointment_key);
ALTER TABLE fact.fact_appointments ADD FOREIGN KEY (patient_key) REFERENCES dim.dim_patient(patient_key);
ALTER TABLE fact.fact_appointments ADD FOREIGN KEY (doctor_key) REFERENCES dim.dim_doctor(doctor_key);

-- ===== ANALYTICS VIEWS =====
DROP VIEW IF EXISTS analytics.v_patient_health_summary CASCADE;
CREATE VIEW analytics.v_patient_health_summary AS
SELECT 
  p.patient_key,
  p.first_name || ' ' || p.last_name as full_name,
  p.gender,
  p.age,
  p.blood_type,
  COUNT(DISTINCT fmt.test_key) as total_tests,
  ROUND(AVG(fmt.cholesterol), 1) as avg_cholesterol,
  ROUND(AVG(fmt.glucose), 1) as avg_glucose,
  ROUND(AVG(fmt.systolic_bp), 1) as avg_systolic,
  ROUND(AVG(fmt.diastolic_bp), 1) as avg_diastolic,
  ROUND(AVG(fmt.heart_rate), 1) as avg_heart_rate,
  MAX(d.full_date) as last_test_date
FROM dim.dim_patient p
LEFT JOIN fact.fact_medical_tests fmt ON p.patient_key = fmt.patient_key
LEFT JOIN dim.dim_date d ON fmt.date_key = d.date_key
GROUP BY p.patient_key, p.first_name, p.last_name, p.gender, p.age, p.blood_type;

DROP VIEW IF EXISTS analytics.v_health_metrics CASCADE;
CREATE VIEW analytics.v_health_metrics AS
SELECT 
  'High Cholesterol (>250)' as metric,
  COUNT(*) as patient_count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(DISTINCT patient_key) FROM fact.fact_medical_tests), 2) as percentage
FROM fact.fact_medical_tests
WHERE cholesterol > 250
GROUP BY 1

UNION ALL

SELECT 
  'High Blood Pressure (>140/90)' as metric,
  COUNT(*) as patient_count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(DISTINCT patient_key) FROM fact.fact_medical_tests), 2) as percentage
FROM fact.fact_medical_tests
WHERE systolic_bp > 140 OR diastolic_bp > 90
GROUP BY 1

UNION ALL

SELECT 
  'High Glucose (>126)' as metric,
  COUNT(*) as patient_count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(DISTINCT patient_key) FROM fact.fact_medical_tests), 2) as percentage
FROM fact.fact_medical_tests
WHERE glucose > 126
GROUP BY 1;
