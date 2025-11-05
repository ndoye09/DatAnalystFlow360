import pandas as pd
import os
import glob
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FileExtractor:
    """Extracteur de données depuis fichiers CSV et Excel"""
    
    def __init__(self):
        self.csv_path = Config.LOCAL_CSV_PATH
        self.excel_path = Config.LOCAL_EXCEL_PATH
    
    def extract_csv_files(self):
        """Extraire tous les fichiers CSV"""
        extracted_data = {}
        
        # Vérifier si le répertoire existe
        if not os.path.exists(self.csv_path):
            logger.warning(f"⚠️  Répertoire CSV n'existe pas: {self.csv_path}")
            return extracted_data
        
        # Trouver tous les fichiers CSV
        csv_files = glob.glob(os.path.join(self.csv_path, '*.csv'))
        
        if not csv_files:
            logger.warning(f"⚠️  Aucun fichier CSV trouvé dans {self.csv_path}")
            return extracted_data
        
        logger.info(f"📂 {len(csv_files)} fichiers CSV trouvés")
        
        for csv_file in csv_files:
            try:
                # Nom du fichier sans extension
                file_name = os.path.splitext(os.path.basename(csv_file))[0]
                
                # Lire le CSV avec différents encodages possibles
                try:
                    df = pd.read_csv(csv_file, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(csv_file, encoding='latin-1')
                    except UnicodeDecodeError:
                        df = pd.read_csv(csv_file, encoding='cp1252')
                
                extracted_data[file_name] = df
                logger.info(f"✅ CSV '{file_name}' extrait: {len(df)} lignes, {len(df.columns)} colonnes")
                
            except Exception as e:
                logger.error(f"❌ Erreur lecture CSV '{csv_file}': {e}")
        
        logger.info(f"📊 Total fichiers CSV extraits: {len(extracted_data)}")
        return extracted_data
    
    def extract_excel_files(self):
        """Extraire tous les fichiers Excel"""
        extracted_data = {}
        
        # Vérifier si le répertoire existe
        if not os.path.exists(self.excel_path):
            logger.warning(f"⚠️  Répertoire Excel n'existe pas: {self.excel_path}")
            return extracted_data
        
        # Trouver tous les fichiers Excel
        excel_files = glob.glob(os.path.join(self.excel_path, '*.xlsx'))
        excel_files += glob.glob(os.path.join(self.excel_path, '*.xls'))
        
        if not excel_files:
            logger.warning(f"⚠️  Aucun fichier Excel trouvé dans {self.excel_path}")
            return extracted_data
        
        logger.info(f"📂 {len(excel_files)} fichiers Excel trouvés")
        
        for excel_file in excel_files:
            try:
                # Nom du fichier sans extension
                file_name = os.path.splitext(os.path.basename(excel_file))[0]
                
                # Lire toutes les feuilles du fichier Excel
                excel_data = pd.read_excel(excel_file, sheet_name=None)
                
                # Si une seule feuille, utiliser directement le nom du fichier
                if len(excel_data) == 1:
                    sheet_name = list(excel_data.keys())[0]
                    df = excel_data[sheet_name]
                    extracted_data[file_name] = df
                    logger.info(f"✅ Excel '{file_name}' extrait: {len(df)} lignes, {len(df.columns)} colonnes")
                else:
                    # Plusieurs feuilles, créer une clé par feuille
                    for sheet_name, df in excel_data.items():
                        key = f"{file_name}_{sheet_name}"
                        extracted_data[key] = df
                        logger.info(f"✅ Excel '{key}' extrait: {len(df)} lignes, {len(df.columns)} colonnes")
                
            except Exception as e:
                logger.error(f"❌ Erreur lecture Excel '{excel_file}': {e}")
        
        logger.info(f"📊 Total fichiers Excel extraits: {len(extracted_data)}")
        return extracted_data
    
    def extract_all_files(self):
        """Extraire tous les fichiers CSV et Excel"""
        logger.info("🔍 Début extraction des fichiers locaux...")
        
        all_data = {}
        
        # Extraire CSV
        csv_data = self.extract_csv_files()
        all_data.update(csv_data)
        
        # Extraire Excel
        excel_data = self.extract_excel_files()
        all_data.update(excel_data)
        
        logger.info(f"📊 Total fichiers extraits: {len(all_data)}")
        return all_data
    
    def extract_specific_file(self, file_path):
        """Extraire un fichier spécifique (CSV ou Excel)"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                logger.error(f"❌ Type de fichier non supporté: {file_ext}")
                return None
            
            logger.info(f"✅ Fichier '{file_path}' extrait: {len(df)} lignes")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction fichier '{file_path}': {e}")
            return None