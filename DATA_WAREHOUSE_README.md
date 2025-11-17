# 🏛️ Data Warehouse - Guide Complet

Data Warehouse PostgreSQL pour analyser les données du Data Lake HDFS.

##  Architecture

```
Data Lake (HDFS)
    ↓
ETL Loader (Python)
    ↓
PostgreSQL Data Warehouse
|── staging.*     → Données brutes depuis HDFS
|── dim.*         → Dimensions
|── fact.*        → Faits
|── analytics.*   → Vues analytiques
└── metadata.*    → Métadonnées et lineage
    ↓
Metabase (BI Tool)
```

##  Installation

### Prérequis

Vous devez avoir le Data Lake déjà configuré et fonctionnel avec des données dans HDFS.

### Structure des Fichiers

```bash
.
|── docker-compose-dwh.yml          # Config Docker Warehouse
|── dwh/
│   └── init-scripts/
│       └── 01_init_schema.sql     # Script initialisation
|── dwh-etl/
│   |── Dockerfile
│   |── requirements.txt
│   └── load_dwh.py                # Script ETL
└── DATA_WAREHOUSE_README.md       # Ce fichier
```

### Démarrage

```bash
# 1. S'assurer que le Data Lake est actif
docker-compose ps

# 2. Démarrer le Data Warehouse
docker-compose -f docker-compose-dwh.yml up -d

# 3. Vérifier les logs
docker-compose -f docker-compose-dwh.yml logs -f etl-dwh

# 4. Attendre la fin du chargement (2-5 minutes)
```

## 🗄️ Schéma du Data Warehouse

### Staging Layer

Tables temporaires recevant les données brutes depuis HDFS:

```sql
staging.nom_table_mysql
staging.nom_collection_mongodb
staging.nom_fichier_csv
staging.nom_fichier_excel
```

### Dimensional Model

#### Dimensions (dim.*)

Tables de dimensions pour le modèle en étoile:

```sql
dim.dim_date          -- Dimension temporelle (déjà créée)
dim.dim_customer      -- Vos dimensions métier
dim.dim_product
dim.dim_location
```

#### Facts (fact.*)

Tables de faits pour les mesures:

```sql
fact.fact_sales       -- Vos faits métier
fact.fact_orders
```

### Analytics Layer (analytics.*)

Vues précalculées pour l'analyse:

```sql
analytics.v_data_summary        -- Résumé des chargements
analytics.v_sales_by_month      -- Vos vues analytiques
analytics.v_customer_analysis
```

### Metadata Layer (metadata.*)

Traçabilité et gouvernance:

```sql
metadata.etl_load_log      -- Historique des chargements
metadata.data_lineage      -- Lignage des données
metadata.quality_checks    -- Vérifications qualité
```

##  Utilisation

### Se Connecter au DWH

```bash
# Via Docker
docker exec -it datawarehouse psql -U dwh_user -d datawarehouse

# Via client PostgreSQL externe
psql -h localhost -p 5432 -U dwh_user -d datawarehouse
# Password: dwh_password
```

### Requêtes Utiles

#### Voir les tables chargées

```sql
-- Tables staging
SELECT table_schema, table_name, 
       pg_size_pretty(pg_total_relation_size(table_schema||'.'||table_name)) as size
FROM information_schema.tables
WHERE table_schema = 'staging'
ORDER BY table_name;
```

#### Vérifier les derniers chargements

```sql
SELECT * FROM metadata.v_recent_loads
LIMIT 10;
```

#### Statistiques par source

```sql
SELECT 
    source_system,
    COUNT(*) as nombre_tables,
    SUM(rows_loaded) as total_lignes,
    MAX(load_end_time) as dernier_chargement
FROM metadata.etl_load_log
WHERE load_status = 'SUCCESS'
GROUP BY source_system;
```

#### Explorer les données staging

```sql
-- Exemple avec une table MySQL
SELECT * FROM staging.nom_de_votre_table LIMIT 10;

-- Voir le nombre de lignes
SELECT COUNT(*) FROM staging.nom_de_votre_table;

-- Voir la structure
\d staging.nom_de_votre_table
```



#### Exemple: Dimension Client

```sql
CREATE TABLE dim.dim_customer AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY customer_id) as customer_key,
    customer_id,
    customer_name,
    customer_email,
    customer_segment,
    CURRENT_TIMESTAMP as created_at
FROM staging.customers;

-- Ajouter clé primaire
ALTER TABLE dim.dim_customer ADD PRIMARY KEY (customer_key);

-- Index sur l'ID naturel
CREATE INDEX idx_customer_id ON dim.dim_customer(customer_id);
```



```sql
CREATE TABLE fact.fact_sales AS
SELECT 
    s.sale_id,
    c.customer_key,
    d.date_key,
    s.amount,
    s.quantity,
    s.discount,
    CURRENT_TIMESTAMP as created_at
FROM staging.sales s
LEFT JOIN dim.dim_customer c ON s.customer_id = c.customer_id
LEFT JOIN dim.dim_date d ON s.sale_date = d.full_date;

-- Ajouter clés étrangères
ALTER TABLE fact.fact_sales 
ADD CONSTRAINT fk_customer FOREIGN KEY (customer_key) REFERENCES dim.dim_customer(customer_key);

ALTER TABLE fact.fact_sales 
ADD CONSTRAINT fk_date FOREIGN KEY (date_key) REFERENCES dim.dim_date(date_key);
```

