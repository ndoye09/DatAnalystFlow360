# ELK Stack - Logs Centralisés

##  Vue d'ensemble

La stack ELK (Elasticsearch + Logstash + Kibana) centralise tous les logs du projet ETL pour une visualisation et analyse unifiée.

### Architecture

```
┌─────────────────────────────────────────────┐
│         Sources de logs                      │
├─────────────────────────────────────────────┤
│ • Logs Python ETL                           │
│ • Monitoring & Qualité                      │
│ • Logs Docker                               │
│ • Logs temps réel (TCP/UDP)                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │     Logstash         │
        │  (Ingestion & Filter)│
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Elasticsearch       │
        │  (Stockage & Index)  │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │      Kibana          │
        │  (Visualisation)     │
        └──────────────────────┘
```

##  Démarrage

### Windows (PowerShell)

```powershell
.\start-elk.ps1
```

### Linux/Mac (Bash)

```bash
chmod +x start-elk.sh
./start-elk.sh
```

### Docker Compose direct

```bash
docker-compose -f docker-compose-elk.yml up -d
```

## 📍 Accès aux services

| Service | URL | Port |
|---------|-----|------|
| Elasticsearch | http://localhost:9200 | 9200 |
| Kibana | http://localhost:5601 | 5601 |
| Logstash | localhost | 5000 (TCP/UDP) |

## 🔌 Intégration avec Python

### Utiliser ELKLogger dans votre code

```python
from monitoring.elk_integration import ELKLogger

# Initialiser le logger
elk_logger = ELKLogger(
    name="mon-application",
    logstash_host="localhost",
    logstash_port=5000
)

# Logs standards
logger = elk_logger.get_logger()
logger.info("Message d'information")
logger.error("Message d'erreur")

# Logs de métriques
elk_logger.log_metric(
    "data_completeness",
    99.5,
    {"source": "mysql", "table": "patients"}
)

# Logs de qualité
elk_logger.log_quality_check(
    table="patients",
    completeness=99.8,
    duplicates=0.1,
    status="PASS",
    details={"rows": 1000}
)
```

### Dans monitoring/github_integration.py

```python
from elk_integration import ELKLogger

# Automatiquement intégré si ELK est disponible
elk_logger = ELKLogger(
    name="etl-monitoring",
    logstash_host=os.getenv("LOGSTASH_HOST", "localhost")
)

# Envoyer les métriques de qualité à ELK
elk_logger.log_quality_check(
    table="mysql_patients",
    completeness=100,
    duplicates=0,
    status="PASS"
)
```

##  Configuration Logstash

Le fichier `logstash/pipeline/logstash.conf` définit le pipeline de traitement:

### Inputs
- **File**: Lit les logs Python des fichiers
- **TCP**: Reçoit les logs en JSON via TCP
- **UDP**: Reçoit les logs légers via UDP

### Filters
- **Grok**: Parse les logs standards
- **Mutate**: Transforme et enrichit les données
- **Conversion de types**: Convertit les valeurs numériques

### Outputs
- **Elasticsearch**: Indexe tous les logs
- **File**: Sauvegarde les alertes critiques
- **Console**: Affiche les logs en debug

##  Utilisation de Kibana

### 1. Créer un Index Pattern

1. Aller à **Stack Management** → **Index Patterns**
2. Cliquer **Create index pattern**
3. Pattern: `etl-logs-*` (correspond aux index Logstash)
4. Timestamp field: `@timestamp`

### 2. Visualisations disponibles

#### Dashboard de qualité des données

```
Métriques principales:
- Total logs: ___
- Erreurs: ___
- Avertissements: ___
- Taux complétude moyen: ___%
- Taux doublons moyen: ___%
```

#### Timeline des erreurs

```
Graphique temporel montrant:
- Nombre d'erreurs par heure
- Avertissements par source
- Tendances de qualité
```

#### Logs par source

```
Tableau avec filtres par:
- Source (ETL, Monitoring, Docker)
- Niveau (INFO, WARNING, ERROR)
- Table/Module
```

### 3. Requêtes KQL (Kibana Query Language)

Exemples utiles:

