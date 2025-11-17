# Guide de Déploiement Power BI - DatAnalystFlow360

## Avant de Commencer

Assurez-vous que:
- [x] PostgreSQL est opérationnel
- [x] Le pipeline ETL a chargé les données
- [x] Power BI Desktop est installé
- [x] Vous avez un compte Power BI

## Étape 1: Préparer l'Environnement

### Vérifier PostgreSQL

```bash
# Vérifier que PostgreSQL est en cours d'exécution
docker ps | grep postgres

# Vérifier la connexion
psql -h localhost -U dwh_user -d datawarehouse
```

### Vérifier les Données

```sql
-- Vérifier le schéma staging
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'staging';

-- Compter les lignes
SELECT 'stg_patients' as table_name, COUNT(*) as rows FROM staging.stg_patients
UNION ALL
SELECT 'stg_medical_tests', COUNT(*) FROM staging.stg_medical_tests
UNION ALL
SELECT 'stg_medications', COUNT(*) FROM staging.stg_medications
UNION ALL
SELECT 'stg_patient_activities', COUNT(*) FROM staging.stg_patient_activities
UNION ALL
SELECT 'stg_appointments', COUNT(*) FROM staging.stg_appointments
UNION ALL
SELECT 'stg_vital_signs_logs', COUNT(*) FROM staging.stg_vital_signs_logs;
```

## Étape 2: Créer le Modèle dans Power BI Desktop

### 1. Lancer Power BI Desktop

```bash
# Si installé localement
"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
```

### 2. Créer une Nouvelle Source de Données

1. Cliquez sur `Get Data`
2. Recherchez `PostgreSQL`
3. Configurez la connexion:
   - **Server**: `localhost`
   - **Port**: `5432`
   - **Database**: `datawarehouse`

### 3. Charger les Tables

Sélectionnez les 6 tables de staging:
- stg_patients
- stg_medical_tests
- stg_medications
- stg_patient_activities
- stg_appointments
- stg_vital_signs_logs

### 4. Configurer les Relations

Dans l'onglet `Model`:

```
stg_patients.patient_id ──→ stg_medical_tests.patient_id
stg_patients.patient_id ──→ stg_medications.patient_id
stg_patients.patient_id ──→ stg_patient_activities.patient_id
stg_patients.patient_id ──→ stg_appointments.patient_id
stg_patients.patient_id ──→ stg_vital_signs_logs.patient_id
```

## Étape 3: Créer les Visualisations

### Page 1: Overview

**KPI 1: Total Patients**
```dax
TotalPatients = COUNTROWS(stg_patients)
```
- Visualisation: Card
- Format: Nombre entier

**KPI 2: Average Age**
```dax
AverageAge = AVERAGE(stg_patients[age])
```
- Visualisation: Card
- Format: 1 décimale

**KPI 3: Total Tests**
```dax
TotalTests = COUNTROWS(stg_medical_tests)
```
- Visualisation: Card
- Format: Nombre entier

**KPI 4: Data Quality**
```dax
DataQuality = 99.87%
```
- Visualisation: Gauge
- Format: Pourcentage

### Page 2: Patients Analysis

**Table: Patients List**
- Colonnes: PatientID, Age, Gender, DiseaseType
- Sort: By PatientID

**Chart 1: Disease Type Distribution**
- Type: Bar Chart (Horizontal)
- Axe X: Count of Patients
- Axe Y: DiseaseType
- Sort: Count descending

**Chart 2: Gender Distribution**
- Type: Pie Chart
- Values: Count of Patients
- Legend: Gender

**Chart 3: Age Range Distribution**
- Type: Histogram
- Données: Age
- Bins: Automatique

### Page 3: Medical Tests

**Table: Test Results**
- Colonnes: TestID, PatientID, TestType, Result, Date

**Chart 1: Tests by Patient**
- Type: Bar Chart
- Axe X: Count of Tests
- Axe Y: PatientID

