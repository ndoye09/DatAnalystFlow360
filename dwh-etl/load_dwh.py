import os
import pandas as pd
import sqlalchemy
import logging
import requests
from io import BytesIO
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - INFO - %(message)s')
logger = logging.getLogger(__name__)

class DWHLoader:
    """Charge les données Parquet depuis HDFS vers PostgreSQL via WebHDFS"""
    
    def __init__(self):
        self.hdfs_namenode = os.getenv('HDFS_NAMENODE', 'hadoop-namenode')
        self.hdfs_port = int(os.getenv('HDFS_PORT', 9870))
        self.webhdfs_url = f"http://{self.hdfs_namenode}:{self.hdfs_port}/webhdfs/v1"
        self.hdfs_raw_path = "/datalake/raw"
        
        self.postgres_host = os.getenv('POSTGRES_HOST', 'postgres-dwh')
        self.postgres_user = os.getenv('POSTGRES_USER', 'dwh_user')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD', 'dwh_password')
        self.postgres_db = os.getenv('POSTGRES_DB', 'datawarehouse')
        
        # Connexion PostgreSQL
        self.engine = sqlalchemy.create_engine(
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:5432/{self.postgres_db}"
        )
        logger.info("[OK] Connexion PostgreSQL établie")
    
    def create_schemas(self):
        """Créer les schémas nécessaires"""
        try:
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS staging;"))
                conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS dim;"))
                conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS fact;"))
                conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS analytics;"))
                conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS metadata;"))
                conn.commit()
            logger.info("[OK] Schémas créés avec succès")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Erreur création schémas: {e}")
            return False
    
    def list_hdfs_files(self, path=""):
        """Liste les fichiers dans HDFS via WebHDFS"""
        try:
            target_path = f"{self.hdfs_raw_path}{path}" if path else self.hdfs_raw_path
            url = f"{self.webhdfs_url}{target_path}"
            
            response = requests.get(url, params={'op': 'LISTSTATUS', 'user.name': 'root'}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                files = []
                
                for item in data.get('FileStatuses', {}).get('FileStatus', []):
                    item_path = item['pathSuffix']
                    is_file = item['type'] == 'FILE'
                    is_dir = item['type'] == 'DIRECTORY'
                    
                    if is_file and item_path.endswith('.parquet'):
                        full_path = f"{target_path}/{item_path}".replace('//', '/')
                        files.append(full_path)
                    elif is_dir:
                        # Récursivement chercher dans les sous-répertoires
                        sub_files = self.list_hdfs_files(f"{path}/{item_path}")
                        files.extend(sub_files)
                
                return files
            else:
                logger.warning(f"⚠️  Impossible de lister HDFS (code {response.status_code})")
                return []
        except Exception as e:
            logger.warning(f"⚠️  Erreur WebHDFS: {e}")
            return []
    
    def download_parquet_from_hdfs(self, hdfs_path):
        """Télécharge un fichier Parquet depuis HDFS via WebHDFS"""
        try:
            url = f"{self.webhdfs_url}{hdfs_path}"
            
            # Première requête pour obtenir l'URL de redirection
            response = requests.get(url, params={'op': 'OPEN', 'user.name': 'root'}, 
                                  allow_redirects=False, timeout=30)
            
            if response.status_code == 307:
                # Suivre la redirection
                redirect_url = response.headers['Location']
                response = requests.get(redirect_url, timeout=300)
                
                if response.status_code == 200:
                    return BytesIO(response.content)
                else:
                    logger.warning(f"⚠️  Erreur redirection HTTP {response.status_code}")
                    return None
            else:
                logger.warning(f"⚠️  Erreur HTTP {response.status_code} pour {hdfs_path}")
                return None
        except Exception as e:
            logger.warning(f"⚠️  Erreur téléchargement {hdfs_path}: {e}")
            return None
    
    def load_parquet_to_postgres(self, parquet_buffer, table_name):
        """Charge un fichier Parquet dans PostgreSQL"""
        try:
            # Lire le fichier Parquet depuis le buffer
            df = pd.read_parquet(parquet_buffer)
            
            # Nettoyer le nom de la table
            safe_table_name = "stg_" + table_name.lower().replace('.parquet', '').replace('-', '_')
            
            # Charger dans PostgreSQL
            df.to_sql(safe_table_name, self.engine, schema="staging", 
                     if_exists="replace", index=False)
            
            logger.info(f"[OK] Chargé {len(df):,} lignes → staging.{safe_table_name}")
            return len(df)
        except Exception as e:
            logger.error(f"[ERROR] Erreur chargement {table_name}: {e}")
            return 0
    
    def run(self):
        """Exécute le chargement complet"""
        logger.info("="*60)
        logger.info(" DÉMARRAGE ETL: HDFS → DATA WAREHOUSE")
        logger.info(f"   WebHDFS: {self.webhdfs_url}")
        logger.info("="*60)
        
        # Créer les schémas
        if not self.create_schemas():
            return False
        
        # Attendre que HDFS soit accessible
        max_retries = 5
        for attempt in range(max_retries):
            try:
                requests.get(f"{self.webhdfs_url}/", params={'op': 'LISTSTATUS'}, timeout=5)
                logger.info("[OK] WebHDFS accessible")
                break
            except:
                if attempt < max_retries - 1:
                    logger.info(f"[WAIT] Attente HDFS ({attempt+1}/{max_retries})...")
                    time.sleep(3)
                else:
                    logger.error("[ERROR] HDFS non accessible après 5 tentatives")
                    return False
        
        # Récupérer les fichiers Parquet
        logger.info(f"📂 Recherche fichiers Parquet dans {self.hdfs_raw_path}...")
        parquet_files = self.list_hdfs_files()
        
        if not parquet_files:
            logger.warning("⚠️  Aucun fichier Parquet trouvé dans HDFS")
            logger.info("[INFO] Assurez-vous que l'ETL Data Lake a chargé les données")
            return False
        
        logger.info(f"📂 {len(parquet_files)} fichiers Parquet trouvés")
        
        # Charger chaque fichier
        total_rows = 0
        success_count = 0
        
        for hdfs_file in parquet_files:
            parquet_buffer = self.download_parquet_from_hdfs(hdfs_file)
            if parquet_buffer:
                rows = self.load_parquet_to_postgres(parquet_buffer, os.path.basename(hdfs_file))
                total_rows += rows
                if rows > 0:
                    success_count += 1
        
        # Résumé final
        logger.info("="*60)
        logger.info(f"[OK] CHARGEMENT TERMINÉ")
        logger.info(f"   - Fichiers chargés: {success_count}/{len(parquet_files)}")
        logger.info(f"   - Total lignes: {total_rows:,}")
        logger.info(f"   - Schéma: staging")
        logger.info("="*60)
        
        return success_count > 0

if __name__ == "__main__":
    loader = DWHLoader()
    success = loader.run()
    exit(0 if success else 1)