```
# Tous les erreurs
level: "ERROR"

# Logs de monitoring uniquement
tags: "monitoring"

# Logs de qualité critiques
tags: "alert" AND status: "CRITICAL"

# Complétude basse
metric_name: "completeness" AND value: < 95

# Erreurs de la dernière heure
@timestamp: last 1h AND level: "ERROR"

# Logs d'une table spécifique
table: "patients"
```

## 🔔 Alertes et Notifications

### Configuration des alertes Kibana

1. Aller à **Management** → **Stack Management** → **Alerting**
2. Créer une alerte pour:
   - Complétude < 90%
   - Doublons > 5%
   - Erreurs ETL
   - Délai ETL > 1200s

### Webhook pour notifications

Exemple avec Slack:

```python
# Dans elk_integration.py
import requests

def send_slack_alert(message, level):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    color = "#FF0000" if level == "CRITICAL" else "#FFA500"
    
    payload = {
        "attachments": [{
            "color": color,
            "title": "Alerte ETL",
            "text": message
        }]
    }
    requests.post(webhook_url, json=payload)
```

##  Métriques suivies

### Par source

| Source | Métriques |
|--------|-----------|
| MySQL | Complétude, Doublons, Délai |
| MongoDB | Complétude, Doublons, Délai |
| CSV | Fichiers traités, Erreurs |
| Excel | Fichiers traités, Erreurs |

### Par type

| Type | Description |
|------|-------------|
| INFO | Informations générales |
| WARNING | Avertissements (seuils approchés) |
| ERROR | Erreurs bloquantes |
| METRIC | Valeurs numériques |
| QUALITY_CHECK | Résultats de vérification |



### Nettoyage des anciens logs

```bash
# Supprimer les index > 30 jours
curl -X DELETE "localhost:9200/etl-logs-*" \
  -H "Content-Type: application/json" \
  -d '{"query": {"range": {"@timestamp": {"lt": "now-30d"}}}}'
```

### Vérifier l'espace disque

```bash

curl "localhost:9200/_cat/indices?v"

# Santé du cluster
curl "localhost:9200/_cluster/health?pretty"
```

### Redémarrer les services

```bash
docker-compose -f docker-compose-elk.yml restart

# Ou spécifique
docker-compose -f docker-compose-elk.yml restart kibana
```

## 🐛 Dépannage

### Elasticsearch ne démarre pas

```bash
# Vérifier les logs
docker logs elk-elasticsearch

# Problèmes mémoire courants
# Solution: Augmenter vm.max_map_count
sudo sysctl -w vm.max_map_count=262144
```

### Logstash n'ingère pas les logs

```bash
# Vérifier la connexion
telnet localhost 5000

# Vérifier le pipeline
curl "localhost:9600/_stats"

# Logs Logstash
docker logs elk-logstash
```

### Kibana lent ou non réactif

```bash
# Redémarrer
docker-compose -f docker-compose-elk.yml restart kibana

# Vérifier la connexion ES
curl "localhost:9200/_cluster/health"
```

## 📚 Ressources

- [Elasticsearch Docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Logstash Docs](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Kibana Docs](https://www.elastic.co/guide/en/kibana/current/index.html)
- [KQL Reference](https://www.elastic.co/guide/en/kibana/current/kuery-query.html)

##  Checklist intégration ELK

- [ ] Docker et Docker Compose installés
- [ ] Stack ELK démarrée (`start-elk.ps1` ou `start-elk.sh`)
- [ ] Elasticsearch sain: http://localhost:9200
- [ ] Kibana accessible: http://localhost:5601
- [ ] Index pattern créé: `etl-logs-*`
- [ ] ELKLogger intégré dans le code Python
- [ ] Logs apparaissent dans Kibana
- [ ] Dashboards configurés
- [ ] Alertes paramétrées
- [ ] Notifications (Slack/Email) testées

##  Résultat final

Vous disposez maintenant d'une solution de logging complète et centralisée pour:
- **Suivre** tous les processus ETL en temps réel
- **Analyser** les patterns d'erreurs
- **Alerter** sur les anomalies
- **Auditer** les changements de données
- **Optimiser** la performance du pipeline
