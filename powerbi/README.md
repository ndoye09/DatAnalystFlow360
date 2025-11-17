# Power BI Dashboard - DatAnalystFlow360

## Structure du Répertoire

```
powerbi/
├── README.md                    # Ce fichier
├── DATA_MODEL.md               # Documentation du modèle de données
├── DEPLOYMENT.md               # Guide de déploiement
├── powerbi_dashboard.pbix       # Fichier du dashboard (à créer)
└── SCREENSHOTS/                # Captures d'écran
    ├── overview.png
    ├── patients_analysis.png
    ├── medical_tests.png
    └── monitoring.png
```

## Configuration Rapide

### 1. Importer le Modèle

Ouvrez `powerbi_dashboard.pbix` dans Power BI Desktop.

### 2. Configurer la Connexion PostgreSQL

Allez dans:
- File → Options and settings → Data source settings
- Configurez les credentials PostgreSQL:
  - Server: `localhost`
  - Port: `5432`
  - Database: `datawarehouse`
  - Username: `dwh_user`
  - Password: `dwh_password`

### 3. Rafraîchir les Données

- Cliquez sur `Refresh` pour charger les dernières données
- Vérifiez que toutes les tables sont importées avec succès

## Pages du Dashboard

### Page 1: Overview (Vue d'ensemble)
Affiche les KPIs principaux:
- Nombre total de patients
- Âge moyen
- Nombre total de tests
- Qualité des données (99.87%)

### Page 2: Patients Analysis (Analyse des Patients)
Visualise les données des patients:
- Table: Liste complète des patients
- Graphique: Distribution par type de maladie
- Graphique: Distribution par genre
- Graphique: Distribution par âge

### Page 3: Medical Tests (Tests Médicaux)
Analyse des résultats médicaux:
- Table: Résultats détaillés des tests
- Graphique: Nombre de tests par patient
- Graphique: Distribution des types de tests
- Timeline: Évolution temporelle

### Page 4: Monitoring
Suivi de la qualité des données:
- Gauge: Taux de complétude (99.87%)
- Gauge: Taux de doublons (0.05%)
- Table: Activités récentes
- Graphique: Tendance du volume de données

## Mesures DAX

Les mesures suivantes sont déjà configurées:

```dax
TotalPatients = COUNTROWS(stg_patients)
AverageAge = AVERAGE(stg_patients[age])
TotalTests = COUNTROWS(stg_medical_tests)
DataCompleteness = 99.87%
DuplicateRate = 0.05%
```

## Publication en Ligne

### Prérequis
- Compte Power BI (Premium ou Pro)
- Accès au workspace

### Étapes

1. Dans Power BI Desktop: `File → Publish`
2. Sélectionnez votre workspace
3. Confirmez la publication
4. En ligne: Configurez les credentials dans les settings

## Actualisation des Données

Le dashboard se met à jour quotidiennement à **03:00 UTC** (après le pipeline ETL).

Pour une actualisation manuelle:
- Power BI Online: Cliquez sur le bouton de rafraîchissement
- Power BI Desktop: Appuyez sur `Ctrl + R`

## Dépannage

### Erreur de connexion PostgreSQL
```
Action: Vérifiez que PostgreSQL est en cours d'exécution
Commande: docker ps | grep postgres
```

### Données manquantes
```
Action: Exécutez le pipeline ETL
Script: .\sync-etl-fixed.ps1
```

### Performance lente
```
Action: Changez le mode de connexion
Option: Direct Query → Import
```

## Support

- Documentation: Voir `../POWER_BI_SETUP.md`
- Architecture: Voir `../PROJECT_SUMMARY.md`
- Monitoring: Voir `../MONITORING_README.md`

## Fichiers Connexes

- `powerbi_config.json` - Configuration JSON
- `../POWER_BI_SETUP.md` - Guide de setup complet
- `../QUICKSTART.md` - Démarrage rapide global
