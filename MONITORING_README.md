# 🔍 ELK - Monitoring et Qualité des Données

## 📊 Vue d'ensemble

Système de **logging centralisé** et **monitoring en temps réel** pour votre pipeline ETL.

### Architecture

```
┌──────────────────────────────────────────────────┐
│      Sources de Logs                             │
│  • Python ETL (logging standard)                 │
│  • Monitoring & Qualité                          │
│  • Logs temps réel (TCP/UDP)                     │
└────────────────┬─────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │  Flask/Python   │
        │  (Traitement)   │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  SQLite (DB)    │
        │  (Stockage)     │
        └────────┬────────┘
                 │
        ┌────────▼────────────────┐
        │   Dashboard Web         │
        │   (Visualisation)       │
        │   http://localhost:5000 │
        └─────────────────────────┘
```

## 🚀 Démarrage rapide

### Option 1: Dashboard Python (Recommandé)

```bash
# Windows
python start-dashboard.py

# Ou directement
python monitoring/elk_dashboard.py
```

**Accès**: http://localhost:5000

### Option 2: Docker ELK Stack

```bash
# Windows PowerShell
.\start-elk.ps1

# Linux/Mac
chmod +x start-elk.sh
./start-elk.sh
```

**Services**:
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Logstash: localhost:5000

## 📋 Intégration avec Python

### Utiliser le logger ELK

```python
from monitoring.elk_integration import ELKLogger

# Initialiser
elk_logger = ELKLogger(name="mon-app")
logger = elk_logger.get_logger()

# Logs standards
logger.info("Application démarrée")
logger.error("Erreur critique")
logger.warning("Avertissement")

# Métriques de qualité
elk_logger.log_metric(
    "data_completeness",
    99.5,
    {"source": "mysql", "table": "patients"}
)

# Check de qualité
elk_logger.log_quality_check(
    table="patients",
    completeness=99.8,
    duplicates=0.1,
    status="PASS"
)
```

### Dans le workflow ETL

```python
from monitoring.elk_integration import ELKLogger

elk_logger = ELKLogger(
    name="etl-monitoring",
    logstash_host="localhost",
    logstash_port=5000
)

# Avant ETL
logger = elk_logger.get_logger()
logger.info("Démarrage extraction MySQL")

# Après extraction
elk_logger.log_quality_check(
    table="patients",
    completeness=completeness_rate,
    duplicates=duplicate_rate,
    status="PASS" if completeness_rate > 95 else "WARNING"
)
```

## 📊 Dashboard Web Features

### 🎯 Statistiques principales

- **Logs Total**: Nombre total de logs indexés
- **Erreurs**: Nombre d'erreurs critiques
- **Avertissements**: Nombre d'avertissements
- **Métriques**: Nombre de métriques de qualité

### 📋 Onglets disponibles

1. **Logs** - Tous les logs avec filtrage
2. **Métriques** - Métriques de qualité par table/source
3. **Erreurs** - Erreurs critiques uniquement

### 🔍 Filtrage

- Recherche par texte (message, logger, etc.)
- Filtrer par niveau (INFO, WARNING, ERROR)
- Actualisation en temps réel (10 secondes)

### 📈 Affichage des logs

```
Timestamp | Level | Logger | Message
----------|-------|--------|----------
2025-11-17| ERROR | etl    | Connection failed
11:38:45  |       |        |
```

### 📊 Affichage des métriques

```
Métrique          | Valeur | Source | Table
------------------|--------|--------|-------
data_completeness |  99.5% | MySQL  | patients
duplicate_rate    |  0.3%  | MongoDB| tests
```

## 🗄️ Base de données

### Schema SQLite

#### Logs
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    level TEXT (INFO/WARNING/ERROR),
    logger TEXT,
    message TEXT,
    module TEXT,
    function TEXT,
    line INTEGER,
    tags TEXT (JSON),
    exception TEXT
)
```

#### Métriques
```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    metric_name TEXT,
    value REAL,
    source TEXT,
    table_name TEXT,
    tags TEXT (JSON)
)
```

## 💡 Exemples d'utilisation

### Exemple 1: Logger une extraction

```python
from monitoring.elk_integration import ELKLogger

elk_logger = ELKLogger("etl-mysql")
logger = elk_logger.get_logger()

try:
    logger.info("Extraction table: patients")
    data = extract_from_mysql()
    
    elk_logger.log_quality_check(
        table="patients",
        completeness=100.0,
        duplicates=0.0,
        status="PASS",
        details={"rows": len(data)}
    )
except Exception as e:
    logger.error(f"Erreur extraction: {str(e)}")
    elk_logger.log_quality_check(
        table="patients",
        completeness=0.0,
        duplicates=0.0,
        status="CRITICAL",
        details={"error": str(e)}
    )
```

### Exemple 2: Logger une transformation

```python
from monitoring.elk_integration import ELKLogger

elk_logger = ELKLogger("etl-transform")

logger.info("Transformation en cours...")

# Traitement
completeness = count_non_null(data) / len(data) * 100
duplicates = count_duplicates(data) / len(data) * 100