#### Créer une Vue Analytique

```sql
CREATE VIEW analytics.v_monthly_sales AS
SELECT 
    d.year,
    d.month_name,
    c.customer_segment,
    COUNT(*) as nombre_ventes,
    SUM(f.amount) as chiffre_affaires,
    AVG(f.amount) as panier_moyen
FROM fact.fact_sales f
JOIN dim.dim_date d ON f.date_key = d.date_key
JOIN dim.dim_customer c ON f.customer_key = c.customer_key
GROUP BY d.year, d.month, d.month_name, c.customer_segment
ORDER BY d.year, d.month;
```

##  Accès Metabase

Metabase est un outil de BI libre pour créer des dashboards.

### Accéder à Metabase

```
URL: http://localhost:3000
```

### Configuration Initiale

1. **Première connexion**: Créer un compte admin
2. **Ajouter la base de données**:
   - Type: PostgreSQL
   - Nom: Data Warehouse
   - Host: postgres-dwh
   - Port: 5432
   - Database: datawarehouse
   - Username: dwh_user
   - Password: dwh_password

3. **Explorer les données**:
   - Parcourir les schémas: staging, dim, fact, analytics
   - Créer des questions SQL
   - Construire des dashboards

### Exemples de Questions Metabase

**Question 1: Volume de données par source**
```sql
SELECT 
    source_system as "Source",
    SUM(rows_loaded) as "Nombre de lignes"
FROM metadata.etl_load_log
WHERE load_status = 'SUCCESS'
GROUP BY source_system
ORDER BY SUM(rows_loaded) DESC
```

**Question 2: Évolution des chargements**
```sql
SELECT 
    DATE(load_start_time) as "Date",
    COUNT(*) as "Nombre de chargements",
    SUM(rows_loaded) as "Lignes chargées"
FROM metadata.etl_load_log
WHERE load_status = 'SUCCESS'
GROUP BY DATE(load_start_time)
ORDER BY DATE(load_start_time) DESC
```

## 🔄 Rechargement des Données

### Recharger depuis HDFS

```bash
# Relancer l'ETL
docker-compose -f docker-compose-dwh.yml restart etl-dwh

# Voir les logs
docker-compose -f docker-compose-dwh.yml logs -f etl-dwh
```

### Nettoyer et Recharger

```sql
-- Vider les tables staging
TRUNCATE staging.nom_table CASCADE;

-- Puis relancer l'ETL
```



### Backup du DWH

```bash
# Backup complet
docker exec datawarehouse pg_dump -U dwh_user datawarehouse > dwh_backup_$(date +%Y%m%d).sql

# Backup d'un schéma spécifique
docker exec datawarehouse pg_dump -U dwh_user -n staging datawarehouse > staging_backup.sql
```

### Restore

```bash
# Restore
docker exec -i datawarehouse psql -U dwh_user datawarehouse < dwh_backup.sql
```

### Optimisation

```sql
-- Analyser les tables pour optimiser les requêtes
ANALYZE;

-- Vacuum pour récupérer l'espace
VACUUM ANALYZE;

-- Reindex si nécessaire
REINDEX DATABASE datawarehouse;
```

### Monitoring

```sql
-- Taille de la base
SELECT pg_size_pretty(pg_database_size('datawarehouse'));

-- Taille des schémas
SELECT 
    schemaname,
    pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))::bigint) as size
FROM pg_tables
WHERE schemaname IN ('staging', 'dim', 'fact', 'analytics')
GROUP BY schemaname;

-- Tables les plus volumineuses
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname IN ('staging', 'dim', 'fact', 'analytics')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Requêtes lentes
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## 🐛 Dépannage

### Le DWH ne démarre pas

```bash
# Vérifier les logs
docker-compose -f docker-compose-dwh.yml logs postgres-dwh


docker-compose -f docker-compose-dwh.yml down
docker volume rm <project>_postgres_dwh_data
docker-compose -f docker-compose-dwh.yml up -d
```

### L'ETL ne charge pas les données

```bash
# Vérifier que HDFS est accessible
docker exec etl-datawarehouse curl http://hadoop-namenode:9870

# Vérifier les fichiers HDFS
docker exec datalake-namenode hdfs dfs -ls /datalake/raw/mysql


docker-compose -f docker-compose-dwh.yml logs etl-dwh
```

### Metabase ne se connecte pas

- Vérifier que vous utilisez `postgres-dwh` comme hostname (pas `localhost`)
- Vérifier les credentials
- Attendre 2-3 minutes après le démarrage

## 📚 Ressources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Metabase Documentation](https://www.metabase.com/docs/)
- [Data Warehouse Design](https://en.wikipedia.org/wiki/Data_warehouse)
- [Star Schema](https://en.wikipedia.org/wiki/Star_schema)



1. **Modéliser vos données métier** (dimensions et faits)
2. **Créer des vues analytiques** pour vos besoins
3. **Construire des dashboards** dans Metabase
4. **Automatiser** les rechargements (cron, Airflow)
5. **Optimiser** les performances (index, partitionnement)

---

** Votre Data Warehouse est opérationnel !**