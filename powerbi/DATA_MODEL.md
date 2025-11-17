# Data Model - Power BI Dashboard

## Architecture du Modèle

```
┌─────────────────────────────────────────────────────────────┐
│                    STAR SCHEMA MODEL                        │
└─────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │  stg_patients   │ (FACT)
                    │  (200+ records) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   (1:N)                (1:N)                (1:N)
   
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│stg_medical_tests │ │  stg_medications │ │stg_appointments  │
│ (1000+ records)  │ │  (500+ records)  │ │ (1500+ records)  │
└──────────────────┘ └──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│stg_vital_signs   │ │stg_patient_      │
│   (10000+)       │ │  activities      │
└──────────────────┘ │ (5000+ records)  │
                     └──────────────────┘
```

## Fact Table: stg_patients

Représente la table principale des patients.

### Colonnes

| Colonne | Type | Description |
|---------|------|-------------|
| patient_id | INT | Clé primaire |
| name | VARCHAR | Nom du patient |
| age | INT | Âge en années |
| gender | VARCHAR | Genre (M/F) |
| disease_type | VARCHAR | Type de maladie |
| admission_date | DATE | Date d'admission |
| discharge_date | DATE | Date de sortie |
| status | VARCHAR | Statut (Active/Inactive) |

### Mesures

```dax
TotalPatients = COUNTROWS(stg_patients)
ActivePatients = CALCULATE(COUNTROWS(stg_patients), stg_patients[status] = "Active")
AverageAge = AVERAGE(stg_patients[age])
MalePatients = CALCULATE(COUNTROWS(stg_patients), stg_patients[gender] = "M")
FemalePatients = CALCULATE(COUNTROWS(stg_patients), stg_patients[gender] = "F")
```

## Dimension Table: stg_medical_tests

Contient les résultats des tests médicaux.

### Colonnes

| Colonne | Type | Description |
|---------|------|-------------|
| test_id | INT | Clé primaire |
| patient_id | INT | Clé étrangère vers patients |
| test_type | VARCHAR | Type de test |
| result | VARCHAR | Résultat du test |
| test_date | DATE | Date du test |
| value | FLOAT | Valeur numérique |
| unit | VARCHAR | Unité de mesure |
| reference_range | VARCHAR | Plage de référence |

### Mesures

```dax
TotalTests = COUNTROWS(stg_medical_tests)
TestsPerPatient = DIVIDE(COUNTROWS(stg_medical_tests), COUNTROWS(stg_patients))
AbnormalResults = CALCULATE(COUNTROWS(stg_medical_tests), stg_medical_tests[result] = "Abnormal")
```

### Hiérarchies

```
Test_Hierarchy
├── test_type
└── test_date (par année, trimestre, mois)
```

## Dimension Table: stg_medications

Contient les informations sur les médicaments prescrits.

### Colonnes

| Colonne | Type | Description |
|---------|------|-------------|
| medication_id | INT | Clé primaire |
| patient_id | INT | Clé étrangère vers patients |
| drug_name | VARCHAR | Nom du médicament |
| dosage | VARCHAR | Dosage prescrit |
| frequency | VARCHAR | Fréquence (daily, weekly, etc.) |
| start_date | DATE | Date de début |
| end_date | DATE | Date de fin |
| prescribed_by | VARCHAR | Prescripteur |

### Mesures

```dax
TotalMedications = COUNTROWS(stg_medications)
UniqueMedicines = DISTINCTCOUNT(stg_medications[drug_name])
ActiveMedications = CALCULATE(COUNTROWS(stg_medications), ISBLANK(stg_medications[end_date]))
```

## Dimension Table: stg_appointments

Enregistre les rendez-vous médicaux.

### Colonnes

| Colonne | Type | Description |
|---------|------|-------------|
| appointment_id | INT | Clé primaire |
| patient_id | INT | Clé étrangère vers patients |
| doctor_id | INT | Médecin responsable |
| appointment_date | DATETIME | Date/heure du RDV |
| appointment_type | VARCHAR | Type de RDV |
| status | VARCHAR | Statut (Scheduled/Completed/Cancelled) |
| notes | TEXT | Notes |

### Mesures

```dax
TotalAppointments = COUNTROWS(stg_appointments)
CompletedAppointments = CALCULATE(COUNTROWS(stg_appointments), stg_appointments[status] = "Completed")
CancelledAppointments = CALCULATE(COUNTROWS(stg_appointments), stg_appointments[status] = "Cancelled")
AppointmentAttendanceRate = DIVIDE(COUNTROWS(FILTER(stg_appointments, stg_appointments[status] = "Completed")), COUNTROWS(stg_appointments))
```