elk_logger.log_quality_check(
    table="stg_patients",
    completeness=completeness,
    duplicates=duplicates,
    status="PASS" if completeness > 95 else "WARNING"
)

elk_logger.log_metric(
    "transformation_time",
    elapsed_time,
    {"table": "patients"}
)
```

### Exemple 3: Logger une charge

```python
from monitoring.elk_integration import ELKLogger

elk_logger = ELKLogger("etl-load")

for table in tables:
    logger.info(f"Chargement {table} dans warehouse")
    
    try:
        load_to_warehouse(table, data)
        
        elk_logger.log_quality_check(
            table=f"staging.{table}",
            completeness=100.0,
            duplicates=0.0,
            status="PASS",
            details={"rows_loaded": len(data)}
        )
    except Exception as e:
        logger.error(f"Erreur chargement {table}: {e}")
        elk_logger.log_quality_check(
            table=f"staging.{table}",
            completeness=0.0,
            duplicates=0.0,
            status="CRITICAL"
        )
```

## 🔌 API Dashboard

### GET /api/stats
Retourne les statistiques générales

```json
{
    "total_logs": 1234,
    "errors": 12,
    "warnings": 45,
    "total_metrics": 567,
    "db_size": 102400
}
```

### GET /api/logs?level=ERROR&limit=100
Retourne les logs

```json
[
    {
        "id": 1,
        "timestamp": "2025-11-17T11:38:45",
        "level": "ERROR",
        "logger": "etl-monitor",
        "message": "Erreur de connexion",
        "module": "extractors",
        "function": "extract_mysql",
        "line": 42
    }
]
```

### GET /api/metrics?metric_name=data_completeness&limit=100
Retourne les métriques

```json
[
    {
        "id": 1,
        "timestamp": "2025-11-17T11:38:45",
        "metric_name": "data_completeness",
        "value": 99.5,
        "source": "mysql",
        "table_name": "patients"
    }
]
```

### POST /api/index
Index un nouveau log/métrique

```json
{
    "type": "metric",
    "timestamp": "2025-11-17T11:38:45",
    "metric_name": "data_completeness",
    "value": 99.5,
    "source": "mysql",
    "table_name": "patients"
}
```

## 📈 Visualisations disponibles

### Dashboard principal
- Compteurs de logs, erreurs, avertissements
- Métriques de qualité globales
- Logs en temps réel

### Onglet Logs
- Liste complète des logs
- Filtrage par niveau et texte
- Affichage du contexte (module, fonction, ligne)

### Onglet Métriques
- Grille des métriques récentes
- Valeurs par source et table
- Historique accessible via API

### Onglet Erreurs
- Liste des erreurs critiques
- Mise en avant visuelle (fond rouge)
- Filtre automatique

## 🧹 Maintenance

### Nettoyer les old logs

```python
from monitoring.simple_elasticsearch import SimpleElasticsearch
from datetime import datetime, timedelta
import sqlite3

es = SimpleElasticsearch()
conn = sqlite3.connect('elk_logs.db')
c = conn.cursor()

# Supprimer logs > 30 jours
cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
c.execute("DELETE FROM logs WHERE created_at < ?", (cutoff_date,))

conn.commit()
conn.close()
```

### Vérifier la taille de la DB

```python
from pathlib import Path
db_size = Path('elk_logs.db').stat().st_size
print(f"Taille DB: {db_size / 1024 / 1024:.2f} MB")
```

## 🐛 Dépannage

### Dashboard ne répond pas

```bash
# Vérifier si le port 5000 est occupé
# Relancer
python start-dashboard.py
```

### Logs n'apparaissent pas

1. Vérifier que ELKLogger est utilisé dans le code
2. Vérifier les logs console pour les erreurs
3. Vérifier que `elk_logs.db` existe
4. Rafraîchir le dashboard

### Problèmes de performance

- Vider les anciens logs (30+ jours)
- Redémarrer le dashboard
- Augmenter la limite de requête API

## 📚 Ressources

- [Python logging](https://docs.python.org/3/library/logging.html)
- [Flask documentation](https://flask.palletsprojects.com/)
- [SQLite documentation](https://www.sqlite.org/docs.html)

## ✅ Checklist

- [ ] Flask installé (`pip install flask`)
- [ ] Dashboard lancé (`python start-dashboard.py`)
- [ ] Accessible sur http://localhost:5000
- [ ] ELKLogger intégré au code ETL
- [ ] Logs apparaissent dans le dashboard
- [ ] Métriques de qualité indexées
- [ ] Filtrage fonctionne
- [ ] Auto-refresh actif (10 secondes)

## 🎉 Résumé

Vous disposez maintenant d'une solution **ELK légère et flexible** qui:

✅ Centralise tous les logs du pipeline ETL
✅ Indexe les métriques de qualité
✅ Fournit un dashboard web interactif
✅ Permet le filtrage et la recherche
✅ Fonctionne sans Docker supplémentaire
✅ Utilise une base de données SQLite locale
✅ Offre une API REST complète

**Dashboard**: http://localhost:5000
