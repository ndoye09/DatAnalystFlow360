import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MongoDBExtractor:
    """Extracteur de données depuis MongoDB"""
    
    def __init__(self):
        self.uri = Config.MONGO_URI
        self.db_name = Config.MONGO_DB
        self.client = None
        self.db = None
    
    def connect(self):
        """Établir la connexion à MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test de connexion
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            logger.info(f"✅ Connexion MongoDB établie: {self.uri}")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ Erreur connexion MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion"""
        if self.client:
            self.client.close()
            logger.info("Connexion MongoDB fermée")
    
    def get_all_collections(self):
        """Récupérer la liste de toutes les collections"""
        try:
            collections = self.db.list_collection_names()
            logger.info(f"📋 Collections trouvées: {collections}")
            return collections
        except Exception as e:
            logger.error(f"❌ Erreur récupération collections: {e}")
            return []
    
    def extract_collection(self, collection_name, query=None, projection=None):
        """Extraire les données d'une collection spécifique"""
        try:
            collection = self.db[collection_name]
            
            # Query par défaut
            if query is None:
                query = {}
            
            # Récupération des documents
            cursor = collection.find(query, projection)
            documents = list(cursor)
            
            if not documents:
                logger.warning(f"⚠️  Collection '{collection_name}' est vide")
                return pd.DataFrame()
            
            # Conversion en DataFrame
            df = pd.DataFrame(documents)
            
            # Conversion de l'ObjectId en string si présent
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)
            
            logger.info(f"✅ Collection '{collection_name}' extraite: {len(df)} documents, {len(df.columns)} champs")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction collection '{collection_name}': {e}")
            return None
    
    def extract_all_collections(self):
        """Extraire toutes les collections de la base de données"""
        if not self.connect():
            return {}
        
        collections = self.get_all_collections()
        extracted_data = {}
        
        for collection in collections:
            df = self.extract_collection(collection)
            if df is not None:
                extracted_data[collection] = df
        
        self.disconnect()
        logger.info(f"📊 Total collections MongoDB extraites: {len(extracted_data)}")
        return extracted_data
    
    def extract_with_aggregation(self, collection_name, pipeline, result_name="aggregation"):
        """Extraire des données avec une pipeline d'agrégation"""
        try:
            if not self.client:
                self.connect()
            
            collection = self.db[collection_name]
            results = list(collection.aggregate(pipeline))
            
            if not results:
                logger.warning(f"⚠️  Agrégation '{result_name}' n'a retourné aucun résultat")
                return pd.DataFrame()
            
            df = pd.DataFrame(results)
            
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)
            
            logger.info(f"✅ Agrégation '{result_name}' exécutée: {len(df)} résultats")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur agrégation '{result_name}': {e}")
            return None