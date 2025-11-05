import logging
import colorlog
from datetime import datetime
from config.config import Config
import os

def setup_logger(name):
    """Configure un logger avec couleurs et fichier"""
    
    # Créer le répertoire de logs s'il n'existe pas
    os.makedirs(Config.LOG_PATH, exist_ok=True)
    
    # Configuration du logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Format des logs
    log_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s'
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Handler console avec couleurs
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    # Handler fichier
    log_file = os.path.join(Config.LOG_PATH, f'etl_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S'))
    
    # Ajout des handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger