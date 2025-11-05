import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import os
from io import BytesIO
from datetime import datetime
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class HDFSLoader:
    """Chargeur de données vers HDFS via WebHDFS"""
    
    def __init__(self):
        self.namenode = Config.HDFS_NAMENODE
        self.port = 9870  # Port WebHDFS
        self.user = Config.HDFS_USER
        self.base_url = f"http://{self.namenode}:{self.port}/webhdfs/v1"
        self.hdfs_paths = Config.get_hdfs_paths()
    
    def _make_request(self, path, operation, method='PUT', data=None, params=None):
        """Faire une requête WebHDFS"""
        try:
            url = f"{self.base_url}{path}"
            
            # Paramètres par défaut
            default_params = {
                'op': operation,
                'user.name': self.user
            }
            
            if params:
                default_params.update(params)
            
            # Première requête pour obtenir l'URL de redirection
            response = requests.request(
                method,
                url,
                params=default_params,
                allow_redirects=False,
                timeout=30
            )
            
            # Si c'est une redirection (307), suivre la redirection
            if response.status_code == 307:
                redirect_url = response.headers['Location']
                response = requests.request(
                    method,
                    redirect_url,
                    data=data,
                    timeout=300
                )
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur requête WebHDFS: {e}")
            return None
    
    def create_directory(self, path):
        """Créer un répertoire dans HDFS"""
        try:
            response = self._make_request(path, 'MKDIRS', method='PUT')
            
            if response and response.status_code == 200:
                result = response.json()
                if result.get('boolean'):
                    logger.info(f"✅ Répertoire créé: {path}")
                    return True
                else:
                    logger.warning(f"⚠️  Répertoire existe déjà: {path}")
                    return True
            else:
                logger.error(f"❌ Erreur création répertoire {path}: {response.status_code if response else 'No response'}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur création répertoire {path}: {e}")
            return False
    
    def initialize_directories(self):
        """Initialiser la structure de répertoires du Data Lake"""
        logger.info("📁 Initialisation de la structure HDFS...")
        
        directories = [
            Config.HDFS_BASE_PATH,
            Config.HDFS_RAW_PATH,
            Config.HDFS_PROCESSED_PATH,
            self.hdfs_paths['mysql'],
            self.hdfs_paths['mongodb'],
            self.hdfs_paths['csv'],
            self.hdfs_paths['excel']
        ]
        
        success = True
        for directory in directories:
            if not self.create_directory(directory):
                success = False
        
        if success:
            logger.info("✅ Structure HDFS initialisée avec succès")
        else:
            logger.warning("⚠️  Certains répertoires n'ont pas pu être créés")
        
        return success
    
    def upload_dataframe(self, df, hdfs_path, file_name, format='parquet'):
        """Uploader un DataFrame vers HDFS"""
        try:
            # Créer le chemin complet
            full_path = f"{hdfs_path}/{file_name}.{format}"
            
            # Convertir le DataFrame selon le format
            if format == 'parquet':
                buffer = BytesIO()
                table = pa.Table.from_pandas(df)
                pq.write_table(table, buffer)
                data = buffer.getvalue()
            elif format == 'csv':
                data = df.to_csv(index=False).encode('utf-8')
            else:
                logger.error(f"❌ Format non supporté: {format}")
                return False
            
            # Upload vers HDFS
            response = self._make_request(
                full_path,
                'CREATE',
                method='PUT',
                data=data,
                params={'overwrite': 'true'}
            )
            
            if response and response.status_code in [200, 201]:
                size_mb = len(data) / (1024 * 1024)
                logger.info(f"✅ Fichier uploadé: {full_path} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error(f"❌ Erreur upload {full_path}: {response.status_code if response else 'No response'}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur upload DataFrame vers {hdfs_path}/{file_name}: {e}")
            return False
    
    def load_mysql_data(self, data_dict):
        """Charger les données MySQL vers HDFS"""
        logger.info("📤 Chargement données MySQL vers HDFS...")
        
        success_count = 0
        for table_name, df in data_dict.items():
            if self.upload_dataframe(df, self.hdfs_paths['mysql'], table_name):
                success_count += 1
        
        logger.info(f"✅ MySQL: {success_count}/{len(data_dict)} tables chargées")
        return success_count == len(data_dict)
    
    def load_mongodb_data(self, data_dict):
        """Charger les données MongoDB vers HDFS"""
        logger.info("📤 Chargement données MongoDB vers HDFS...")
        
        success_count = 0
        for collection_name, df in data_dict.items():
            if self.upload_dataframe(df, self.hdfs_paths['mongodb'], collection_name):
                success_count += 1
        
        logger.info(f"✅ MongoDB: {success_count}/{len(data_dict)} collections chargées")
        return success_count == len(data_dict)
    
    def load_csv_data(self, data_dict):
        """Charger les fichiers CSV vers HDFS"""
        logger.info("📤 Chargement fichiers CSV vers HDFS...")
        
        success_count = 0
        for file_name, df in data_dict.items():
            if self.upload_dataframe(df, self.hdfs_paths['csv'], file_name):
                success_count += 1
        
        logger.info(f"✅ CSV: {success_count}/{len(data_dict)} fichiers chargés")
        return success_count == len(data_dict)
    
    def load_excel_data(self, data_dict):
        """Charger les fichiers Excel vers HDFS"""
        logger.info("📤 Chargement fichiers Excel vers HDFS...")
        
        success_count = 0
        for file_name, df in data_dict.items():
            if self.upload_dataframe(df, self.hdfs_paths['excel'], file_name):
                success_count += 1
        
        logger.info(f"✅ Excel: {success_count}/{len(data_dict)} fichiers chargés")
        return success_count == len(data_dict)
    
    def check_hdfs_connection(self):
        """Vérifier la connexion HDFS"""
        try:
            response = self._make_request('/', 'LISTSTATUS', method='GET')
            if response and response.status_code == 200:
                logger.info("✅ Connexion HDFS établie")
                return True
            else:
                logger.error("❌ Impossible de se connecter à HDFS")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur connexion HDFS: {e}")
            return False
    
    def generate_metadata(self, source_type, data_dict):
        """Générer un fichier de métadonnées"""
        metadata = {
            'source': source_type,
            'timestamp': datetime.now().isoformat(),
            'datasets': {}
        }
        
        for name, df in data_dict.items():
            metadata['datasets'][name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
        
        return pd.DataFrame([metadata])