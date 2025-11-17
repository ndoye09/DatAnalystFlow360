#!/bin/bash
# Script de synchronisation ETL - À exécuter manuellement ou via cron

set -e

echo "=========================================="
echo " SYNCHRONISATION ETL AUTOMATIQUE"
echo "=========================================="
echo "📅 Début : $(date)"

# Aller au répertoire du projet
cd "$(dirname "$0")"

echo ""
echo " Vérification de la structure..."
if [ ! -f "docker-compose.yml" ]; then
  echo "[ERROR] Erreur: docker-compose.yml non trouvé"
  exit 1
fi

echo "[OK] Structure OK"

# ===== DÉMARRER LES SERVICES =====
echo ""
echo "🐳 Démarrage des services Docker..."
docker-compose up -d
docker-compose -f docker-compose-dwh.yml up -d

# ===== ATTENDRE QUE HDFS SOIT PRÊT =====
echo ""
echo "[WAIT] Attente que HDFS soit accessible..."
for i in {1..30}; do
  if docker exec datalake-namenode hdfs dfs -ls / &>/dev/null; then
    echo "[OK] HDFS accessible"
    break
  fi
  echo "[WAIT] Tentative $i/30..."
  sleep 10
  if [ $i -eq 30 ]; then
    echo "[ERROR] HDFS non accessible après 30 tentatives"
    exit 1
  fi
done

# ===== RELANCER L'ETL DATA LAKE =====
echo ""
echo "🔄 Relancement ETL Data Lake..."
docker restart datalake-etl
sleep 40

echo ""
echo " Logs ETL Data Lake :"
docker logs datalake-etl --tail 10

# ===== RELANCER L'ETL DWH =====
echo ""
echo "🔄 Relancement ETL Data Warehouse..."
docker restart etl-dwh
sleep 10

echo ""
echo " Logs ETL DWH :"
docker logs etl-dwh --tail 10

# ===== VÉRIFIER LES DONNÉES =====
echo ""
echo " Vérification des données..."

PATIENTS=$(docker exec datawarehouse psql -U dwh_user -d datawarehouse -t -c "SELECT COUNT(*) FROM staging.stg_patients;" 2>/dev/null | tr -d ' ')
TESTS=$(docker exec datawarehouse psql -U dwh_user -d datawarehouse -t -c "SELECT COUNT(*) FROM staging.stg_medical_tests;" 2>/dev/null | tr -d ' ')
TOTAL=$(docker exec datawarehouse psql -U dwh_user -d datawarehouse -t -c "SELECT SUM(cnt) FROM (SELECT COUNT(*) as cnt FROM staging.stg_patients UNION ALL SELECT COUNT(*) FROM staging.stg_medical_tests UNION ALL SELECT COUNT(*) FROM staging.stg_medications UNION ALL SELECT COUNT(*) FROM staging.stg_appointments) t;" 2>/dev/null | tr -d ' ')

echo "   [OK] Patients : $PATIENTS"
echo "   [OK] Tests Médicaux : $TESTS"
echo "   [OK] Total données : $TOTAL"

# ===== RÉSUMÉ =====
echo ""
echo "=========================================="
echo "[OK] SYNCHRONISATION ETL RÉUSSIE"
echo "=========================================="
echo "📅 Fin : $(date)"
echo ""
echo " Données disponibles sur : http://localhost:3000 (Metabase)"
echo "💾 PostgreSQL : localhost:5432 (dwh_user / dwh_password)"
echo "🗂️  HDFS : http://localhost:9871"
