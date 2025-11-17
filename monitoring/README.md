#  Système de Monitoring et Qualité des Données

## Vue d'ensemble

Ce système assure la qualité et la fiabilité des données à travers l'ETL.

##  Composants

### 1. **Data Quality Check** (`data_quality_check.py`)

Vérifie automatiquement :
- ✓ **Complétude** : Absence de valeurs nulles
- ✓ **Doublons** : Détection des enregistrements dupliqués
- ✓ **Types de données** : Conformité avec les schémas
- ✓ **Plages numériques** : Min, Max, Moyenne, Écart-type

```python
from monitoring.data_quality_check import DataQualityChecker

checker = DataQualityChecker()
result = checker.check_completeness(df, 'patients')
```

### 2. **Monitoring Dashboard** (`monitoring_dashboard.py`)

Génère un dashboard interactif avec :
-  Métriques en temps réel
- 🚨 Système d'alertes
-  Rapports HTML
-  Console reporting

```python
from monitoring.monitoring_dashboard import MonitoringDashboard

dashboard = MonitoringDashboard()
dashboard.save_dashboard(metrics)
```

### 3. **SLA Configuration** (`sla_config.json`)

Définit les seuils de qualité :
- **Data Completeness** : > 95% (warning), > 90% (critical)
- **Duplicate Rate** : < 1% (warning), < 5% (critical)
- **ETL Duration** : < 600s (warning), < 1200s (critical)

##  Utilisation

### Exécuter les vérifications de qualité

```bash
# Python
python -c "
from monitoring.data_quality_check import run_quality_checks
from etl.extractors.mysql_extractor import MySQLExtractor


extractor = MySQLExtractor()
data = {'mysql': extractor.extract_all()}

# Vérifier la qualité
report = run_quality_checks(data)
"
```

### Générer le dashboard

```bash
# Afficher dans la console
python monitoring/monitoring_dashboard.py

# Générer HTML
python -c "
from monitoring.monitoring_dashboard import MonitoringDashboard
import json

dashboard = MonitoringDashboard()
with open('monitoring/quality_report.json') as f:
    metrics = json.load(f)

dashboard.print_console_dashboard(metrics)
dashboard.save_dashboard(metrics)
"
```

##  Métriques suivi

### Volume des données
```json
{
  "mysql": {
    "patients": {"rows": 200, "size_mb": 0.5},
    "medical_tests": {"rows": 600, "size_mb": 1.2}
  }
}
```

### Historique ETL
```json
{
  "etl_runs": [
    {
      "timestamp": "2025-11-17T10:45:24Z",
      "status": "success",
      "duration_seconds": 45,
      "records_processed": 1400
    }
  ]
}
```

## 🚨 Système d'alertes

### Types d'alertes

| Sévérité | Seuil | Action |
|----------|-------|--------|
| [OK] OK | > 95% complétude | Aucune |
| ⚠️ WARNING | 90-95% complétude | Notification |
| 🔴 CRITICAL | < 90% complétude | Alerte + Email |

### Configurer les alertes

```json
{
  "monitoring": {
    "enable_alerts": true,
    "notification_email": "your-email@example.com",
    "check_interval": 3600
  }
}
```

##  Rapport de qualité

Le rapport JSON contient :

```json
{
  "timestamp": "2025-11-17T10:45:24Z",
  "checks": {
    "mysql_patients": {
      "completeness": {
        "completion_rate": "98.5%",
        "status": "PASS"
      },
      "duplicates": {
        "duplicate_rate": "0.2%",
        "status": "PASS"
      }
    }
  }
}
```

##  Rapports disponibles

1. **Console Report** : Affichage texte immédiat
2. **JSON Report** : `monitoring/quality_report.json`
3. **HTML Dashboard** : `monitoring/dashboard.html`
4. **CSV Export** : Export pour Excel/BI

##  Configuration avancée

### Ajouter une vérification personnalisée

```python
class DataQualityChecker:
    def check_custom(self, df, table_name):
        # Votre logique de vérification
        result = {
            'table': table_name,
            'status': 'PASS'
        }
        return result
```

### Intégrer avec GitHub Actions

Le workflow vérifie automatiquement la qualité des données à chaque ETL.

## 📞 Support

Pour des problèmes :
1. Consulter les logs dans `logs/quality_check.log`
2. Vérifier la configuration `sla_config.json`
3. Consulter le dashboard HTML



### Nettoyage des anciens rapports
```bash
find monitoring/reports -mtime +30 -delete
```

### Archivage des métriques
```bash
tar -czf monitoring/archive_$(date +%Y%m%d).tar.gz monitoring/quality_report.json
```
