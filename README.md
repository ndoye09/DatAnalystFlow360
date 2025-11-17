#  Data Lake ETL - Centralisation HDFS

Projet ETL complet pour centraliser vos données MySQL, MongoDB, CSV et Excel dans un Data Lake HDFS.

##  Fonctionnalités

- [OK] Extraction automatique depuis MySQL (toutes les tables)
- [OK] Extraction automatique depuis MongoDB (toutes les collections)
- [OK] Extraction automatique de fichiers CSV
- [OK] Extraction automatique de fichiers Excel (toutes les feuilles)
- [OK] Chargement vers HDFS au format Parquet (optimisé pour le Big Data)
- [OK] Logs détaillés avec codes couleur
- [OK] Gestion des erreurs robuste
- [OK] Architecture conteneurisée avec Docker

## 🏗️ Architecture

```
MySQL Workbench → Extracteur MySQL → 
MongoDB Compass → Extracteur MongoDB → HDFS Data Lake
Fichiers CSV → Extracteur CSV → 
Fichiers Excel → Extracteur Excel →
```

### Structure HDFS
```
/datalake/
|── raw/
│   |── mysql/         # Tables MySQL au format Parquet
│   |── mongodb/       # Collections MongoDB au format Parquet
│   |── csv/           # Fichiers CSV convertis en Parquet
│   └── excel/         # Fichiers Excel convertis en Parquet
└── processed/         # Données transformées (futur)
```

##  Installation et Démarrage

### Prérequis
- Docker et Docker Compose installés
- MySQL Workbench avec votre base de données
- MongoDB Compass avec vos collections
- Fichiers CSV et Excel à migrer

### 1. Structure du projet

```bash
mkdir -p data-lake-etl/{etl/{config,extractors,loaders,transformers,utils},data/{csv,excel},logs}
cd data-lake-etl
```

### 2. Créer les fichiers

Copiez tous les fichiers fournis dans leur emplacement respectif selon l'arborescence.

### 3. Préparer vos données

**Pour MySQL:**
- Votre base MySQL doit être accessible sur `localhost:3307`
- Créditentials: user=`root`, password=`Lebou09@`, database=`data_analyst_db`

**Pour MongoDB:**
- Votre MongoDB doit être accessible sur `localhost:27017`
- Database: `data_analyst_db`

**Pour les fichiers:**
```bash
# Copier vos fichiers CSV
cp /chemin/vers/vos/*.csv ./data/csv/

# Copier vos fichiers Excel
cp /chemin/vers/vos/*.xlsx ./data/excel/
```

### 4. Démarrer l'infrastructure

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f etl-python
```

### 5. Vérifier le chargement

**Via l'interface Web HDFS:**
```
http://localhost:9870
```
Naviguez vers: `Utilities → Browse the file system → /datalake/raw/`

**Via ligne de commande:**
```bash
# Entrer dans le conteneur namenode
docker exec -it datalake-namenode bash

# Lister les données chargées
hdfs dfs -ls /datalake/raw/mysql
hdfs dfs -ls /datalake/raw/mongodb
hdfs dfs -ls /datalake/raw/csv
hdfs dfs -ls /datalake/raw/excel
```

##  Utilisation

### Exécution manuelle

```bash
# Relancer l'ETL manuellement
docker-compose restart etl-python

# Voir les logs en temps réel
docker-compose logs -f etl-python
```

### Personnalisation

**Modifier la configuration:**
Éditez `etl/config/config.py` pour changer:
- Credentials de connexion
- Chemins HDFS
- Format de sortie (Parquet ou CSV)

**Ajouter des transformations:**
Créez vos transformations dans `etl/transformers/data_transformer.py`

##  Commandes utiles

### Gestion Docker

```bash
# Arrêter tous les services
docker-compose down

# Redémarrer un service spécifique
docker-compose restart mysql

# Voir les logs d'un service
docker-compose logs mongodb

# Supprimer tous les volumes (⚠️ perte de données)
docker-compose down -v
```

### Accès aux services

| Service | URL/Port | Credentials |
|---------|----------|-------------|
| MySQL | localhost:3307 | root / Lebou09@ |
| MongoDB | localhost:27017 | (aucun) |
| HDFS Web UI | http://localhost:9870 | (aucun) |
| MinIO Console | http://localhost:9006 | admin / admin12345 |

### Commandes HDFS

```bash
# Accéder au conteneur HDFS
docker exec -it datalake-namenode bash

# Lister les fichiers
hdfs dfs -ls /datalake/raw/mysql

# Voir le contenu d'un fichier
hdfs dfs -cat /datalake/raw/mysql/ma_table.parquet | head

# Télécharger un fichier localement
hdfs dfs -get /datalake/raw/mysql/ma_table.parquet ./

# Supprimer un fichier
hdfs dfs -rm /datalake/raw/mysql/ancienne_table.parquet

# Informations sur l'espace
hdfs dfs -df -h /datalake
```

##  Monitoring

### Logs applicatifs
Les logs sont stockés dans `./logs/etl_YYYYMMDD.log`

```bash
# Voir les logs du jour
tail -f logs/etl_$(date +%Y%m%d).log

# Rechercher les erreurs
grep "ERROR" logs/etl_*.log
```

### Métriques HDFS
Interface Web HDFS: http://localhost:9870
- Espace utilisé
- Nombre de fichiers
- Santé du cluster

## 🐛 Dépannage

### Erreur: "Cannot connect to MySQL"
```bash
# Vérifier que MySQL est accessible
docker-compose ps mysql
docker-compose logs mysql

# Tester la connexion
docker exec -it datalake-mysql mysql -uroot -pLebou09@ -e "SHOW DATABASES;"
```

### Erreur: "HDFS not accessible"
```bash
# Vérifier HDFS
docker-compose ps hadoop-namenode

# Attendre que HDFS soit prêt (peut prendre 2-3 minutes)
curl http://localhost:9870


docker-compose restart hadoop-namenode hadoop-datanode
```

### Erreur: "No files found in /data/csv"
```bash
# Vérifier que vos fichiers sont bien montés
docker exec -it datalake-etl ls -la /data/csv
docker exec -it datalake-etl ls -la /data/excel


docker cp mon_fichier.csv datalake-etl:/data/csv/
```

##  Sécurité

**⚠️ IMPORTANT pour la production:**

1. Changez les mots de passe par défaut dans `docker-compose.yml`
2. Utilisez des variables d'environnement ou Docker secrets
3. Activez l'authentification HDFS
4. Configurez un pare-feu approprié
5. Utilisez HTTPS pour les interfaces Web

## 📚 Ressources

- [Documentation HDFS](https://hadoop.apache.org/docs/stable/)
- [WebHDFS API](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/WebHDFS.html)
- [Format Parquet](https://parquet.apache.org/docs/)
- [Docker Compose](https://docs.docker.com/compose/)

## 🤝 Support

Pour toute question ou problème:
1. Consultez les logs: `docker-compose logs etl-python`
2. Vérifiez la santé des services: `docker-compose ps`
3. Consultez les logs applicatifs dans `./logs/`

## 📝 License

Ce projet est fourni tel quel pour usage éducatif et professionnel.

---

**Développé avec ❤️ pour simplifier vos pipelines ETL**