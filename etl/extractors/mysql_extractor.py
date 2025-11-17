import pandas as pd
import mysql.connector
from mysql.connector import Error
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MySQLExtractor:
    """Extracteur de données depuis MySQL"""
    
    def __init__(self):
        self.config = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DB
        }
        self.connection = None
    
    def connect(self):
        """Établir la connexion à MySQL"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                logger.info(f"[OK] Connexion MySQL établie: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
                return True
        except Error as e:
            logger.error(f"[ERROR] Erreur connexion MySQL: {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Connexion MySQL fermée")
    
    def get_all_tables(self):
        """Récupérer la liste de toutes les tables"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            logger.info(f" Tables trouvées: {tables}")
            return tables
        except Error as e:
            logger.error(f"[ERROR] Erreur récupération tables: {e}")
            return []
    
    def extract_table(self, table_name):
        """Extraire les données d'une table spécifique"""
        try:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, self.connection)
            logger.info(f"[OK] Table '{table_name}' extraite: {len(df)} lignes, {len(df.columns)} colonnes")
            return df
        except Exception as e:
            logger.error(f"[ERROR] Erreur extraction table '{table_name}': {e}")
            return None
    
    def extract_all_tables(self):
        """Extraire toutes les tables de la base de données"""
        if not self.connect():
            return {}
        
        tables = self.get_all_tables()
        extracted_data = {}
        
        for table in tables:
            df = self.extract_table(table)
            if df is not None:
                extracted_data[table] = df
        
        self.disconnect()
        logger.info(f" Total tables MySQL extraites: {len(extracted_data)}")
        return extracted_data
    
    def extract_custom_query(self, query, name="custom_query"):
        """Extraire des données avec une requête personnalisée"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            df = pd.read_sql(query, self.connection)
            logger.info(f"[OK] Requête '{name}' exécutée: {len(df)} lignes")
            return df
        except Exception as e:
            logger.error(f"[ERROR] Erreur requête '{name}': {e}")
            return None