#!/usr/bin/env python3
"""
Module de vérification de la qualité des données
Vérifie l'intégrité, la complétude et la validité des données
"""

import sys
import logging
from datetime import datetime
import pandas as pd
import json
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Vérificateur de qualité des données"""
    
    def __init__(self, hdfs_path='/datalake/raw'):
        self.hdfs_path = hdfs_path
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {}
        }
    
    def check_completeness(self, df, table_name):
        """Vérifier la complétude des données"""
        logger.info(f"✓ Vérification de la complétude : {table_name}")
        
        total_rows = len(df)
        missing_values = df.isnull().sum().to_dict()
        completion_rate = (1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))) * 100
        
        result = {
            'table': table_name,
            'total_rows': total_rows,
            'missing_values': missing_values,
            'completion_rate': f"{completion_rate:.2f}%",
            'status': 'PASS' if completion_rate > 95 else 'WARNING'
        }
        
        logger.info(f"  📊 Taux de complétude : {completion_rate:.2f}%")
        return result
    
    def check_duplicates(self, df, table_name):
        """Vérifier les doublons"""
        logger.info(f"✓ Vérification des doublons : {table_name}")
        
        total_duplicates = df.duplicated().sum()
        duplicate_rate = (total_duplicates / len(df) * 100) if len(df) > 0 else 0
        
        result = {
            'table': table_name,
            'total_duplicates': int(total_duplicates),
            'duplicate_rate': f"{duplicate_rate:.2f}%",
            'status': 'PASS' if duplicate_rate < 1 else 'WARNING'
        }
        
        logger.info(f"  🔍 Taux de doublons : {duplicate_rate:.2f}%")
        return result
    
    def check_data_types(self, df, table_name):
        """Vérifier les types de données"""
        logger.info(f"✓ Vérification des types de données : {table_name}")
        
        data_types = df.dtypes.to_dict()
        data_types_str = {col: str(dtype) for col, dtype in data_types.items()}
        
        result = {
            'table': table_name,
            'columns': len(df.columns),
            'data_types': data_types_str,
            'status': 'PASS'
        }
        
        logger.info(f"  📋 Colonnes : {len(df.columns)}")
        return result
    
    def check_numeric_ranges(self, df, table_name, numeric_columns=None):
        """Vérifier les plages numériques"""
        logger.info(f"✓ Vérification des plages numériques : {table_name}")
        
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        ranges = {}
        for col in numeric_columns:
            if col in df.columns:
                ranges[col] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std())
                }
        
        result = {
            'table': table_name,
            'numeric_columns': numeric_columns,
            'ranges': ranges,
            'status': 'PASS'
        }
        
        logger.info(f"  📈 Colonnes numériques analysées : {len(numeric_columns)}")
        return result
    
    def generate_report(self):
        """Générer un rapport de qualité"""
        logger.info("\n" + "="*60)
        logger.info("📊 RAPPORT DE QUALITÉ DES DONNÉES")
        logger.info("="*60)
        
        report = {
            'timestamp': self.results['timestamp'],
            'total_checks': len(self.results['checks']),
            'passed_checks': sum(1 for check in self.results['checks'].values() 
                                if check.get('status') == 'PASS'),
            'warning_checks': sum(1 for check in self.results['checks'].values() 
                                 if check.get('status') == 'WARNING'),
            'details': self.results['checks']
        }
        
        logger.info(f"✓ Vérifications réussies : {report['passed_checks']}/{report['total_checks']}")
        logger.info(f"⚠️  Avertissements : {report['warning_checks']}")
        logger.info("="*60 + "\n")
        
        return report


class DataMonitor:
    """Moniteur de performance des données"""
    
    def __init__(self):
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'etl_runs': [],
            'data_volumes': {},
            'processing_times': {}
        }
    
    def log_etl_run(self, status, duration, records_processed):
        """Enregistrer une exécution ETL"""
        run_info = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'duration_seconds': duration,
            'records_processed': records_processed
        }
        
        self.metrics['etl_runs'].append(run_info)
        logger.info(f"📝 ETL Run: {status} | Duration: {duration}s | Records: {records_processed}")
    
    def log_data_volume(self, source, table_name, row_count, size_mb):
        """Enregistrer le volume de données"""
        if source not in self.metrics['data_volumes']:
            self.metrics['data_volumes'][source] = {}
        
        self.metrics['data_volumes'][source][table_name] = {
            'rows': row_count,
            'size_mb': size_mb,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"📊 Data Volume: {source}.{table_name} | Rows: {row_count} | Size: {size_mb}MB")
    
    def generate_monitoring_report(self):
        """Générer un rapport de monitoring"""
        logger.info("\n" + "="*60)
        logger.info("🔍 RAPPORT DE MONITORING")
        logger.info("="*60)
        
        if self.metrics['etl_runs']:
            last_run = self.metrics['etl_runs'][-1]
            logger.info(f"✓ Dernier run ETL: {last_run['status']}")
            logger.info(f"  Duration: {last_run['duration_seconds']}s")
            logger.info(f"  Records: {last_run['records_processed']}")
        
        total_volume_mb = sum(
            sum(table.get('size_mb', 0) for table in tables.values())
            for tables in self.metrics['data_volumes'].values()
        )
        
        logger.info(f"💾 Volume total: {total_volume_mb:.2f}MB")
        logger.info("="*60 + "\n")
        
        return self.metrics


def run_quality_checks(data_dict):
    """Exécuter tous les contrôles de qualité"""
    logger.info("\n🚀 Démarrage des vérifications de qualité...")
    
    checker = DataQualityChecker()
    
    for source, tables in data_dict.items():
        logger.info(f"\n📂 Vérification de {source}...")
        
        for table_name, df in tables.items():
            if isinstance(df, pd.DataFrame) and len(df) > 0:
                check_key = f"{source}_{table_name}"
                
                # Exécuter les vérifications
                checks = {
                    'completeness': checker.check_completeness(df, table_name),
                    'duplicates': checker.check_duplicates(df, table_name),
                    'data_types': checker.check_data_types(df, table_name),
                }
                
                # Vérifier les plages numériques si applicable
                if source in ['mysql', 'mongodb']:
                    checks['numeric_ranges'] = checker.check_numeric_ranges(df, table_name)
                
                checker.results['checks'][check_key] = checks
    
    return checker.generate_report()


def save_quality_report(report, output_path='monitoring/quality_report.json'):
    """Sauvegarder le rapport de qualité"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"✅ Rapport sauvegardé : {output_path}")


if __name__ == '__main__':
    # Exemple d'utilisation
    logger.info("Module de vérification de qualité des données")
    logger.info("À utiliser depuis etl/main.py")
