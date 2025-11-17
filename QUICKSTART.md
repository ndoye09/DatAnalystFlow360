# ⚡ Quickstart - DatAnalystFlow360

## 🚀 Démarrage en 5 minutes

### 1️⃣ Installation (1 min)

```powershell
# Cloner le repository
git clone https://github.com/ndoye09/DatAnalystFlow360.git
cd data-lake-etl

# Installer les dépendances
pip install -r requirements.txt
```

### 2️⃣ Démarrer les services (2 min)

```powershell
# Démarrer l'infrastructure complète
.\sync-etl-fixed.ps1

# Attendez ~45 secondes...
# ✅ SYNCHRONISATION ETL RÉUSSIE
```

### 3️⃣ Vérifier les données (1 min)

```powershell
# Tester la solution ELK
python test-elk.py

# Résultat attendu:
# 🎉 TOUS LES TESTS SONT PASSÉS! (4/4)
```

### 4️⃣ Visualiser les dashboards (1 min)

```powershell
# Ouvrir le dashboard ELK
start monitoring\dashboard-elk.html

# Ou accéder à Metabase
start http://localhost:3000
```

---

## 📊 Vérifier le statut

```powershell
# Voir les services Docker
docker ps

# Vérifier la base de données
docker exec datawarehouse psql -U dwh_user -d datawarehouse -c "
  SELECT table_name, count(*) as rows FROM information_schema.tables t
  LEFT JOIN (SELECT table_name FROM information_schema.columns GROUP BY table_name) c
  ON t.table_name = c.table_name
  WHERE table_schema = 'staging'
  GROUP BY table_name ORDER BY rows DESC;
"

# Vérifier les logs de qualité
python -c "
from monitoring.simple_elasticsearch import SimpleElasticsearch
es = SimpleElasticsearch()
stats = es.get_stats()
print(f'Total logs: {stats[\"total_logs\"]}')
print(f'Total métriques: {stats[\"total_metrics\"]}')
print(f'Erreurs: {stats[\"errors\"]}')
"
```

---

## 🎯 Cas d'usage

### 1. Exécuter l'ETL complet

```powershell
.\sync-etl-fixed.ps1

# Extrait de 4 sources différentes
# Transforme et charge 72,950 lignes
# Valide la qualité des données
# Temps: ~45 secondes
```

### 2. Exécuter le monitoring

```powershell
python monitoring/github_integration.py

# Génère les rapports de qualité
# Crée les dashboards HTML
# Indexe les logs
# Export JSON pour GitHub Actions
```

### 3. Consulter les logs centralisés

```powershell
python test-elk.py

# Affiche tous les logs
# Recherche par niveau (ERROR, WARNING, INFO)
# Filtre par source (MySQL, MongoDB, etc.)
# Génère le dashboard HTML
```

### 4. Accéder aux données

```
PostgreSQL (Data Warehouse):
  - Host: localhost:5432
  - User: dwh_user
  - Password: dwh_password
  - Database: datawarehouse

HDFS (Data Lake):
  - URL: http://localhost:9871
  - Format: Parquet
  - Données: Compressées (Snappy)

Metabase (Dashboards):
  - URL: http://localhost:3000
```

---

## 🔧 Commandes utiles

```powershell
# Arrêter tous les services
docker-compose down
docker-compose -f docker-compose-dwh.yml down

# Voir les logs d'une application
docker logs datalake-etl --tail 50
docker logs datawarehouse --tail 50

# Relancer un service
docker-compose restart datalake-mysql
docker-compose restart datalake-mongodb

# Nettoyer les données
docker volume prune
rm monitoring/elk_logs.db

# Vérifier les performances
docker stats

# Exécuter les tests
python test-elk.py
pytest tests/ -v

# Mettre à jour le code
git pull origin main
```

---

## 📈 Métriques rapides

```
Infrastructure:
  ✓ Services: 8 (MySQL, MongoDB, HDFS, PostgreSQL, MinIO, etc.)
  ✓ Docker containers: Tous opérationnels
  ✓ Storage: PostgreSQL + HDFS + MinIO

Données:
  ✓ Sources: 4 (MySQL, MongoDB, CSV, Excel)
  ✓ Total rows: 72,950
  ✓ Tables: 8 (staging)
  ✓ Complétude: 99.87%
  ✓ Doublons: 0.05%

Monitoring:
  ✓ Logs: Centralisés (SQLite)
  ✓ Dashboard: HTML + Metabase
  ✓ Tests: 4/4 PASS
  ✓ Qualité: En temps réel
  
Automatisation:
  ✓ GitHub Actions: Quotidien (2h UTC)
  ✓ Workflow status: ✅ SUCCESS
  ✓ CI/CD: Complètement automatisé
```

---

## ⚠️ Troubleshooting rapide

### Problème: Docker service down

```powershell
# Redémarrer Docker Desktop
# Puis:
.\sync-etl-fixed.ps1
```

### Problème: Port déjà utilisé

```powershell
# Arrêter les anciens conteneurs
docker-compose down

# Nettoyer les orphelins
docker-compose down --remove-orphans
```

### Problème: Données manquantes

```powershell
# Vérifier la base de données
docker exec datalake-mysql mysql -uroot -pLebou09@ data_analyst_db -e "SELECT COUNT(*) FROM patients;"

# Vérifier MongoDB
docker exec datalake-mongodb mongosh --eval "db.medical_records.countDocuments()"
```

### Problème: Tests échouent

```powershell
# Nettoyer la base ELK
rm monitoring/elk_logs.db

# Réexécuter les tests
python test-elk.py
```

---

## 📚 Documentation complète

| Fichier | Contenu |
|---------|---------|
| README.md | Vue d'ensemble générale |
| PROJECT_SUMMARY.md | Résumé complet du projet |
| ELK_README.md | Logs centralisés (ELK stack) |
| TEST_ELK.md | Guide de test détaillé |
| QUICKSTART.md | Ce fichier (démarrage rapide) |

---

## 🎓 Exemples de code

### Indexer un log

```python
from monitoring.simple_elasticsearch import SimpleElasticsearch
from datetime import datetime

es = SimpleElasticsearch()
es.index_log({
    'timestamp': datetime.now().isoformat(),
    'level': 'INFO',
    'logger': 'my-app',
    'message': 'Mon log',
    'module': 'main',
    'function': 'start',
    'line': 42,
    'tags': ['tag1', 'tag2']
})
```

### Rechercher des logs

```python
# Tous les logs
logs = es.search_logs(limit=10)

# Uniquement les erreurs
errors = es.search_logs(level='ERROR', limit=10)

# Chercher dans les métriques
metrics = es.search_metrics(source='mysql', limit=20)
```

### Utiliser ELKLogger

```python
from monitoring.elk_integration import ELKLogger

logger = ELKLogger("my-app")
logger.log_quality_check(
    table="patients",
    completeness=99.8,
    duplicates=0.1,
    status="PASS"
)
```

---

## 🚀 Prochaines étapes

1. ✅ Infrastructure opérationnelle
2. ✅ ETL fonctionnel
3. ✅ Monitoring actif
4. ⏳ Power BI finalisé
5. ⏳ Alertes Slack/Email
6. ⏳ Performance tuning

---

## 📞 Besoin d'aide?

- **Logs**: `./logs/etl_*.log`
- **Status**: `docker ps`
- **Tests**: `python test-elk.py`
- **Dashboards**: `http://localhost:3000` (Metabase)

---

**Status: ✅ Production Ready**

Dernière mise à jour: 17/11/2025
