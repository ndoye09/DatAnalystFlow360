#!/usr/bin/env python3
"""
Script principal ETL - Data Lake HDFS
Centralise les données de MySQL, MongoDB, CSV et Excel vers HDFS
"""

import time
import sys
from datetime import datetime
from config.config import Config
from extractors.mysql_extractor import MySQLExtractor
from extractors.mongodb_extractor import MongoDBExtractor
from extractors.file_extractor import FileExtractor
from loaders.hdfs_loader import HDFSLoader
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataLakeETL:
    """Orchestrateur principal du processus ETL"""
    
    def __init__(self):
        self.mysql_extractor = MySQLExtractor()
        self.mongodb_extractor = MongoDBExtractor()
        self.file_extractor = FileExtractor()
        self.hdfs_loader = HDFSLoader()
        
        self.stats = {
            'start_time': None,
            'end_time': None,
            'mysql': {'extracted': 0, 'loaded': 0},
            'mongodb': {'extracted': 0, 'loaded': 0},
            'csv': {'extracted': 0, 'loaded': 0},
            'excel': {'extracted': 0, 'loaded': 0},
            'errors': []
        }
    
    def print_banner(self):
        """Afficher la bannière de démarrage"""
        banner = """
        ╔-------------------------------------------------------╗
        |           DATA LAKE ETL - HDFS INGESTION           |
        |                                                       |
        |  MySQL → HDFS  |  MongoDB → HDFS                    |
        |  CSV → HDFS    |  Excel → HDFS                      |
        ╚-------------------------------------------------------╝
        """
        print(banner)
        logger.info("Démarrage du processus ETL Data Lake")
    
    def check_prerequisites(self):
        """Vérifier les prérequis avant de lancer l'ETL"""
        logger.info(" Vérification des prérequis...")
        
        # Vérifier la connexion HDFS
        if not self.hdfs_loader.check_hdfs_connection():
            logger.error("[ERROR] HDFS non accessible. Arrêt du processus.")
            return False
        
        # Initialiser la structure HDFS
        if not self.hdfs_loader.initialize_directories():
            logger.warning("⚠️  Problème lors de l'initialisation des répertoires HDFS")
        
        logger.info("[OK] Prérequis validés")
        return True
    
    def extract_mysql_data(self):
        """Extraire les données MySQL"""
        logger.info("\n" + "="*60)
        logger.info(" PHASE 1: Extraction MySQL")
        logger.info("="*60)
        
        try:
            mysql_data = self.mysql_extractor.extract_all_tables()
            self.stats['mysql']['extracted'] = len(mysql_data)
            
            if not mysql_data:
                logger.warning("⚠️  Aucune donnée MySQL extraite")
            
            return mysql_data
        except Exception as e:
            error_msg = f"Erreur extraction MySQL: {e}"
            logger.error(f"[ERROR] {error_msg}")
            self.stats['errors'].append(error_msg)
            return {}
    
    def extract_mongodb_data(self):
        """Extraire les données MongoDB"""
        logger.info("\n" + "="*60)
        logger.info("🍃 PHASE 2: Extraction MongoDB")
        logger.info("="*60)
        
        try:
            mongodb_data = self.mongodb_extractor.extract_all_collections()
            self.stats['mongodb']['extracted'] = len(mongodb_data)
            
            if not mongodb_data:
                logger.warning("⚠️  Aucune donnée MongoDB extraite")
            
            return mongodb_data
        except Exception as e:
            error_msg = f"Erreur extraction MongoDB: {e}"
            logger.error(f"[ERROR] {error_msg}")
            self.stats['errors'].append(error_msg)
            return {}
    
    def extract_file_data(self):
        """Extraire les données des fichiers CSV et Excel"""
        logger.info("\n" + "="*60)
        logger.info("📁 PHASE 3: Extraction Fichiers (CSV & Excel)")
        logger.info("="*60)
        
        try:
            
            csv_data = self.file_extractor.extract_csv_files()
            self.stats['csv']['extracted'] = len(csv_data)
            
            
            excel_data = self.file_extractor.extract_excel_files()
            self.stats['excel']['extracted'] = len(excel_data)
            
            return csv_data, excel_data
        except Exception as e:
            error_msg = f"Erreur extraction fichiers: {e}"
            logger.error(f"[ERROR] {error_msg}")
            self.stats['errors'].append(error_msg)
            return {}, {}
    
    def load_to_hdfs(self, mysql_data, mongodb_data, csv_data, excel_data):
        """Charger toutes les données vers HDFS"""
        logger.info("\n" + "="*60)
        logger.info("💾 PHASE 4: Chargement vers HDFS")
        logger.info("="*60)
        
        # Charger MySQL
        if mysql_data:
            if self.hdfs_loader.load_mysql_data(mysql_data):
                self.stats['mysql']['loaded'] = len(mysql_data)
        
        # Charger MongoDB
        if mongodb_data:
            if self.hdfs_loader.load_mongodb_data(mongodb_data):
                self.stats['mongodb']['loaded'] = len(mongodb_data)
        
        # Charger CSV
        if csv_data:
            if self.hdfs_loader.load_csv_data(csv_data):
                self.stats['csv']['loaded'] = len(csv_data)
        
        # Charger Excel
        if excel_data:
            if self.hdfs_loader.load_excel_data(excel_data):
                self.stats['excel']['loaded'] = len(excel_data)
    
    def print_summary(self):
        """Afficher le résumé du processus ETL"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        summary = f"""
        ╔-------------------------------------------------------╗
        |                   RÉSUMÉ ETL                       |
        ╠-------------------------------------------------------╣
        | Durée totale: {duration:.2f} secondes                     
        ╠-------------------------------------------------------╣
        | MySQL:                                                |
        |   - Extraits: {self.stats['mysql']['extracted']:>3} tables                        |
        |   - Chargés:  {self.stats['mysql']['loaded']:>3} tables                        |
        |                                                       |
        | MongoDB:                                              |
        |   - Extraits: {self.stats['mongodb']['extracted']:>3} collections                  |
        |   - Chargés:  {self.stats['mongodb']['loaded']:>3} collections                  |
        |                                                       |
        | CSV:                                                  |
        |   - Extraits: {self.stats['csv']['extracted']:>3} fichiers                      |
        |   - Chargés:  {self.stats['csv']['loaded']:>3} fichiers                      |
        |                                                       |
        | Excel:                                                |
        |   - Extraits: {self.stats['excel']['extracted']:>3} fichiers                      |
        |   - Chargés:  {self.stats['excel']['loaded']:>3} fichiers                      |
        ╠-------------------------------------------------------╣
        | Total datasets: {self.stats['mysql']['loaded'] + self.stats['mongodb']['loaded'] + self.stats['csv']['loaded'] + self.stats['excel']['loaded']:>3}                               |
        """
        
        if self.stats['errors']:
            summary += f"| Erreurs: {len(self.stats['errors']):>3}                                    |\n"
        
        summary += "╚-------------------------------------------------------╝"
        
        print(summary)
        logger.info("Processus ETL terminé")
    
    def run(self):
        """Exécuter le processus ETL complet"""
        try:
            self.stats['start_time'] = datetime.now()
            
            # Bannière
            self.print_banner()
            
            # Vérification des prérequis
            if not self.check_prerequisites():
                return False
            
            # Phase 1: Extraction MySQL
            mysql_data = self.extract_mysql_data()
            
            # Phase 2: Extraction MongoDB
            mongodb_data = self.extract_mongodb_data()
            
            # Phase 3: Extraction Fichiers
            csv_data, excel_data = self.extract_file_data()
            
            # Phase 4: Chargement vers HDFS
            self.load_to_hdfs(mysql_data, mongodb_data, csv_data, excel_data)
            
            # Fin du processus
            self.stats['end_time'] = datetime.now()
            
            # Résumé
            self.print_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Erreur critique dans le processus ETL: {e}")
            self.stats['errors'].append(str(e))
            return False

def main():
    """Point d'entrée principal"""
    etl = DataLakeETL()
    
    try:
        success = etl.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Processus interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[ERROR] Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()