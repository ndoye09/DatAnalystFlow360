# Configuration Power BI - DatAnalystFlow360

## Vue d'ensemble

Ce guide explique comment configurer et déployer le dashboard Power BI pour le projet DatAnalystFlow360.

## Prérequis

- Power BI Desktop (version récente)
- PostgreSQL connecté et opérationnel
- Données dans le schéma `staging` de PostgreSQL
- Accès à Internet (pour Power BI Online)

## Architecture des Données

```
PostgreSQL (staging schema)
    ├── stg_patients
    ├── stg_medical_tests
    ├── stg_medications
    ├── stg_patient_activities
    ├── stg_appointments
    └── stg_vital_signs_logs
```

## Configuration de la Connexion PostgreSQL

### 1. Ouvrir Power BI Desktop

Lancez Power BI Desktop et créez un nouveau projet.

### 2. Importer les Données

1. Cliquez sur `Get Data` → `PostgreSQL database`
2. Configurez la connexion:
   - **Server**: `localhost` (ou votre adresse PostgreSQL)
   - **Database**: `datawarehouse`
   - **Port**: `5432`
3. Entrez les credentials:
   - **Username**: `dwh_user`
   - **Password**: `dwh_password`

### 3. Charger les Tables de Staging

Sélectionnez et chargez les tables suivantes:
- `stg_patients` - Données patients
- `stg_medical_tests` - Résultats médicaux
- `stg_medications` - Médicaments
- `stg_patient_activities` - Activités patients
- `stg_appointments` - Rendez-vous
- `stg_vital_signs_logs` - Signes vitaux

## Modèle de Données Recommandé

### Fact Table: Patients
- PatientID (PK)
- Age, Gender
- Disease Type
- TestCount

### Dimension Tables
- DimMedicalTests
- DimMedications
- DimVitalSigns

### Relationships
```
stg_patients (1) ──→ (*) stg_medical_tests
stg_patients (1) ──→ (*) stg_medications
stg_patients (1) ──→ (*) stg_vital_signs_logs
stg_patients (1) ──→ (*) stg_appointments
```

## Visualisations Recommandées

### Page 1: Vue d'ensemble
- KPI Cards:
  - Total Patients
  - Average Age
  - Total Tests
  - Total Medications

### Page 2: Analyse des Patients
- Table: Liste des patients avec détails
- Graphique: Distribution par type de maladie
- Graphique: Distribution par genre

### Page 3: Tests Médicaux
- Table: Résultats des tests
- Graphique: Tests par patient
- Graphique: Distribution des résultats

### Page 4: Monitoring
- Gauge: Qualité des données (99.87%)
- Table: Dernières activités
- Timeline: Évolution des données

## Mesures DAX Recommandées

```dax
// Nombre total de patients
TotalPatients = COUNTROWS(stg_patients)

// Âge moyen
AverageAge = AVERAGE(stg_patients[age])

// Nombre de tests
TotalTests = COUNTROWS(stg_medical_tests)

// Taux de complétude
DataCompleteness = 99.87%

// Taux de doublons
DuplicateRate = 0.05%
```

## Publication sur Power BI Online

### 1. Créer un Compte Power BI
- Allez à https://app.powerbi.com
- Connectez-vous avec votre compte Microsoft

### 2. Publier le Rapport
Dans Power BI Desktop:
1. Cliquez sur `Publish`
2. Sélectionnez votre workspace
3. Confirmez la publication

### 3. Configurer la Source de Données
Dans Power BI Online:
1. Allez aux `Settings`
2. Configurez les credentials PostgreSQL
3. Planifiez les rafraîchissements (quotidien à 3h UTC)

## Sécurité

- Utilisez un compte de service dédié pour PostgreSQL
- Configurez les permissions au niveau des lignes (RLS) si nécessaire
- Utilisez des rôles Power BI pour contrôler l'accès

## Intégration GitHub

### Exporter le Rapport
Power BI Desktop exporte en format `.pbix`:

```bash
# Fichier: powerbi_dashboard.pbix
# Format: Propriétaire
# Sauvegardé dans: /
```

### Stocker sur GitHub
1. Créez un dossier `/powerbi`
2. Ajoutez le fichier `.pbix`
3. Créez une documentation

```
powerbi/
├── powerbi_dashboard.pbix
├── DATA_MODEL.md
└── SCREENSHOTS/
    ├── overview.png
    ├── patients.png
    └── metrics.png
```

## Dépannage

### Connexion PostgreSQL refuse
- Vérifiez que PostgreSQL est en cours d'exécution
- Vérifiez les credentials
- Vérifiez les firewalls

### Données manquantes
- Exécutez le pipeline ETL: `.\sync-etl-fixed.ps1`
- Vérifiez le schéma `staging`

### Performance lente
- Utilisez l'importation au lieu du Direct Query
- Optimisez les requêtes
- Créez des agrégations

## Prochaines Étapes

1. [x] Configuration PostgreSQL
2. [x] Importation des données
3. [ ] Création du modèle de données
4. [ ] Création des visualisations
5. [ ] Tests et validation
6. [ ] Publication sur Power BI Online
7. [ ] Configuration des rafraîchissements
8. [ ] Partage avec les utilisateurs

## Support

Pour des questions sur:
- **ETL Pipeline**: Voir `README.md`
- **Monitoring**: Voir `MONITORING_README.md`
- **Architecture**: Voir `PROJECT_SUMMARY.md`

## Fichiers Connexes

- `POWER_BI.md` - Configuration Power BI
- `QUICKSTART.md` - Démarrage rapide
- `DATA_WAREHOUSE_README.md` - Documentation DWH