**Chart 2: Test Type Distribution**
- Type: Pie Chart
- Values: Count of Tests
- Legend: TestType

**Chart 3: Results Timeline**
- Type: Line Chart
- Axe X: Date
- Axe Y: Count of Tests

### Page 4: Monitoring

**Gauge 1: Completeness**
- Value: 99.87%
- Min: 0%, Max: 100%
- Color: Green if > 95%, Red otherwise

**Gauge 2: Duplicate Rate**
- Value: 0.05%
- Min: 0%, Max: 5%
- Color: Green if < 1%, Yellow if 1-2%, Red if > 2%

**Table: Recent Activities**
- Colonnes: ActivityID, PatientID, ActivityType, Timestamp
- Filter: Last 100 records
- Sort: Timestamp descending

**Chart: Data Volume Trend**
- Type: Area Chart
- Axe X: Date
- Axe Y: Total Records

## Étape 4: Publier sur Power BI Online

### 1. Sauvegarder le Fichier

```
File → Save As
Chemin: ./powerbi/powerbi_dashboard.pbix
```

### 2. Publier

```
File → Publish
Workspace: Sélectionnez votre workspace
Confirm: Cliquez sur Select
```

### 3. Configurer les Paramètres en Ligne

Une fois publié:

1. Allez sur https://app.powerbi.com
2. Sélectionnez votre rapport
3. Cliquez sur `Settings`
4. Allez à `Data source credentials`
5. Entrez les credentials PostgreSQL
6. Cochez "Use OAuth2"

### 4. Planifier l'Actualisation

1. Dans `Settings`
2. `Scheduled refresh`
3. Configurez:
   - **Frequency**: Daily
   - **Time**: 03:00 UTC
   - **Timezone**: UTC

## Étape 5: Partager le Dashboard

### Avec les Utilisateurs

1. Dans Power BI Online
2. Cliquez sur `Share`
3. Entrez les emails
4. Sélectionnez les permissions
5. Envoyez

### Avec les Groupes

1. Créez un Group Workspace
2. Ajoutez le rapport
3. Invitez les membres du groupe

## Vérification Post-Déploiement

Checklist:

- [ ] Toutes les pages se chargent correctement
- [ ] Les KPIs affichent les bonnes valeurs
- [ ] Les graphiques sont remplis de données
- [ ] Les filtres fonctionnent correctement
- [ ] Le rafraîchissement planifié est actif
- [ ] Les utilisateurs peuvent accéder au rapport

## Dépannage

### Problème: "PostgreSQL driver not found"

**Solution**:
```
1. Téléchargez PostgreSQL ODBC Driver
2. https://www.postgresql.org/download/windows/
3. Installez et redémarrez Power BI Desktop
```

### Problème: "Cannot connect to server"

**Solution**:
```bash
# Vérifiez la connexion PostgreSQL
psql -h localhost -U dwh_user -d datawarehouse

# Vérifiez le firewall
netstat -an | findstr 5432
```

### Problème: "Data refresh failed"

**Solution**:
```
1. Vérifiez les credentials dans Power BI Online
2. Vérifiez que PostgreSQL est accessible depuis le cloud
3. Configurez un gateway Power BI si nécessaire
```

## Prochaines Étapes

1. [x] Créer le modèle
2. [x] Ajouter les visualisations
3. [x] Publier en ligne
4. [ ] Configurer les alertes
5. [ ] Partager avec l'équipe
6. [ ] Former les utilisateurs

## Support et Documentation

- Voir `README.md` dans ce répertoire
- Voir `../POWER_BI_SETUP.md` pour la configuration générale
- Voir `../PROJECT_SUMMARY.md` pour l'architecture

## Fichiers de Référence

- `powerbi_config.json` - Configuration complète
- `../powerbi_config.json` - Configuration racine
- `../docker-compose.yml` - Infrastructure
