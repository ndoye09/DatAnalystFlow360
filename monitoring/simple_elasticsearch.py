"""
Solution ELK alternative sans Docker
Utilise des services locaux Python pour Elasticsearch-like storage
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging


class SimpleElasticsearch:
    """Simulateur simple d'Elasticsearch utilisant SQLite"""

    def __init__(self, db_path: str = "elk_logs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialiser la base de données"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                logger TEXT,
                message TEXT,
                module TEXT,
                function TEXT,
                line INTEGER,
                tags TEXT,
                exception TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_name TEXT,
                value REAL,
                source TEXT,
                table_name TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def index_log(self, doc: Dict) -> bool:
        """Indexer un document log"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''
                INSERT INTO logs
                (timestamp, level, logger, message, module, function, line, tags, exception)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc.get('timestamp'),
                doc.get('level'),
                doc.get('logger'),
                doc.get('message'),
                doc.get('module'),
                doc.get('function'),
                doc.get('line'),
                json.dumps(doc.get('tags', [])),
                doc.get('exception', '')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Erreur indexation: {e}")
            return False

    def index_metric(self, doc: Dict) -> bool:
        """Indexer une métrique"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''
                INSERT INTO metrics
                (timestamp, metric_name, value, source, table_name, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                doc.get('timestamp'),
                doc.get('metric_name'),
                doc.get('value'),
                doc.get('source'),
                doc.get('table_name'),
                json.dumps(doc.get('tags', []))
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Erreur indexation métrique: {e}")
            return False

    def search_logs(
        self,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Rechercher les logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "SELECT * FROM logs"
            params = []

            if level:
                query += " WHERE level = ?"
                params.append(level)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            c.execute(query, params)
            rows = c.fetchall()

            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'level': row['level'],
                    'logger': row['logger'],
                    'message': row['message'],
                    'module': row['module'],
                    'function': row['function'],
                    'line': row['line'],
                    'tags': json.loads(row['tags'])
                })

            conn.close()
            return results

        except Exception as e:
            logging.error(f"Erreur recherche: {e}")
            return []

    def search_metrics(
        self,
        metric_name: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Rechercher les métriques"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "SELECT * FROM metrics WHERE 1=1"
            params = []

            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)

            if source:
                query += " AND source = ?"
                params.append(source)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            c.execute(query, params)
            rows = c.fetchall()

            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'metric_name': row['metric_name'],
                    'value': row['value'],
                    'source': row['source'],
                    'table_name': row['table_name'],
                    'tags': json.loads(row['tags'])
                })

            conn.close()
            return results

        except Exception as e:
            logging.error(f"Erreur recherche métriques: {e}")
            return []

    def get_stats(self) -> Dict:
        """Obtenir les statistiques"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM logs")
            total_logs = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM logs WHERE level = 'ERROR'")
            error_logs = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM logs WHERE level = 'WARNING'")
            warning_logs = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM metrics")
            total_metrics = c.fetchone()[0]

            conn.close()

            return {
                'total_logs': total_logs,
                'errors': error_logs,
                'warnings': warning_logs,
                'total_metrics': total_metrics,
                'db_size': Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            }

        except Exception as e:
            logging.error(f"Erreur stats: {e}")
            return {}


# Exemple d'utilisation
if __name__ == "__main__":
    es = SimpleElasticsearch()

    # Indexer des logs
    es.index_log({
        'timestamp': datetime.now().isoformat(),
        'level': 'INFO',
        'logger': 'etl-monitor',
        'message': 'Démarrage du monitoring',
        'module': 'monitoring',
        'function': 'main',
        'line': 42,
        'tags': ['etl', 'python']
    })

    # Indexer une métrique
    es.index_metric({
        'timestamp': datetime.now().isoformat(),
        'metric_name': 'data_completeness',
        'value': 99.5,
        'source': 'mysql',
        'table_name': 'patients',
        'tags': ['quality-check']
    })

    # Rechercher
    logs = es.search_logs(limit=5)
    print(f"Logs trouvés: {len(logs)}")

    metrics = es.search_metrics()
    print(f"Métriques trouvées: {len(metrics)}")

    stats = es.get_stats()
    print(f"Stats: {stats}")
