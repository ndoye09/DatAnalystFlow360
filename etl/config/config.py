import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration centrale pour le projet ETL Data Lake"""
    
    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Lebou09@')
    MYSQL_DB = os.getenv('MYSQL_DB', 'data_analyst_db')
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'data_analyst_db')
    
    # HDFS Configuration
    HDFS_NAMENODE = os.getenv('HDFS_NAMENODE', 'hadoop-namenode')
    HDFS_PORT = int(os.getenv('HDFS_PORT', 9000))
    HDFS_USER = os.getenv('HDFS_USER', 'root')
    HDFS_URL = f'hdfs://{HDFS_NAMENODE}:{HDFS_PORT}'
    
    # MinIO Configuration
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9005')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'admin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'admin12345')
    
    # Chemins Data Lake HDFS
    HDFS_BASE_PATH = '/datalake'
    HDFS_RAW_PATH = f'{HDFS_BASE_PATH}/raw'
    HDFS_PROCESSED_PATH = f'{HDFS_BASE_PATH}/processed'
    
    # Chemins sources locales
    LOCAL_CSV_PATH = '/data/csv'
    LOCAL_EXCEL_PATH = '/data/excel'
    
    # Logging
    LOG_PATH = '/logs'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_mysql_connection_string(cls):
        return f"mysql+mysqlconnector://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DB}"
    
    @classmethod
    def get_hdfs_paths(cls):
        return {
            'mysql': f'{cls.HDFS_RAW_PATH}/mysql',
            'mongodb': f'{cls.HDFS_RAW_PATH}/mongodb',
            'csv': f'{cls.HDFS_RAW_PATH}/csv',
            'excel': f'{cls.HDFS_RAW_PATH}/excel',
            'processed': cls.HDFS_PROCESSED_PATH
        }