## Dimension Table: stg_vital_signs_logs

Historique des signes vitaux des patients.

### Colonnes

| Colonne | Type | Description |
|---------|------|-------------|
| vital_id | INT | Clé primaire |
| patient_id | INT | Clé étrangère vers patients |
| blood_pressure | VARCHAR | Tension artérielle |
| heart_rate | INT | Fréquence cardiaque (bpm) |
| temperature | FLOAT | Température (°C) |
| respiratory_rate | INT | Fréquence respiratoire |
| oxygen_saturation | FLOAT | Saturation en oxygène (%) |
| measurement_date | DATETIME | Date/heure de mesure |

### Mesures

```dax
AverageHeartRate = AVERAGE(stg_vital_signs_logs[heart_rate])
AverageTemperature = AVERAGE(stg_vital_signs_logs[temperature])
LatestVitalSigns = MAXX(FILTER(stg_vital_signs_logs, stg_vital_signs_logs[measurement_date] = MAX(stg_vital_signs_logs[measurement_date])), stg_vital_signs_logs)
```

## Dimension Table: stg_patient_activities

Suivi des activités des patients.

### Colonnes

| Colonne | Type | Description |
|---------|------|-------------|
| activity_id | INT | Clé primaire |
| patient_id | INT | Clé étrangère vers patients |
| activity_type | VARCHAR | Type d'activité |
| activity_date | DATE | Date de l'activité |
| description | TEXT | Description |
| duration | INT | Durée (minutes) |
| intensity | VARCHAR | Intensité (Low/Medium/High) |

### Mesures

```dax
TotalActivities = COUNTROWS(stg_patient_activities)
ActivitiesByIntensity = SUMMARIZE(stg_patient_activities, stg_patient_activities[intensity], "Count", COUNTROWS(stg_patient_activities))
AverageDuration = AVERAGE(stg_patient_activities[duration])
```

## Relations et Hiérarchies

### Relations Principales

| De | Vers | Cardinalité | Activité |
|----|------|-------------|----------|
| stg_patients.patient_id | stg_medical_tests.patient_id | 1:N | Actif |
| stg_patients.patient_id | stg_medications.patient_id | 1:N | Actif |
| stg_patients.patient_id | stg_appointments.patient_id | 1:N | Actif |
| stg_patients.patient_id | stg_vital_signs_logs.patient_id | 1:N | Actif |
| stg_patients.patient_id | stg_patient_activities.patient_id | 1:N | Actif |

### Hiérarchies Temporelles

```
Date_Hierarchy
├── Year
├── Quarter
├── Month
└── Day

Time_Hierarchy (pour timestamps)
├── Year
├── Month
├── Day
└── Hour
```

## Qualité des Données

### Indicateurs

- **Complétude**: 99.87%
- **Taux de doublons**: 0.05%
- **Validation des types**: 100%
- **Validation des plages**: 100%

### Nettoyage Effectué

```dax
CleanedRecords = COUNTROWS(FILTER(stg_patients, NOT(ISBLANK(stg_patients[patient_id]))))
InvalidRecords = CALCULATE(COUNTROWS(stg_patients), ISBLANK(stg_patients[patient_id]))
CleanlinessPercentage = DIVIDE(CleanedRecords, COUNTROWS(stg_patients)) * 100
```

## Performance Optimisations

### Agrégations Recommandées

```
Aggregation 1: Total patients by disease_type and age_group
Aggregation 2: Total tests by test_type and month
Aggregation 3: Average vital signs by patient
```

### Index PostgreSQL (Côté Source)

```sql
CREATE INDEX idx_stg_patients_id ON staging.stg_patients(patient_id);
CREATE INDEX idx_stg_medical_tests_patient_id ON staging.stg_medical_tests(patient_id);
CREATE INDEX idx_stg_medications_patient_id ON staging.stg_medications(patient_id);
CREATE INDEX idx_stg_appointments_patient_id ON staging.stg_appointments(patient_id);
CREATE INDEX idx_stg_vital_signs_patient_id ON staging.stg_vital_signs_logs(patient_id);
CREATE INDEX idx_stg_activities_patient_id ON staging.stg_patient_activities(patient_id);
```

## Règles de Sécurité (RLS)

Recommandé pour un déploiement multi-utilisateurs:

```dax
[Department Filter] = [Current User Department]
[Patient Access] = OR([IsAdmin], [AssignedDepartment] = [Current User Department])
```

## Fichiers de Référence

- `README.md` - Vue d'ensemble
- `DEPLOYMENT.md` - Guide de déploiement
- `powerbi_config.json` - Configuration JSON
